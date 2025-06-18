from flask import Flask, render_template, jsonify
from fetch_data import get_all_data

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("map.html")

@app.route("/data")
def data():
    try:
        raw_data = get_all_data()
        
        # Debugging: Print raw response
        print("Raw fetched data:", raw_data)

        # Extract 'threats' if the response is a dictionary
        threats = raw_data.get("threats", []) if isinstance(raw_data, dict) else []

        # Ensure it's a valid list
        if not isinstance(threats, list):
            print("⚠️ Warning: Extracted threats are not a list!")
            return jsonify([])

        return jsonify(threats)

    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return jsonify([])

if __name__ == "__main__":
    app.run(debug=True)
