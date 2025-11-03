from flask import Flask
from controllers.db_instance import db
from controllers.user_register_controller import UserRegisterController
from controllers.reports_controller import ReportsController
from flask_jwt_extended import jwt_required

app = Flask(__name__)

@app.route("/status")
def check_database_status():
    return db.status()

@app.route("/register", methods=["POST"])
def register_user():
    controller = UserRegisterController()
    return controller.register()

@app.route("/users", methods=["GET"])
def list_users():
    return db.execute("select * from users")

@app.route("/reports", methods=["POST"])
@jwt_required()
def register_reports():
    controller = ReportsController()
    return controller.report_problem()

@app.route("/reports", methods=["GET"])
def list_reports():
    return db.execute("select * from reports")

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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)