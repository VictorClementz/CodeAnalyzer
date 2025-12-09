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

class VariableNameVisitor(ast.NodeVisitor):
    
    def __init__(self):
        self.all_names = []
        self.single_letter_warnings = []
        self.unclear_names = []
        self.name_lengths = []

    def visit_Name(self, node):
        name = node.id
        self.all_names.append(name)
        self.name_lengths.append(len(name))
        
        # Flag single-letter variables unless they are common loop indices
        if len(name) == 1 and name not in ('i', 'j', 'k', 'n', 'e', 'x', 'y'):
            # Only flag names used for assigning or loading (not built-in context)
            if isinstance(node.ctx, (ast.Load, ast.Store)):
                self.single_letter_warnings.append(name)
        
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Analyze argument names
        for arg in node.args.args:
            name = arg.arg
            self.all_names.append(name)
            if len(name) == 1 and name not in ('a', 'b', 'c', 'x', 'y'):
                self.single_letter_warnings.append(name)
        self.generic_visit(node)

def calculate_naming_quality(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            'avg_name_length': 0.0, 
            'single_letter_warnings': [], 
            'unclear_name_flags': []
        }

    visitor = VariableNameVisitor()
    visitor.visit(tree)

    # 1. Calculate Average Length
    # Exclude Python's standard dunder names (e.g., __name__, __init__)
    meaningful_names = [name for name in visitor.all_names if not name.startswith('__')]
    
    if not meaningful_names:
        avg_length = 0.0
    else:
        total_length = sum(len(name) for name in meaningful_names)
        avg_length = total_length / len(meaningful_names)

    # 2. Detect Unclear Names (Simple Heuristic)
    # Flag common non-descriptive filler names
    unclear_flags = []
    unclear_keywords = ('temp', 'val', 'data', 'info', 'thing')
    
    for name in meaningful_names:
        if name in unclear_keywords and len(name) < 6:
            unclear_flags.append(name)
    
    # 3. Compile and return results
    return {
        'avg_name_length': round(avg_length, 2),
        'single_letter_warnings': list(set(visitor.single_letter_warnings)),
        'unclear_name_flags': list(set(unclear_flags)),
        'sorted_name_lengths': sorted(visitor.name_lengths)
    }

class NestingDepthVisitor(ast.NodeVisitor):
    NESTING_NODES = (ast.If, ast.For, ast.While, ast.With, ast.Try, 
                     ast.ExceptHandler, ast.FunctionDef, ast.AsyncFor, ast.AsyncWith)
    
    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0
        self.depth_counts = []
    
    def visit(self, node):
        if isinstance(node, self.NESTING_NODES):
            self.current_depth += 1
            self.max_depth = max(self.max_depth, self.current_depth)
            self.depth_counts.append(self.current_depth)
            self.generic_visit(node)
            self.current_depth -= 1
        else:
            self.generic_visit(node)

def calculate_nesting_depth(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {'max_depth': 0, 'avg_depth': 0.0}
    
    visitor = NestingDepthVisitor()
    visitor.visit(tree)
    
    avg_depth = sum(visitor.depth_counts) / len(visitor.depth_counts) if visitor.depth_counts else 0.0
    
    return {
        'max_depth': visitor.max_depth,
        'avg_depth': round(avg_depth, 2)
    }


class CognitiveComplexityVisitor(ast.NodeVisitor):
    NESTING_NODES = (ast.If, ast.For, ast.While, ast.Try)
    
    def __init__(self):
        self.complexity = 0
        self.nesting_level = 0
    
    def visit(self, node):
        if isinstance(node, self.NESTING_NODES):
            self.complexity += 1 + self.nesting_level
            self.nesting_level += 1
            self.generic_visit(node)
            self.nesting_level -= 1
        elif isinstance(node, (ast.ExceptHandler, ast.Lambda, ast.ListComp, ast.DictComp)):
            self.complexity += 1 + self.nesting_level
            self.generic_visit(node)
        elif isinstance(node, ast.BoolOp):
            self.complexity += len(node.values) - 1 + self.nesting_level
            self.generic_visit(node)
        else:
            self.generic_visit(node)

def calculate_cognitive_complexity(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return 0
    
    visitor = CognitiveComplexityVisitor()
    visitor.visit(tree)
    return visitor.complexity

