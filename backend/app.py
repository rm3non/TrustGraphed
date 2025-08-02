
from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
from routes.evaluate import evaluate_bp
import os

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')
CORS(app)

# Register blueprints
app.register_blueprint(evaluate_bp)

@app.route("/")
def index():
    """Serve the main frontend page"""
    return render_template('index.html')

@app.route("/health")
def health_check():
    return jsonify({"status": "TrustGraphed backend is live"})

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    return send_from_directory('../static', filename)

# Debug logging for development
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
