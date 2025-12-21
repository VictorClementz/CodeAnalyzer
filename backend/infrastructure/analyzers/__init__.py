"""
This package contains the analyzer infrastructure for supporting
multiple programming languages in the CodeReader application.
"""

from .base_analyzer import BaseAnalyzer
from .factory import LanguageAnalyzerFactory

__all__ = ['BaseAnalyzer', 'LanguageAnalyzerFactory']
