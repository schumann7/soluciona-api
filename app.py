from flask import Flask
from config import Config
from controllers.db_instance import db
from controllers.user_register_controller import UserRegisterController
from controllers.auth import AuthController
from controllers.reports_controller import ReportsController
from controllers.images_controller import ImageController
from flask_jwt_extended import JWTManager, jwt_required
from controllers.places_controller import PlacesController

app = Flask(__name__)
app.config.from_object(Config)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
jwt = JWTManager(app)

@app.route("/register", methods=["POST"])
def register_user():
    controller = UserRegisterController()
    return controller.register()

@app.route("/login", methods=["POST"])
def login():
    controller = AuthController()
    return controller.login()

@app.route("/reports", methods=["POST"])
@jwt_required()
def register_reports():
    controller = ReportsController()
    return controller.report_problem()

@app.route("/reports/<place>", methods=["GET"])
@jwt_required()
def list_reports_by_place(place):
    controller = ReportsController()
    return controller.list_reports_by_place(place)

@app.route("/reports/<int:report_id>", methods=["DELETE"])
@jwt_required()
def remove_report(report_id):
    controller = ReportsController()
    return controller.remove_report(report_id)

@app.route("/reports/<int:report_id>/upload-image", methods=["POST"])
@jwt_required()
def upload_report_image(report_id):
    controller = ImageController()
    return controller.upload_image(report_id)

@app.route("/upload-image", methods=["POST"])
@jwt_required()
def upload_image():
    controller = ImageController()
    return controller.upload_image()

@app.route("/places", methods=["GET"])
def list_places():
    controller = PlacesController()
    return controller.return_all_places()

@app.route("/places", methods=["POST"])
@jwt_required()
def add_place():
    controller = PlacesController()
    return controller.add_place()
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)