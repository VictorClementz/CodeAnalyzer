from flask import Blueprint, request, jsonify
from infrastructure.code_analyzer import analyze_code
from models import db, Project, ProjectFile, FileAnalysis
from routes.auth import token_required
from utils.git_utils import get_git_info, get_code_hash
from datetime import datetime

analyze_bp = Blueprint('analyze', __name__)

@analyze_bp.route('/analyze', methods=['POST'])
@token_required
def analyze(current_user):
    data = request.json
    code = data.get('code', '')
    language = data.get('language', 'python')
    project_name = data.get('project_name') 
    filename = data.get('filename', 'untitled.py') 
    save_results = data.get('save_results', False)
    
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    try:
        #Run analysis
        results = analyze_code(code, language)
        
        #Save to database if requested
        if save_results and current_user:
            #get or create project
            if project_name:
                project = Project.query.filter_by(
                    user_id=current_user.id, 
                    name=project_name
                ).first()
                
                if not project:
                    project = Project(user_id=current_user.id, name=project_name)
                    db.session.add(project)
                    db.session.flush()
            else:
                # Use default project
                project = Project.query.filter_by(
                    user_id=current_user.id, 
                    name='Default Project'
                ).first()
                
                if not project:
                    project = Project(user_id=current_user.id, name='Default Project')
                    db.session.add(project)
                    db.session.flush()
            
            file = ProjectFile.query.filter_by(
                project_id=project.id,
                filename=filename
            ).first()
            
            if not file:
                file = ProjectFile(
                    project_id=project.id,
                    filename=filename,
                    language=language
                )
                db.session.add(file)
                db.session.flush()
            
            #Update file stats
            file.current_score = results['readability_score']
            file.last_analyzed = datetime.utcnow()
            file.total_analyses += 1
            
            #Get git 
            git_info = get_git_info()
            
            #Create analysis record
            analysis = FileAnalysis(
                file_id=file.id,
                commit_hash=git_info['commit_hash'] if git_info else None,
                commit_message=git_info['commit_message'] if git_info else None,
                branch=git_info['branch'] if git_info else None,
                code_hash=get_code_hash(code),
                readability_score=results['readability_score'],
                cyclomatic_complexity=results['cyclomatic_complexity'],
                maintainability_index=results['maintainability_index'],
                lines_of_code=results['lines_of_code'],
                comment_density=results['comment_density'],
                duplication_percentage=results['duplication_percentage'],
                avg_name_length=results['avg_name_length'],
                max_nesting_depth=results['max_nesting_depth'],
                avg_nesting_depth=results['avg_nesting_depth'],
                cognitive_complexity=results['cognitive_complexity'],
                avg_function_length=results['avg_function_length'],
                max_function_length=results['max_function_length']
            )
            
            db.session.add(analysis)
            db.session.commit()
            
            results['saved'] = True
            results['analysis_id'] = analysis.id
        
        return jsonify(results)
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@analyze_bp.route('/analyze-batch', methods=['POST'])
@token_required
def analyze_batch(current_user):
    files = request.files.getlist('files')
    
    if not files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    language = request.form.get('language', 'python')
    project_name = request.form.get('project_name', 'Batch Upload')
    
    #Get or create project
    project = Project.query.filter_by(
        user_id=current_user.id,
        name=project_name
    ).first()
    
    if not project:
        project = Project(user_id=current_user.id, name=project_name)
        db.session.add(project)
        db.session.flush()
    
    results = []
    
    for file in files:
        filename = file.filename
        
        #Filter by language
        if language == 'python' and not filename.endswith('.py'):
            continue
        elif language == 'javascript' and not filename.endswith('.js'):
            continue
        
        try:
            code = file.read().decode('utf-8')
            analysis_results = analyze_code(code, language)
            
            #Save to database
            project_file = ProjectFile.query.filter_by(
                project_id=project.id,
                filename=filename
            ).first()
            
            if not project_file:
                project_file = ProjectFile(
                    project_id=project.id,
                    filename=filename,
                    language=language
                )
                db.session.add(project_file)
                db.session.flush()
            
            #Update file stats
            project_file.current_score = analysis_results['readability_score']
            project_file.last_analyzed = datetime.utcnow()
            project_file.total_analyses += 1
            
            #Get git info
            git_info = get_git_info()
            
            #Create analysis record
            analysis = FileAnalysis(
                file_id=project_file.id,
                commit_hash=git_info['commit_hash'] if git_info else None,
                commit_message=git_info['commit_message'] if git_info else None,
                branch=git_info['branch'] if git_info else None,
                code_hash=get_code_hash(code),
                readability_score=analysis_results['readability_score'],
                cyclomatic_complexity=analysis_results['cyclomatic_complexity'],
                maintainability_index=analysis_results['maintainability_index'],
                lines_of_code=analysis_results['lines_of_code'],
                comment_density=analysis_results['comment_density'],
                duplication_percentage=analysis_results['duplication_percentage'],
                avg_name_length=analysis_results['avg_name_length'],
                max_nesting_depth=analysis_results['max_nesting_depth'],
                avg_nesting_depth=analysis_results['avg_nesting_depth'],
                cognitive_complexity=analysis_results['cognitive_complexity'],
                avg_function_length=analysis_results['avg_function_length'],
                max_function_length=analysis_results['max_function_length']
            )
            
            db.session.add(analysis)
            
            results.append({
                'filename': filename,
                'metrics': analysis_results
            })
            
        except Exception as e:
            results.append({
                'filename': filename,
                'error': str(e)
            })
    
    db.session.commit()
    
    #Calculate
    valid_results = [r for r in results if 'metrics' in r]
    
    if not valid_results:
        return jsonify({'error': 'No valid files found'}), 400
    
    def safe_avg(key):
        values = [r['metrics'][key] for r in valid_results if r['metrics'].get(key) is not None]
        return round(sum(values) / len(values), 2) if values else 0
    
    project_summary = {
        'project_id': project.id,
        'project_name': project.name,
        'total_files': len(valid_results),
        'avg_readability': safe_avg('readability_score'),
        'avg_complexity': safe_avg('cyclomatic_complexity'),
        'avg_maintainability': safe_avg('maintainability_index'),
        'total_lines': sum(r['metrics']['lines_of_code'] for r in valid_results),
        'files': results
    }
    
    return jsonify(project_summary)