from controllers.db_instance import db
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

class ReportsController:
    def report_problem(self):
        data = request.get_json(silent=True) or {}
        required = ["name", "latitude", "longitude", "description", "place_id"]
        for field in required:
            if not data.get(field):
                return jsonify({"error": f"Campo '{field}' é obrigatório."}), 400

        name = data["name"]
        latitude = data["latitude"]
        longitude = data["longitude"]
        description = data["description"]
        place_id = data["place_id"]
        address = data.get("address")
        registered_by = None
        try:
            identity = get_jwt_identity()
            if identity:
                if isinstance(identity, dict):
                    registered_by = int(identity.get("id")) if identity.get("id") else None
                else:
                    registered_by = int(identity)
        except Exception:
            registered_by = data.get("registered_by")

        try:
            result = db.execute(
                "INSERT INTO reports (name, latitude, longitude, description, place_id, address, registered_by, registered_date) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, NOW()) RETURNING id",
                (name, latitude, longitude, description, place_id, address, registered_by),
            )
        except Exception as e:
            return jsonify({"error": "Error registering report.", "detail": str(e)}), 500

        if isinstance(result, dict) and result.get("error"):
            return jsonify({"error": "Error registering report.", "detail": result["error"]}), 500

        try:
            new_id = result[0][0] if result and len(result) > 0 else None
        except Exception:
            new_id = None

        report_info = {"id": new_id, "name": name, "latitude": latitude, "longitude": longitude,
                       "description": description, "place_id": place_id, "registered_by": registered_by}
        return jsonify({"message": "Report registered successfully.", "report": report_info}), 201

    def list_reports_by_user_place(self):
        try:
            identity = get_jwt_identity()
            if isinstance(identity, dict):
                user_id = int(identity.get("id")) if identity.get("id") else None
            else:
                user_id = int(identity) if identity else None
        except Exception:
            user_id = None

        if not user_id:
            return jsonify({"error": "User not authenticated."}), 401

        try:
            user_row = db.execute("SELECT place_id FROM users WHERE id = %s", (user_id,))
        except Exception as e:
            return jsonify({"error": "Error fetching user.", "detail": str(e)}), 500

        if not user_row:
            return jsonify({"error": "User not found."}), 404

        place_id = user_row[0][0]
        if not place_id:
            return jsonify({"error": "User has no associated place."}), 404

        try:
            place_row = db.execute("SELECT id, name FROM places WHERE id = %s", (place_id,))
        except Exception as e:
            return jsonify({"error": "Error fetching user's place.", "detail": str(e)}), 500

        place_name = place_row[0][1] if place_row and len(place_row) > 0 else None

        # search reports linked to place_id with status = active
        try:
            reports = db.execute(
                "SELECT id, latitude, longitude "
                "FROM reports WHERE place_id = %s AND status = %s",
                (place_id, "active")
            )
        except Exception as e:
            return jsonify({"error": "Error listing reports.", "detail": str(e)}), 500

        if isinstance(reports, dict) and reports.get("error"):
            return jsonify({"error": "Error listing reports.", "detail": reports["error"]}), 500

        reports_list = []
        for report in reports:
            report_dict = {
                "id": report[0],
                "latitude": report[1],
                "longitude": report[2]
            }
            reports_list.append(report_dict)

        return jsonify({
            "place": {"id": place_id, "name": place_name},
            "reports": reports_list
        }), 200

    def get_report_full_details(self, report_id):
        # search report by id
        try:
            report = db.execute(
                "SELECT id, name, latitude, longitude, description, place_id, address, status, registered_by, registered_date "
                "FROM reports WHERE id = %s",
                (report_id,)
            )
        except Exception as e:
            return jsonify({"error": "Error fetching report.", "detail": str(e)}), 500

        if isinstance(report, dict) and report.get("error"):
            return jsonify({"error": "Error fetching report.", "detail": report["error"]}), 500

        if not report or len(report) == 0:
            return jsonify({"error": "Report not found."}), 404

        r = report[0]
        report_dict = {
            "id": r[0],
            "name": r[1],
            "latitude": r[2],
            "longitude": r[3],
            "description": r[4],
            "place_id": r[5],
            "address": r[6],
            "status": r[7],
            "registered_by": r[8],
            "registered_date": r[9]
        }

        # search associated images
        try:
            images = db.execute(
                "SELECT url_storage FROM images WHERE report_id = %s ORDER BY id",
                (report_id,)
            )
            if not images:
                images = []
        except Exception:
            # in case of error, just return empty images list
            images = []

        images_list = []
        if images and not (isinstance(images, dict) and images.get("error")):
            for img in images:
                # img can be a tuple/row; the first column is the url_storage
                url = img[0] if img and len(img) > 0 else None
                if url:
                    images_list.append(url)

        report_dict["images"] = images_list
        return jsonify(report_dict), 200
    
    def remove_report(self, report_id):
        try:
            identity = get_jwt_identity()
            if isinstance(identity, dict):
                user_id = int(identity.get("id")) if identity.get("id") else None
            else:
                user_id = int(identity) if identity else None
        except Exception:
            user_id = None

        if not user_id:
            return jsonify({"error": "User not authenticated."}), 401

        try:
            row = db.execute("SELECT registered_by FROM reports WHERE id = %s", (report_id,))
        except Exception as e:
            return jsonify({"error": "Error fetching report.", "detail": str(e)}), 500

        if not row or len(row) == 0:
            return jsonify({"error": "Report not found."}), 404

        report_owner = row[0][0]
        try:
            report_owner_int = int(report_owner) if report_owner is not None else None
        except Exception:
            report_owner_int = None

        if report_owner_int != user_id:
            return jsonify({"error": "Permission denied. Only the creator can remove the report."}), 403

        # delete report
        try:
            result = db.execute(
                "DELETE FROM reports WHERE id = %s RETURNING id",
                (report_id,)
            )
        except Exception as e:
            return jsonify({"error": "Error removing report.", "detail": str(e)}), 500

        if isinstance(result, dict) and result.get("error"):
            return jsonify({"error": "Error removing report.", "detail": result["error"]}), 500

        if not result:
            return jsonify({"error": "Report not found."}), 404

        return jsonify({"message": "Report removed successfully.", "report_id": report_id}), 200

    def list_reports_by_user(self):
        try:
            identity = get_jwt_identity()
            if isinstance(identity, dict):
                user_id = int(identity.get("id")) if identity.get("id") else None
            else:
                user_id = int(identity) if identity else None
        except Exception:
            user_id = None

        if not user_id:
            return jsonify({"error": "User not authenticated."}), 401

        try:
            reports = db.execute(
                "SELECT id, name, latitude, longitude, description, place_id, status, registered_date "
                "FROM reports WHERE registered_by = %s ORDER BY registered_date DESC",
                (user_id,)
            )
            if not reports:
                reports = []
        except Exception as e:
            return jsonify({"error": "Error listing user reports.", "detail": str(e)}), 500

        if isinstance(reports, dict) and reports.get("error"):
            return jsonify({"error": "Error listing user reports.", "detail": reports["error"]}), 500

        reports_list = []
        for r in (reports or []):
            reports_list.append({
                "id": r[0],
                "name": r[1],
                "latitude": r[2],
                "longitude": r[3],
                "description": r[4],
                "place_id": r[5],
                "status": r[6],
                "registered_date": r[7]
            })

        return jsonify({"user_id": user_id, "reports": reports_list}), 200