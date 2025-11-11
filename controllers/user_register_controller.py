from controllers.db_instance import db
from flask import request, jsonify
from models.user_model import password_to_hash
from flask_jwt_extended import get_jwt_identity

class UserRegisterController:
    def register(self):
        data = request.get_json(silent=True) or {}
        required = ["username", "email", "password"]
        for field in required:
            if not data.get(field):
                return jsonify({"error": f"Campo '{field}' é obrigatório."}), 400

        email = data["email"].strip().lower()
        password = data["password"]
        username = data.get("username")
        phone = data.get("phone")
        place_id = data.get("place_id")
        profile_picture = data.get("profile_picture")

        try:
            existing = db.execute("SELECT id FROM users WHERE email = %s", (email,))
        except Exception as e:
            return jsonify({"error": "Error at checking existing user.", "detail": str(e)}), 500

        if isinstance(existing, dict) and existing.get("error"):
            return jsonify({"error": "Error at accessing database.", "detail": existing["error"]}), 500

        if existing and len(existing) > 0:
            return jsonify({"error": "E-mail already exists."}), 409

        hashed = password_to_hash(password)
        try:
            result = db.execute(
                "INSERT INTO users (email, password, username, phone, place_id, profile_picture) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (email, hashed, username, phone, place_id, profile_picture),
            )
        except Exception as e:
            return jsonify({"error": "Error creating user.", "detail": str(e)}), 500

        if isinstance(result, dict) and result.get("error"):
            return jsonify({"error": "Error creating user.", "detail": result["error"]}), 500

        try:
            new_id = result[0][0] if result and len(result) > 0 else None
        except Exception:
            new_id = None

        user_info = {"id": new_id, "email": email, "phone": phone}
        return jsonify({"message": "User registered successfully.", "user": user_info}), 201

    def get_user_profile(self):
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
            user_row = db.execute(
                "SELECT id, username, email, phone, profile_picture, place_id, account_status, created_at "
                "FROM users WHERE id = %s",
                (user_id,)
            )
        except Exception as e:
            return jsonify({"error": "Error fetching user.", "detail": str(e)}), 500

        if isinstance(user_row, dict) and user_row.get("error"):
            return jsonify({"error": "Error fetching user.", "detail": user_row["error"]}), 500

        if not user_row or len(user_row) == 0:
            return jsonify({"error": "User not found."}), 404

        u = user_row[0]
        profile_picture_id = u[4]

        image_url = ""
        if profile_picture_id:
            try:
                img_row = db.execute(
                    "SELECT url_storage FROM images WHERE id = %s",
                    (profile_picture_id,)
                )
            except Exception:
                img_row = []

            if isinstance(img_row, dict) and img_row.get("error"):
                img_row = []

            if img_row and len(img_row) > 0:
                image_url = img_row[0][0] if len(img_row[0]) > 0 else ""

        user_dict = {
            "id": u[0],
            "username": u[1],
            "email": u[2],
            "phone": u[3],
            "profile_picture": image_url,  # string url or "" if not available
            "place_id": u[5],
            "account_status": u[6],
            "created_at": u[7]
        }

        return jsonify({"user": user_dict}), 200
