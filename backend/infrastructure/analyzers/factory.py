#Factory for creating language specific code analyzers

from typing import Dict
from .base_analyzer import BaseAnalyzer


class LanguageAnalyzerFactory:

   #Uses lazy loading to only import and instantiate analyzers when needed.

    #Cache for analyzer instances
    _analyzers: Dict[str, BaseAnalyzer] = {}

    #Supported languages
    SUPPORTED_LANGUAGES = ['python', 'javascript', 'typescript', 'java']

    @classmethod
    def get_analyzer(cls, language: str) -> BaseAnalyzer:
        
       #Get or create an analyzer

        #Normalize language to lowercase
        language = language.lower()

        #Check if language is supported
        if language not in cls.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: '{language}'. "
                f"Supported languages: {', '.join(cls.SUPPORTED_LANGUAGES)}"
            )

        #Return cached analyzer if available
        if language in cls._analyzers:
            return cls._analyzers[language]

        #Create new analyzer instance
        analyzer = cls._create_analyzer(language)
        cls._analyzers[language] = analyzer
        return analyzer

    @classmethod
    def _create_analyzer(cls, language: str) -> BaseAnalyzer:
        if language == 'python':
            from .python_analyzer import PythonAnalyzer
            return PythonAnalyzer()

        elif language == 'javascript':
            from .javascript_analyzer import JavaScriptAnalyzer
            return JavaScriptAnalyzer()

        elif language == 'typescript':
            from .typescript_analyzer import TypeScriptAnalyzer
            return TypeScriptAnalyzer()

        elif language == 'java':
            from .java_analyzer import JavaAnalyzer
            return JavaAnalyzer()

        # This should never happen due to the check in get_analyzer()
        raise ValueError(f"Unknown language: {language}")

    @classmethod
    def clear_cache(cls):
        cls._analyzers.clear()

    @classmethod
    def is_supported(cls, language: str) -> bool:
        return language.lower() in cls.SUPPORTED_LANGUAGES
