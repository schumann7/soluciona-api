from controllers.db_instance import db
from flask import request, jsonify

class PlacesController:
    def return_all_places(self):
        return db.execute("SELECT * FROM places")

    def add_place(self):
        data = request.get_json()
        name = data.get('name')
        type = data.get('type')
        
        db.execute(
            "INSERT INTO places (name, type) VALUES (%s, %s)",
            (name, type)
        )
        return jsonify({"message": "Place added successfully"}), 201