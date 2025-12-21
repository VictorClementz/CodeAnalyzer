import subprocess
import hashlib
import os

def get_git_info(repo_path=None):
    try:
        original_dir = os.getcwd()
        
        if repo_path:
            os.chdir(repo_path)
        
        # Check if it's a git repository
        subprocess.run(['git', 'rev-parse', '--git-dir'], 
                      check=True, 
                      capture_output=True, 
                      text=True)
        
        # Get commit hash
        commit_hash = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                    capture_output=True, 
                                    text=True, 
                                    check=True).stdout.strip()
        
        # Get branch name
        branch = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                               capture_output=True, 
                               text=True, 
                               check=True).stdout.strip()
        
        # Get commit message
        commit_message = subprocess.run(['git', 'log', '-1', '--pretty=%B'], 
                                       capture_output=True, 
                                       text=True, 
                                       check=True).stdout.strip()
        
        if repo_path:
            os.chdir(original_dir)
        
        return {
            'commit_hash': commit_hash,
            'branch': branch,
            'commit_message': commit_message
        }
    
    except (subprocess.CalledProcessError, FileNotFoundError):
        if repo_path and os.getcwd() != original_dir:
            os.chdir(original_dir)
        return None

def get_code_hash(code):
    return hashlib.sha256(code.encode()).hexdigest()

def validate_git_repo(repo_path):
    """Check if a path is a valid git repository"""
    if not os.path.exists(repo_path):
        return False, "Path does not exist"
    
    try:
        result = subprocess.run(['git', '-C', repo_path, 'rev-parse', '--git-dir'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        if result.returncode == 0:
            return True, "Valid git repository"  # Added missing message
        else:
            return False, "Not a git repository"  # Added missing message
    except Exception as e:
        return False, str(e)
    
def scan_repo_files(repo_path, language='python'):
    """
    Scan a git repository for code files

    Args:
        repo_path: Path to git repository
        language: Programming language to scan for ('python', 'javascript', 'typescript', 'java', 'cpp')

    Returns:
        List of tuples: [(relative_path, file_content), ...]
    """
    if not os.path.exists(repo_path):
        return []
    
    # File extensions by language
    extensions = {
        'python': ['.py'],
        'javascript': ['.js', '.jsx'],
        'typescript': ['.ts', '.tsx'],
        'java': ['.java'],
        'cpp': ['.cpp', '.cc', '.cxx', '.h', '.hpp']
    }
    
    valid_extensions = extensions.get(language, ['.py'])
    
    # Directories to skip
    skip_dirs = {
        '.git', '__pycache__', 'node_modules', 'venv', 'env',
        '.venv', 'build', 'dist', '.pytest_cache', '.mypy_cache',
        'eggs', '.eggs', '*.egg-info'
    }
    
    files_found = []
    
    for root, dirs, files in os.walk(repo_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        # Get relative path from repo root
        rel_root = os.path.relpath(root, repo_path)
        
        for file in files:
            # Check if file has valid extension
            if any(file.endswith(ext) for ext in valid_extensions):
                file_path = os.path.join(root, file)
                rel_path = os.path.join(rel_root, file) if rel_root != '.' else file
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        files_found.append((rel_path, content))
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    continue
    
    return files_found