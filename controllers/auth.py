from flask_jwt_extended import create_access_token
from flask import request, jsonify
from controllers.db_instance import db
from models.user_model import password_to_hash

class AuthController:
    def login(self):
        data = request.get_json(silent=True) or {}
        identifier = (
            data.get("identifier")
            or data.get("username")
            or data.get("email")
            or data.get("phone")
        )
        password = data.get("password")

        if not identifier or not password:
            return jsonify({
                "error": "Identifier (username/email/phone) and password are required."
            }), 400

        try:
            user = db.execute(
                "SELECT id, username, password, place_id FROM users "
                "WHERE username = %s OR LOWER(email) = LOWER(%s) OR phone = %s LIMIT 1",
                (identifier, identifier, identifier)
            )
        except Exception as e:
            return jsonify({
                "error": "Error accessing the database.",
                "detail": str(e)
            }), 500

        if not user or len(user) == 0:
            return jsonify({"error": "Invalid credentials."}), 401

        user_id, db_username, db_password, place_id = user[0]

        # Verify password
        if password_to_hash(password) != db_password:
            return jsonify({"error": "Invalid credentials."}), 401

        # Create jwt token for user
        access_token = create_access_token(identity=str(user_id))

        # Return the access token and user information
        return jsonify({
            "access_token": access_token,
            "username": db_username,
            "place_id": place_id
        }), 200
