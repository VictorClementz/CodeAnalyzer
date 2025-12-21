"""
Language-specific thresholds and configuration for code analysis.

Each language has different conventions and best practices, so we use
different thresholds for metrics like function length, complexity, etc.
"""

LANGUAGE_CONFIGS = {
    'python': {
        'max_function_length': 40,
        'max_complexity': 10,
        'min_comment_density': 15,
        'ideal_avg_name_length': 12,  # Python convention: descriptive snake_case names
        'max_nesting_depth': 3,
        'max_cognitive_complexity': 15,
        'readability_weights': {
            'maintainability': 0.25,
            'complexity': 0.15,
            'cognitive_complexity': 0.15,
            'nesting': 0.15,
            'naming': 0.10,
            'comments': 0.10,
            'lines': 0.10
        }
    },
    'javascript': {
        'max_function_length': 30,  # JS tends to be more modular with smaller functions
        'max_complexity': 8,
        'min_comment_density': 10,  # JSDoc not always required, code should be self-documenting
        'ideal_avg_name_length': 8,  # camelCase typically shorter
        'max_nesting_depth': 3,
        'max_cognitive_complexity': 12,
        'readability_weights': {
            'maintainability': 0.25,
            'complexity': 0.20,  # Complexity more important in JS
            'cognitive_complexity': 0.15,
            'nesting': 0.15,
            'naming': 0.10,
            'comments': 0.05,  # Less weight on comments
            'lines': 0.10
        }
    },
    'typescript': {
        'max_function_length': 35,
        'max_complexity': 8,
        'min_comment_density': 8,  # Types provide documentation, less need for comments
        'ideal_avg_name_length': 10,  # Slightly longer for clarity
        'max_nesting_depth': 3,
        'max_cognitive_complexity': 12,
        'readability_weights': {
            'maintainability': 0.25,
            'complexity': 0.20,
            'cognitive_complexity': 0.15,
            'nesting': 0.15,
            'naming': 0.10,
            'comments': 0.05,  # Types reduce need for comments
            'lines': 0.10
        }
    },
    'java': {
        'max_function_length': 50,  # Java more verbose
        'max_complexity': 12,
        'min_comment_density': 20,  # JavaDoc culture emphasizes documentation
        'ideal_avg_name_length': 15,  # Java naming conventions very verbose
        'max_nesting_depth': 4,  # Java code tends to be more nested
        'max_cognitive_complexity': 18,
        'readability_weights': {
            'maintainability': 0.25,
            'complexity': 0.15,
            'cognitive_complexity': 0.15,
            'nesting': 0.10,  # Less weight on nesting (expected to be higher)
            'naming': 0.10,
            'comments': 0.15,  # More weight on documentation
            'lines': 0.10
        }
    }
}


def get_language_config(language: str) -> dict:
    """
    Get configuration for a specific language.

    Args:
        language: Programming language (e.g., 'python', 'javascript')

    Returns:
        Configuration dictionary for the language

    Raises:
        ValueError: If language is not supported
    """
    language = language.lower()
    if language not in LANGUAGE_CONFIGS:
        raise ValueError(
            f"No configuration found for language: '{language}'. "
            f"Supported languages: {', '.join(LANGUAGE_CONFIGS.keys())}"
        )
    return LANGUAGE_CONFIGS[language]


def get_supported_languages() -> list:
    """
    Get list of languages with defined configurations.

    Returns:
        List of supported language names
    """
    return list(LANGUAGE_CONFIGS.keys())
