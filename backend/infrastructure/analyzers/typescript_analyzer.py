#TypeScript code analyzer.
#his analyzer treats TypeScript as JavaScript by stripping type annotations
#nd then delegating to the JavaScript analyzer.


import re
from typing import Dict, Any
from .javascript_analyzer import JavaScriptAnalyzer
from ..config.thresholds import get_language_config


class TypeScriptAnalyzer(JavaScriptAnalyzer):

    def __init__(self):
        self.language = 'typescript'
        self._thresholds = get_language_config('typescript')

    def analyze(self, code: str) -> Dict[str, Any]:
        try:
            #Strip TypeScript-specific syntax
            js_code = self._strip_typescript_syntax(code)

            #Use JavaScript analyzer for the rest
            results = super().analyze(js_code)

            #Override language in results
            results['language'] = self.language

            return results

        except Exception as e:
            # Analysis error
            return {
                'error': f'TypeScript analysis failed: {str(e)}',
                'lines_of_code': len([l for l in code.split('\n') if l.strip()]),
                'language': self.language
            }

    def _strip_typescript_syntax(self, code: str) -> str:
        # Remove readonly, public, private, protected, static modifiers (do this first)
        code = re.sub(r'\b(readonly|public|private|protected|static)\s+', '', code)

        # Remove type parameters from functions and classes
        # Example: function foo<T>(x) -> function foo(x)
        # Example: class Container<T> -> class Container
        code = re.sub(r'<[^>]+>', '', code)

        # Remove optional parameter markers (?)
        # Example: lastName?: string -> lastName: string
        code = re.sub(r'(\w+)\?:', r'\1:', code)

        # Remove type annotations after variable/parameter declarations
        # Example: const foo: string = "bar" -> const foo = "bar"
        # Example: value: number; -> value;
        code = re.sub(r'(\w+)\s*:\s*[^;,=\)}\n]+([;,=\)}\n])', r'\1\2', code)

        # Remove bare property declarations (value;) inside classes
        # These are TypeScript-only and not valid in JavaScript
        code = re.sub(r'^\s*\w+\s*;\s*$', '', code, flags=re.MULTILINE)

        # Remove function return type annotations (including arrow functions)
        # Example: function foo(): string { -> function foo() {
        # Example: (): number => { -> () => {
        code = re.sub(r'\)\s*:\s*[^{;=>\n]+(\s*[{;=>\n])', r')\1', code)

        # Remove interface declarations
        code = re.sub(r'interface\s+\w+\s*\{[^}]*\}', '', code)

        # Remove type aliases (handle multi-line type definitions)
        code = re.sub(r'type\s+\w+[^;]*;', '', code)

        # Remove enum declarations
        code = re.sub(r'enum\s+\w+\s*\{[^}]*\}', '', code)

        # Remove 'as' type assertions
        # Example: foo as string -> foo
        code = re.sub(r'\s+as\s+\w+', '', code)

        # Remove non-null assertion operator (!)
        code = re.sub(r'!(\s*[;,\)\]])', r'\1', code)

        # Remove implements clauses
        code = re.sub(r'\s+implements\s+[\w,\s]+', '', code)

        # Remove declare statements
        code = re.sub(r'declare\s+', '', code)

        # Remove namespace declarations (keep content)
        code = re.sub(r'namespace\s+\w+\s*\{', '{', code)

        return code

    def get_thresholds(self) -> Dict[str, Any]:
        return self._thresholds.copy()
