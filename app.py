from unittest import result
from flask import Flask
from models.database import Database
from config import Config

app = Flask(__name__)

db = Database(Config.DATABASE_URL)
conn = db.connect()

@app.route("/database")
def database_route():
    return conn

@app.route("/query")
def query_route():
    result = db.execute_query("SELECT * FROM teste")
    return result

if __name__ == "__main__":
    app.run(debug=True)