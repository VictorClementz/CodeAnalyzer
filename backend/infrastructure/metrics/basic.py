from radon.raw import analyze
from radon.complexity import cc_visit
from radon.metrics import mi_visit

def calculate_lines(code):
    raw_metrics = analyze(code)
    return raw_metrics.sloc

def calculate_complexity(code):
    complexity_results = cc_visit(code)
    
    if complexity_results:
        avg_complexity = sum(result.complexity for result in complexity_results) / len(complexity_results)
        return round(avg_complexity, 2)
    return 0

def calculate_maintainability(code):
    mi_score = mi_visit(code, multi=True)
    
    if mi_score:
        return round(mi_score, 2)
    return 0

def calculate_comment_density(code):
    raw_metrics = analyze(code)
    
    total_lines = raw_metrics.loc
    comment_lines = raw_metrics.comments
    
    if total_lines > 0:
        density = (comment_lines / total_lines) * 100
        return round(density, 2)
    return 0

def calculate_function_length(code):
    complexity_results = cc_visit(code)
    
    if complexity_results:
        function_lengths = [result.endline - result.lineno + 1 for result in complexity_results]
        
        avg_length = sum(function_lengths) / len(function_lengths)
        max_length = max(function_lengths)
        
        return {
            'avg': round(avg_length, 2),
            'max': max_length
        }
    
    return {'avg': 0, 'max': 0}