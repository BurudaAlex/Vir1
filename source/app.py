from dotenv import load_dotenv
import os

# Загрузка переменных окружения из файла .env
load_dotenv()
from flask import Flask, request, jsonify
from Yama.source.database_setup import PassesDB

db = PassesDB(
    host=os.getenv("FSTR_DB_HOST"),
    database=os.getenv("FSTR_DB_DATABASE"),
    user=os.getenv("FSTR_DB_USER"),
    password=os.getenv("FSTR_DB_PASSWORD")
)
app = Flask(__name__)
db = PassesDB(
    host="127.0.0.1", # Нужно внести данные
    database="", # Нужно внести данные
    user="",     # Нужно внести данные
    password=""  # Нужно внести данные
)

@app.route('/submitData', methods=['POST'])
def submit_data():
    data = request.json
    result = db.submit_data(data)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)