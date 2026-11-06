from pathlib import Path
from flask import Flask, request, jsonify
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
FILE_PATH = BASE_DIR / "data" / "leaked_summary.csv"

app = Flask(__name__)

@app.route('/hello')
def index():
    return "Hello, welcome to the weakest link API!"


@app.route('/api/data', methods=['GET'])
def get_data():
    try:
        df = pd.read_csv(FILE_PATH)

        data_dict = df.to_dict(orient='records')
        message = "This API references summarized data. It is the same data illustrated on the password checker."
        return f"<p>{message}</p><pre>{df.to_json(orient='records', indent=2)}</pre>", 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)