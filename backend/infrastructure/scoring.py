#default config but hte user can define there own later
config = {
    'max_function_length': 40,
    'max_complexity': 10,
    'min_comment_density': 15,
    'max_nesting_depth': 3,
    'readability_weights': {
        'maintainability': 0.5,
        'complexity': 0.3,
        'lines': 0.2
    }
}

def calculate_readability_score(lines, complexity, maintainability):
    # Maintainability contributes 50%
    mi_score = maintainability * config['readability_weights']['maintainability']
    
    # Complexity contributes 30%
    if complexity <= 5:
        complexity_score = 100
    elif complexity <= 10:
        complexity_score = 70
    else:
        complexity_score = max(0, 100 - (complexity * 5))
    complexity_score *= config['readability_weights']['complexity']
    
    # Lines contributes 20%
    if lines < 100:
        lines_score = 100
    elif lines < 300:
        lines_score = 70
    else:
        lines_score = max(0, 100 - (lines / 10))
    lines_score *= config['readability_weights']['lines']
    
    total_score = mi_score + complexity_score + lines_score
    return round(total_score, 2)