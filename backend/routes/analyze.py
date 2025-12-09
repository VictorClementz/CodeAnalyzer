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
        print(f"ERROR: {str(e)}")  
        traceback.print_exc()     
        return jsonify({'error': str(e)}), 500
    

# api/routes.py

@analyze_bp.route('/analyze-batch', methods=['POST'])
def analyze_batch():
    files = request.files.getlist('files')
    
    if not files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    results = []
    language = request.form.get('language', 'python')
    
    for file in files:
        filename = file.filename
        
        # Filter by language
        if language == 'python' and not filename.endswith('.py'):
            continue
        elif language == 'javascript' and not filename.endswith('.js'):
            continue
        
        try:
            code = file.read().decode('utf-8')
            analysis = analyze_code(code, language)
            results.append({
                'filename': filename,
                'metrics': analysis
            })
        except Exception as e:
            results.append({
                'filename': filename,
                'error': str(e)
            })
    
    if not results:
        return jsonify({'error': 'No valid files found'}), 400
    
    # Calculate aggregate metrics for ALL fields
    valid_results = [r for r in results if 'metrics' in r]
    
    def safe_avg(key):
        """Calculate average, handling None/missing values"""
        values = [r['metrics'][key] for r in valid_results if r['metrics'].get(key) is not None]
        return round(sum(values) / len(values), 2) if values else 0
    
    project_summary = {
        'total_files': len(valid_results),
        
        # Core metrics
        'avg_readability': safe_avg('readability_score'),
        'avg_complexity': safe_avg('cyclomatic_complexity'),
        'avg_maintainability': safe_avg('maintainability_index'),
        'total_lines': sum(r['metrics']['lines_of_code'] for r in valid_results),
        
        # Additional metrics
        'avg_comment_density': safe_avg('comment_density'),
        'avg_function_length': safe_avg('avg_function_length'),
        'avg_duplication': safe_avg('duplication_percentage'),
        'avg_name_length': safe_avg('avg_name_length'),
        'avg_nesting_depth': safe_avg('avg_nesting_depth'),
        'max_nesting_depth': max((r['metrics']['max_nesting_depth'] for r in valid_results if r['metrics'].get('max_nesting_depth')), default=0),
        'avg_cognitive_complexity': safe_avg('cognitive_complexity'),
        
        # Per-file results
        'files': results
    }
    
    return jsonify(project_summary)