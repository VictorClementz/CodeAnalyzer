import subprocess
import hashlib
from pathlib import Path

def get_git_info(file_path=None):
  
    try:
        #Get commit hash
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        #Get branch name
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        #Get commit message
        commit_message = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%B'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        return {
            'commit_hash': commit_hash,
            'branch': branch,
            'commit_message': commit_message
        }
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not a git repo or git not installed
        return None

def get_code_hash(code):
    return hashlib.sha256(code.encode()).hexdigest()

def is_git_repo():
    try:
        subprocess.check_output(
            ['git', 'rev-parse', '--git-dir'],
            stderr=subprocess.DEVNULL
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False