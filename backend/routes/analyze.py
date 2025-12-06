from flask import Blueprint, request, jsonify
from infrastructure.code_analyzer import analyze_code
import traceback

analyze_bp = Blueprint('analyze', __name__)

@analyze_bp.route('/analyze', methods=['POST'])
def analyze():
    try:
        data =request.get_json()
        
        if not data or 'code' not in data:
            return jsonify ({'error' : 'No code provided'}), 400
        
        code = data['code']
        language = data.get('language', 'python')

        if not code.strip():
            return jsonify({'error': 'Code cannot be empty'}), 400
        
        results = analyze_code(code, language)
        return jsonify(results), 200
        
    except Exception as e:
        print(f"ERROR: {str(e)}")  # ADD THIS LINE
        traceback.print_exc()      # ADD THIS LINE
        return jsonify({'error': str(e)}), 500