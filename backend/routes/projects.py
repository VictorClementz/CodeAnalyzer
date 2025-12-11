from flask import request, jsonify, Blueprint
from models import db, Project, ProjectFile, FileAnalysis
from routes.auth import token_required

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects', methods=['GET', 'OPTIONS', 'POST'])
@token_required
def get_projects(current_user):
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        
        if not name:
            return jsonify({'error': 'Project name is required'}), 400
        
        new_project = Project(
            name=name,
            user_id=current_user.id
        )
        
        db.session.add(new_project)
        db.session.commit()
        
        return jsonify(new_project.to_dict()), 201
    
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return jsonify([p.to_dict() for p in projects])



@projects_bp.route('/projects/<int:project_id>', methods=['GET', 'OPTIONS','DELETE'])
@token_required
def get_project_detail(current_user, project_id):
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    if request.method == 'DELETE':
        project = Project.query.get_or_404(project_id)

        if project.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        db.session.delete(project)
        db.session.commit()
        return jsonify({'message': 'Project deleted successfully'}), 200
           

       

    project = Project.query.filter_by(
        id=project_id, 
        user_id=current_user.id
    ).first_or_404()
    
    files = ProjectFile.query.filter_by(project_id=project_id).all()
    
    return jsonify({
        'project': project.to_dict(),
        'files': [f.to_dict() for f in files]
    })

@projects_bp.route('/projects/<int:project_id>/files/<int:file_id>/history', methods=['GET', 'OPTIONS'])
@token_required
def get_file_history(current_user, project_id, file_id):
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    
    file = ProjectFile.query.get_or_404(file_id)
    
    # Verify ownership
    if file.project.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    analyses = FileAnalysis.query.filter_by(file_id=file_id)\
        .order_by(FileAnalysis.timestamp.desc()).all()
    
    return jsonify({
        'file': file.to_dict(),
        'history': [a.to_dict() for a in analyses]
    })


@projects_bp.route('/projects/<int:project_id>/git', methods=['POST', 'OPTIONS'])
@token_required
def link_git_repo(current_user, project_id):
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    
    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user.id
    ).first_or_404()
    
    data = request.json
    repo_path = data.get('repo_path')
    remote_url = data.get('remote_url')
    auto_detect = data.get('auto_detect_git', True)
    
    # Validate repo path if provided
    if repo_path:
        from utils.git_utils import validate_git_repo
        is_valid, message = validate_git_repo(repo_path)
        if not is_valid:
            return jsonify({'error': f'Invalid git repository: {message}'}), 400
    
    project.git_repo_path = repo_path
    project.git_remote_url = remote_url
    project.auto_detect_git = auto_detect
    
    db.session.commit()
    
    return jsonify({
        'message': 'Git repository linked successfully',
        'project': project.to_dict()
    })

@projects_bp.route('/projects/<int:project_id>/git', methods=['DELETE'])
@token_required
def unlink_git_repo(current_user, project_id):
    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user.id
    ).first_or_404()
    
    project.git_repo_path = None
    project.git_remote_url = None
    
    db.session.commit()
    
    return jsonify({'message': 'Git repository unlinked'})

@projects_bp.route('/projects/<int:project_id>/scan-repo', methods=['POST', 'OPTIONS'])
@token_required
def scan_git_repo(current_user, project_id):
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    
    project = Project.query.filter_by(
        id=project_id,
        user_id=current_user.id
    ).first_or_404()
    
    if not project.git_repo_path:
        return jsonify({'error': 'No git repository linked'}), 400
    
    from utils.git_utils import scan_repo_files
    from infrastructure.code_analyzer import analyze_code
    from utils.git_utils import get_git_info, get_code_hash
    
    # Scan for Python files
    files_found = scan_repo_files(project.git_repo_path, language='python')
    
    if not files_found:
        return jsonify({'message': 'No Python files found', 'files_analyzed': 0})
    
    analyzed_count = 0
    errors = []
    
    # Get git info once
    git_info = get_git_info(project.git_repo_path)
    
    for file_path, code in files_found:
        try:
            # Run analysis
            results = analyze_code(code, 'python')
            
            # Get or create file
            project_file = ProjectFile.query.filter_by(
                project_id=project.id,
                filename=file_path
            ).first()
            
            if not project_file:
                project_file = ProjectFile(
                    project_id=project.id,
                    filename=file_path,
                    language='python'
                )
                db.session.add(project_file)
                db.session.flush()
            
            # Update file stats
            project_file.current_score = results['readability_score']
            project_file.last_analyzed = datetime.utcnow()
            project_file.total_analyses += 1
            
            # Create analysis record
            analysis = FileAnalysis(
                file_id=project_file.id,
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
            analyzed_count += 1
            
        except Exception as e:
            errors.append({'file': file_path, 'error': str(e)})
    
    db.session.commit()
    
    return jsonify({
        'message': f'Successfully analyzed {analyzed_count} files',
        'files_analyzed': analyzed_count,
        'errors': errors if errors else None
    })