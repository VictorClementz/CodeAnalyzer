
#Python code analyzer using Radon and Python AST.


from typing import Dict, Any
from .base_analyzer import BaseAnalyzer
from ..metrics.basic import (
    calculate_lines,
    calculate_complexity,
    calculate_maintainability,
    calculate_comment_density,
    calculate_function_length
)
from ..metrics.ast_analysis import (
    calculate_duplication_ast,
    calculate_naming_quality,
    calculate_cognitive_complexity,
    calculate_nesting_depth
)
from ..scoring import calculate_readability_score
from ..config.thresholds import get_language_config


class PythonAnalyzer(BaseAnalyzer):
    def __init__(self):
        self.language = 'python'
        self._thresholds = get_language_config('python')

    def analyze(self, code: str) -> Dict[str, Any]:
        try:
            # Basic metrics using Radon
            lines = calculate_lines(code)
            complexity = calculate_complexity(code)
            maintainability = calculate_maintainability(code)
            comment_density = calculate_comment_density(code)
            function_length = calculate_function_length(code)

            # Advanced metrics using Python AST
            duplication_percentage, duplicated_blocks_info = calculate_duplication_ast(code)
            naming_metrics = calculate_naming_quality(code)
            nesting_metrics = calculate_nesting_depth(code)
            cognitive_complexity = calculate_cognitive_complexity(code)

            # Calculate readability score with language parameter
            readability = calculate_readability_score(
                lines,
                complexity,
                maintainability,
                cognitive_complexity,
                nesting_metrics['max_depth'],
                nesting_metrics['avg_depth'],
                comment_density,
                naming_metrics['avg_name_length'],
                language=self.language
            )

            # Return standardized metrics dictionary
            return {
                'lines_of_code': lines,
                'cyclomatic_complexity': complexity,
                'maintainability_index': maintainability,
                'readability_score': readability,
                'comment_density': comment_density,
                'avg_function_length': function_length['avg'],
                'max_function_length': function_length['max'],
                'duplication_percentage': duplication_percentage,
                'duplicated_blocks_info': duplicated_blocks_info,
                'avg_name_length': naming_metrics['avg_name_length'],
                'single_letter_warnings': naming_metrics['single_letter_warnings'],
                'unclear_name_flags': naming_metrics['unclear_name_flags'],
                'sorted_name_lengths': naming_metrics['sorted_name_lengths'],
                'max_nesting_depth': nesting_metrics['max_depth'],
                'avg_nesting_depth': nesting_metrics['avg_depth'],
                'cognitive_complexity': cognitive_complexity,
                'language': self.language
            }

        except SyntaxError as e:
            # Python syntax error, return partial metrics
            return {
                'error': f'Python syntax error: {str(e)}',
                'lines_of_code': self._count_sloc(code),
                'language': self.language
            }
        except Exception as e:
            # Other analysis errors
            return {
                'error': f'Analysis failed: {str(e)}',
                'lines_of_code': self._count_sloc(code),
                'language': self.language
            }

    def get_thresholds(self) -> Dict[str, Any]:
        return self._thresholds.copy()
