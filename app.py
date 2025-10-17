from flask import Flask
from models.database_model import DatabaseModel as PostgresConnection

app = Flask(__name__)

connection = PostgresConnection()

if __name__ == "__main__":
    app.run(debug=True)