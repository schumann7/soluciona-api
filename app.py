from flask import Flask
from models.database import Database
from config import Config

app = Flask(__name__)

db = Database(Config.DATABASE_URL)
db.connect()

@app.route("/connect")
def connect_database():
    return db.connect()

@app.route("/database")
def check_database_status():
    return db.status()

@app.route("/close")
def close_database():
    db.close()
    return db.status()

if __name__ == "__main__":
    app.run(debug=True)