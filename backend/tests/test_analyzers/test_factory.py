"""
Tests for LanguageAnalyzerFactory.
"""
import pytest
from infrastructure.analyzers.factory import LanguageAnalyzerFactory
from infrastructure.analyzers.python_analyzer import PythonAnalyzer
from infrastructure.analyzers.javascript_analyzer import JavaScriptAnalyzer
from infrastructure.analyzers.typescript_analyzer import TypeScriptAnalyzer
from infrastructure.analyzers.java_analyzer import JavaAnalyzer


class TestLanguageAnalyzerFactory:
    """Test the language analyzer factory."""

    def test_get_python_analyzer(self):
        """Test getting Python analyzer from factory."""
        analyzer = LanguageAnalyzerFactory.get_analyzer('python')
        assert isinstance(analyzer, PythonAnalyzer)
        assert analyzer.language == 'python'

    def test_get_javascript_analyzer(self):
        """Test getting JavaScript analyzer from factory."""
        analyzer = LanguageAnalyzerFactory.get_analyzer('javascript')
        assert isinstance(analyzer, JavaScriptAnalyzer)
        assert analyzer.language == 'javascript'

    def test_get_typescript_analyzer(self):
        """Test getting TypeScript analyzer from factory."""
        analyzer = LanguageAnalyzerFactory.get_analyzer('typescript')
        assert isinstance(analyzer, TypeScriptAnalyzer)
        assert analyzer.language == 'typescript'

    def test_get_java_analyzer(self):
        """Test getting Java analyzer from factory."""
        analyzer = LanguageAnalyzerFactory.get_analyzer('java')
        assert isinstance(analyzer, JavaAnalyzer)
        assert analyzer.language == 'java'

    def test_case_insensitive(self):
        """Test that language parameter is case-insensitive."""
        analyzer1 = LanguageAnalyzerFactory.get_analyzer('PYTHON')
        analyzer2 = LanguageAnalyzerFactory.get_analyzer('Python')
        analyzer3 = LanguageAnalyzerFactory.get_analyzer('python')

        assert isinstance(analyzer1, PythonAnalyzer)
        assert isinstance(analyzer2, PythonAnalyzer)
        assert isinstance(analyzer3, PythonAnalyzer)

    def test_unsupported_language(self):
        """Test that unsupported language raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported language"):
            LanguageAnalyzerFactory.get_analyzer('ruby')

    def test_analyzer_caching(self):
        """Test that factory caches analyzer instances."""
        analyzer1 = LanguageAnalyzerFactory.get_analyzer('python')
        analyzer2 = LanguageAnalyzerFactory.get_analyzer('python')

        # Should be the same instance (cached)
        assert analyzer1 is analyzer2

    def test_supported_languages(self):
        """Test that all supported languages are listed."""
        supported = LanguageAnalyzerFactory.SUPPORTED_LANGUAGES

        assert 'python' in supported
        assert 'javascript' in supported
        assert 'typescript' in supported
        assert 'java' in supported
        assert len(supported) == 4

    def test_all_analyzers_have_thresholds(self):
        """Test that all analyzers provide thresholds."""
        for language in LanguageAnalyzerFactory.SUPPORTED_LANGUAGES:
            analyzer = LanguageAnalyzerFactory.get_analyzer(language)
            thresholds = analyzer.get_thresholds()

            assert isinstance(thresholds, dict)
            assert 'max_function_length' in thresholds
            assert 'max_complexity' in thresholds
            assert 'ideal_avg_name_length' in thresholds
