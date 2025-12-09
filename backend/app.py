from flask import Flask, jsonify
from flask_cors import CORS
from routes.analyze import analyze_bp

app = Flask(__name__)
CORS(app)

@app.route('/')
def health_check():
    return jsonify({'status': 'running', 'message': 'Code Analyzer API'})

app.register_blueprint(analyze_bp)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5002))
    app.run(host='0.0.0.0', debug=False, port=port)