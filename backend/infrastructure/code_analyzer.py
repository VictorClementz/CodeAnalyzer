
#Main code analysis entry point using language-specific analyzers.
#This module provides the analyze_code() function which dispatches to
#language-specific analyzers based on the language parameter.


from .analyzers.factory import LanguageAnalyzerFactory


def analyze_code(code, language, user_config=None):
    try:
        # Get the appropriate analyzer for this language
        analyzer = LanguageAnalyzerFactory.get_analyzer(language)

        # Analyze the code
        results = analyzer.analyze(code)

        return results

    except ValueError as e:
        # Unsupported language
        return {
            'error': str(e),
            'lines_of_code': _simple_line_count(code),
            'language': language
        }

    except Exception as e:
        # Unexpected error during analysis
        return {
            'error': f'Analysis failed: {str(e)}',
            'lines_of_code': _simple_line_count(code),
            'language': language
        }


def _simple_line_count(code: str) -> int:
    return len([line for line in code.split('\n') if line.strip()])
