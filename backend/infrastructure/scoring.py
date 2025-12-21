from .config.thresholds import get_language_config

# Legacy config for backward compatibility (Python defaults)
config = {
    'max_function_length': 40,
    'max_complexity': 10,
    'min_comment_density': 15,
    'max_nesting_depth': 3,
    'max_cognitive_complexity': 15,
    'ideal_avg_name_length': 12,
    'readability_weights': {
        'maintainability': 0.25,
        'complexity': 0.15,
        'cognitive_complexity': 0.15,
        'nesting': 0.15,
        'naming': 0.10,
        'comments': 0.10,
        'lines': 0.10
    }
}


def calculate_readability_score(lines, complexity, maintainability, cognitive_complexity,
                                max_nesting, avg_nesting, comment_density, avg_name_length,
                                language='python'):
    # Get language-specific configuration
    lang_config = get_language_config(language)
    weights = lang_config['readability_weights']
    
    # Maintainability Index (25%)
    mi_score = maintainability * weights['maintainability']
    
    # Cyclomatic Complexity (15%)
    if complexity <= 5:
        complexity_score = 100
    elif complexity <= 10:
        complexity_score = 70
    else:
        complexity_score = max(0, 100 - (complexity * 5))
    complexity_score *= weights['complexity']
    
    # Cognitive Complexity (15%)
    if cognitive_complexity <= 10:
        cognitive_score = 100
    elif cognitive_complexity <= lang_config['max_cognitive_complexity']:
        cognitive_score = 80
    else:
        cognitive_score = max(0, 100 - (cognitive_complexity * 3))
    cognitive_score *= weights['cognitive_complexity']

    # Nesting Depth (15%)
    if max_nesting <= 2:
        nesting_score = 100
    elif max_nesting <= lang_config['max_nesting_depth']:
        nesting_score = 70
    else:
        nesting_score = max(0, 100 - (max_nesting * 15))
    nesting_score *= weights['nesting']

    # Variable Naming (10%)
    name_diff = abs(avg_name_length - lang_config['ideal_avg_name_length'])
    if name_diff <= 2:
        naming_score = 100
    elif name_diff <= 4:
        naming_score = 70
    else:
        naming_score = max(0, 100 - (name_diff * 10))
    naming_score *= weights['naming']

    # Comment Density (10%)
    if comment_density >= lang_config['min_comment_density']:
        comment_score = 100
    elif comment_density >= 10:
        comment_score = 70
    elif comment_density >= 5:
        comment_score = 50
    else:
        comment_score = 30
    comment_score *= weights['comments']
    
    # Lines of Code (10%)
    if lines < 100:
        lines_score = 100
    elif lines < 300:
        lines_score = 70
    else:
        lines_score = max(0, 100 - (lines / 10))
    lines_score *= weights['lines']
    
    total_score = mi_score + complexity_score + cognitive_score + nesting_score + naming_score + comment_score + lines_score
    return round(total_score, 2)