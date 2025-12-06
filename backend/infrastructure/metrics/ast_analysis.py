# infrastructure/metrics/ast_analysis.py

import ast
from collections import defaultdict

def get_ast_fingerprint(node): #Creates a AST for the code
    if isinstance(node, ast.Name):
        return (type(node).__name__, node.ctx.__class__.__name__, "$NAME$")
    
    if isinstance(node, (ast.Constant, ast.Str, ast.Num)):
        return (type(node).__name__, "$CONST$")
    
    node_type = type(node).__name__
    children = tuple(
        get_ast_fingerprint(child) 
        for child in ast.iter_child_nodes(node)
    )
    return (node_type, children)

def calculate_duplication_ast(code): #Duplicated code
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 0.0, []

    fingerprints = defaultdict(list)
    total_relevant_lines = 0
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.If, ast.For)):
            fingerprint = get_ast_fingerprint(node)
            fingerprints[fingerprint].append(node)
            
            if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                total_relevant_lines += (node.end_lineno - node.lineno + 1)

    duplicated_lines_count = 0
    duplicated_blocks_info = []

    for fingerprint, nodes in fingerprints.items():
        if len(nodes) > 1:
            for node in nodes[1:]: 
                if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                    duplicated_lines_count += (node.end_lineno - node.lineno + 1)
                    duplicated_blocks_info.append(f"Block near line {node.lineno} duplicated.")

    if total_relevant_lines == 0:
        return 0.0, []
        
    duplication_percentage = (duplicated_lines_count / total_relevant_lines) * 100
    
    return round(duplication_percentage, 2), duplicated_blocks_info