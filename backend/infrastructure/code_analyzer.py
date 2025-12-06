from radon.raw import analyze
from radon.complexity import cc_visit
from radon.metrics import mi_visit

def analyze_code(code, language):
    lines = _calculate_lines(code)
    complexity = _calculate_complexity(code)
    maintainability = _calculate_maintainability(code)
    readability = _calculate_readability_score(lines, complexity, maintainability)
    
    return {
        'lines_of_code': lines,
        'cyclomatic_complexity': complexity,
        'maintainability_index': maintainability,
        'readability_score': readability
    }

def _calculate_lines(code):
    raw_metrics = analyze(code)
    return raw_metrics.sloc

def _calculate_complexity(code):
    complexity_results = cc_visit(code)
    
    if complexity_results:
        avg_complexity = sum(result.complexity for result in complexity_results) / len(complexity_results)
        return round(avg_complexity, 2)
    return 0

def _calculate_maintainability(code):
    mi_score = mi_visit(code, multi=True)
    
    if mi_score:
        return round(mi_score, 2)
    return 0

def _calculate_readability_score(lines, complexity, maintainability):
    # Maintainability contributes 50%
    mi_score = maintainability * 0.5
    
    # Complexity contributes 30%
    if complexity <= 5:
        complexity_score = 100
    elif complexity <= 10:
        complexity_score = 70
    else:
        complexity_score = max(0, 100 - (complexity * 5))
    complexity_score *= 0.3
    
    # Lines contributes 20%
    if lines < 100:
        lines_score = 100
    elif lines < 300:
        lines_score = 70
    else:
        lines_score = max(0, 100 - (lines / 10))
    lines_score *= 0.2
    
    total_score = mi_score + complexity_score + lines_score
    return round(total_score, 2)