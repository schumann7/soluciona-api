from controllers.db_instance import db
from flask import request, jsonify
from models.user_model import password_to_hash
import json

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
            return jsonify({"error": "E-mail já cadastrado."}), 409

        hashed = password_to_hash(password)
        try:
            result = db.execute(
                "INSERT INTO users (email, password, username, phone, place_id, profile_picture) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (email, hashed, username, phone, place_id, profile_picture),
            )
        except Exception as e:
            return jsonify({"error": "Erro ao criar usuário.", "detail": str(e)}), 500

        if isinstance(result, dict) and result.get("error"):
            return jsonify({"error": "Erro ao criar usuário.", "detail": result["error"]}), 500

        try:
            new_id = result[0][0] if result and len(result) > 0 else None
        except Exception:
            new_id = None

        user_info = {"id": new_id, "email": email, "phone": phone}
        return jsonify({"message": "Usuário registrado com sucesso.", "user": user_info}), 201
