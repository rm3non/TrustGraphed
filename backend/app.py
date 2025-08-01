from flask import Flask, jsonify
from flask_cors import CORS
from routes.evaluate import evaluate_bp

app = Flask(__name__)
CORS(app)

# Register blueprints
app.register_blueprint(evaluate_bp)

@app.route("/health")
def health_check():
    return jsonify({"status": "TrustGraphed backend is live"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
