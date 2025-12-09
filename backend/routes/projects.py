from flask import Blueprint, jsonify, request
from models import db, Project, ProjectFile, FileAnalysis
from routes.auth import token_required

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/projects', methods=['GET', 'OPTIONS'])
@token_required
def get_projects(current_user):
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return jsonify([p.to_dict() for p in projects])

@projects_bp.route('/projects/<int:project_id>', methods=['GET', 'OPTIONS'])
@token_required
def get_project_detail(current_user, project_id):
    if request.method == "OPTIONS":
        return jsonify({"ok": True}), 200
    
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