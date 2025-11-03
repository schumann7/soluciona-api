from controllers.db_instance import db
from flask import request, jsonify

class ReportsController:
    def report_problem(self):
        data = request.get_json(silent=True) or {}
        required = ["name", "latitude", "longitude", "description", "place"]
        for field in required:
            if not data.get(field):
                return jsonify({"error": f"Campo '{field}' é obrigatório."}), 400

        name = data["name"]
        latitude = data["latitude"]
        longitude = data["longitude"]
        description = data["description"]
        place = data["place"]
        registered_by = data["registered_by"]

        try:
            result = db.execute(
                "INSERT INTO reports (name, latitude, longitude, description, place, registered_by) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (name, latitude, longitude, description, place, registered_by),
            )
        except Exception as e:
            return jsonify({"error": "Erro ao registrar o problema.", "detail": str(e)}), 500

        if isinstance(result, dict) and result.get("error"):
            return jsonify({"error": "Erro ao registrar o problema.", "detail": result["error"]}), 500

        try:
            new_id = result[0][0] if result and len(result) > 0 else None
        except Exception:
            new_id = None

        report_info = {"id": new_id, "name": name, "latitude": latitude, "longitude": longitude, "description": description, "place": place, "registered_by": registered_by}
        return jsonify({"message": "Problema registrado com sucesso.", "report": report_info}), 201
    
    def list_reports_by_place(self, place):
        try:
            reports = db.execute(
                "SELECT * FROM reports WHERE place = %s",
                (place,)
            )
        except Exception as e:
            return jsonify({"error": "Erro ao listar os relatórios.", "detail": str(e)}), 500

        if isinstance(reports, dict) and reports.get("error"):
            return jsonify({"error": "Erro ao listar os relatórios.", "detail": reports["error"]}), 500

        reports_list = []
        for report in reports:
            report_dict = {
                "id": report[0],
                "name": report[1],
                "latitude": report[2],
                "longitude": report[3],
                "description": report[4],
                "place": report[5],
                "registered_by": report[6],
                "registered_date": report[7]
            }
            reports_list.append(report_dict)

        return jsonify(reports_list), 200
    
    def remove_report(self, report_id):
        try:
            result = db.execute(
                "DELETE FROM reports WHERE id = %s RETURNING id",
                (report_id,)
            )
        except Exception as e:
            return jsonify({"error": "Erro ao remover o relatório.", "detail": str(e)}), 500

        if isinstance(result, dict) and result.get("error"):
            return jsonify({"error": "Erro ao remover o relatório.", "detail": result["error"]}), 500

        if not result:
            return jsonify({"error": "Relatório não encontrado."}), 404

        return jsonify({"message": "Relatório removido com sucesso.", "report_id": report_id}), 200