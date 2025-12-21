from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseAnalyzer(ABC):
    """
    Abstract base class for language-specific code analyzers.
    """

    #Standard metrics
    SUPPORTED_METRICS = [
        'lines_of_code',
        'cyclomatic_complexity',
        'maintainability_index',
        'readability_score',
        'comment_density',
        'avg_function_length',
        'max_function_length',
        'duplication_percentage',
        'avg_name_length',
        'max_nesting_depth',
        'avg_nesting_depth',
        'cognitive_complexity',
    ]

    @abstractmethod
    def analyze(self, code: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def get_thresholds(self) -> Dict[str, Any]:
        #Return language-specific thresholds and configuration.
        pass

    def supports_metric(self, metric_name: str) -> bool:
        return metric_name in self.SUPPORTED_METRICS

    def _count_sloc(self, code: str) -> int:
        #Count Source Lines of Code (non-blank, non-comment lines).
        lines = code.split('\n')
        sloc = 0
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('//'):
                sloc += 1
        return sloc
