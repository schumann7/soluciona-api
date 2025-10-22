from flask import Flask
from controllers.db_instance import db
from controllers.user_register_controller import UserRegisterController

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
    
if __name__ == "__main__":
    app.run(debug=True)