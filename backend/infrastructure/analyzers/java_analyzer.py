
#Java code analyzer using javalang parser.

import javalang
from typing import Dict, Any, List
from .base_analyzer import BaseAnalyzer
from ..scoring import calculate_readability_score
from ..config.thresholds import get_language_config


class JavaAnalyzer(BaseAnalyzer):
    #Implements all 13 metrics using custom AST visitors and analysis routines.
    def __init__(self):
        self.language = 'java'
        self._thresholds = get_language_config('java')

    def analyze(self, code: str) -> Dict[str, Any]:
        try:
            #Parse Java code into AST
            tree = javalang.parse.parse(code)

            #Calculate all metrics
            lines_of_code = self._count_sloc(code)
            complexity_result = self._calculate_complexity(tree)
            maintainability = self._calculate_maintainability(
                lines_of_code,
                complexity_result['total_complexity'],
                complexity_result['method_count']
            )
            comment_density = self._calculate_comment_density(code)
            function_lengths = self._calculate_function_lengths(tree)
            duplication_result = self._calculate_duplication(tree)
            naming_result = self._calculate_naming_quality(tree)
            nesting_result = self._calculate_nesting_depth(tree)
            cognitive_complexity = self._calculate_cognitive_complexity(tree)

            #Calculate readability score
            readability = calculate_readability_score(
                lines_of_code,
                complexity_result['avg_complexity'],
                maintainability,
                cognitive_complexity,
                nesting_result['max_depth'],
                nesting_result['avg_depth'],
                comment_density,
                naming_result['avg_name_length'],
                language=self.language
            )

            return {
                'lines_of_code': lines_of_code,
                'cyclomatic_complexity': complexity_result['avg_complexity'],
                'maintainability_index': maintainability,
                'readability_score': readability,
                'comment_density': comment_density,
                'avg_function_length': function_lengths['avg'],
                'max_function_length': function_lengths['max'],
                'duplication_percentage': duplication_result['percentage'],
                'duplicated_blocks_info': duplication_result['blocks'],
                'avg_name_length': naming_result['avg_name_length'],
                'single_letter_warnings': naming_result['single_letter_warnings'],
                'unclear_name_flags': naming_result['unclear_name_flags'],
                'sorted_name_lengths': naming_result['sorted_name_lengths'],
                'max_nesting_depth': nesting_result['max_depth'],
                'avg_nesting_depth': nesting_result['avg_depth'],
                'cognitive_complexity': cognitive_complexity,
                'language': self.language
            }

        except javalang.parser.JavaSyntaxError as e:
            return {
                'error': f'Java syntax error: {str(e)}',
                'lines_of_code': len([l for l in code.split('\n') if l.strip()]),
                'language': self.language
            }
        except Exception as e:
            return {
                'error': f'Java analysis failed: {str(e)}',
                'lines_of_code': len([l for l in code.split('\n') if l.strip()]),
                'language': self.language
            }

    def _count_sloc(self, code: str) -> int:
        lines = code.split('\n')
        sloc = 0
        in_multiline_comment = False

        for line in lines:
            stripped = line.strip()

            #Skip blank lines
            if not stripped:
                continue

            #Handle multi-line comments
            if '/*' in stripped:
                in_multiline_comment = True
            if '*/' in stripped:
                in_multiline_comment = False
                continue
            if in_multiline_comment:
                continue

            #Skip single-line comments
            if stripped.startswith('//'):
                continue

            sloc += 1

        return sloc

    def _calculate_complexity(self, tree) -> Dict[str, Any]:
        complexity_sum = 0
        method_count = 0

        for path, node in tree:
            # Count methods
            if isinstance(node, javalang.tree.MethodDeclaration):
                method_count += 1
                complexity_sum += 1  # Base complexity

            # Count decision points
            elif isinstance(node, (javalang.tree.IfStatement, javalang.tree.TernaryExpression)):
                complexity_sum += 1
            elif isinstance(node, (javalang.tree.WhileStatement, javalang.tree.DoStatement,
                                   javalang.tree.ForStatement, javalang.tree.ForControl)):
                complexity_sum += 1
            elif isinstance(node, javalang.tree.SwitchStatementCase):
                complexity_sum += 1
            elif isinstance(node, javalang.tree.CatchClause):
                complexity_sum += 1

        avg_complexity = round(complexity_sum / max(method_count, 1), 2)

        return {
            'total_complexity': complexity_sum,
            'method_count': method_count,
            'avg_complexity': avg_complexity
        }

    def _calculate_maintainability(self, lines: int, complexity: int, method_count: int) -> float:
        #Calculate maintainability index using a formula adapted for Java.
        #Simplified Halstead volume estimation
        volume = (lines + method_count) * 2.4

        #Maintainability Index formula
        import math

        if volume <= 0 or lines <= 0:
            return 100

        try:
            mi = 171 - 5.2 * math.log(volume) - 0.23 * complexity - 16.2 * math.log(lines)
            mi = max(0, (mi * 100) / 171)
            return round(min(100, mi), 2)
        except:
            return 50  #Default moderate score on calculation error

    def _calculate_comment_density(self, code: str) -> float:
        lines = code.split('\n')
        total_lines = len(lines)

        if total_lines == 0:
            return 0.0

        comment_lines = 0
        in_multiline_comment = False

        for line in lines:
            stripped = line.strip()

            if '/*' in stripped:
                in_multiline_comment = True
            if in_multiline_comment:
                comment_lines += 1
            if '*/' in stripped:
                in_multiline_comment = False
                continue

            if stripped.startswith('//'):
                comment_lines += 1

        density = (comment_lines / total_lines) * 100
        return round(density, 2)

    def _calculate_function_lengths(self, tree) -> Dict[str, Any]:
        method_lengths = []

        for path, node in tree:
            if isinstance(node, javalang.tree.MethodDeclaration):
                #Estimate method length by counting statements
                statement_count = self._count_statements(node)
                method_lengths.append(statement_count)

        if not method_lengths:
            return {'avg': 0, 'max': 0}

        return {
            'avg': round(sum(method_lengths) / len(method_lengths), 2),
            'max': max(method_lengths)
        }

    def _count_statements(self, node) -> int:
        #Count statements in a method body
        count = 0

        if not hasattr(node, 'body') or node.body is None:
            return 0

        for stmt in node.body:
            count += 1
            #Recursively count nested statements
            if hasattr(stmt, 'then_statement'):
                count += self._count_nested_statements(stmt.then_statement)
            if hasattr(stmt, 'else_statement') and stmt.else_statement:
                count += self._count_nested_statements(stmt.else_statement)
            if hasattr(stmt, 'body') and stmt.body:
                if isinstance(stmt.body, list):
                    count += len(stmt.body)

        return count

    def _count_nested_statements(self, stmt) -> int:
        #Count statements in a nested block
        if stmt is None:
            return 0

        if isinstance(stmt, list):
            return len(stmt)

        return 1

    def _calculate_duplication(self, tree) -> Dict[str, Any]:
        #Simplified duplication detection usin ast
        method_signatures = []

        for path, node in tree:
            if isinstance(node, javalang.tree.MethodDeclaration):
                signature = self._create_method_signature(node)
                method_signatures.append(signature)

        #Find duplicates
        duplicates = []
        seen = {}
        for i, signature in enumerate(method_signatures):
            if signature in seen:
                duplicates.append({'block': i, 'duplicate_of': seen[signature]})
            else:
                seen[signature] = i

        total_methods = len(method_signatures)
        duplicate_count = len(duplicates)

        percentage = (duplicate_count / max(total_methods, 1)) * 100 if total_methods > 0 else 0

        return {
            'percentage': round(percentage, 2),
            'blocks': duplicates
        }

    def _create_method_signature(self, method) -> str:
        signature_parts = []

        if hasattr(method, 'body') and method.body:
            for stmt in method.body[:3]:  #First 3 statements
                signature_parts.append(type(stmt).__name__)

        return '-'.join(signature_parts) if signature_parts else 'empty'

    def _calculate_naming_quality(self, tree) -> Dict[str, Any]:
        #Analyze variable/method naming quality
        identifiers = []
        single_letter_warnings = []
        unclear_names = []
        unclear_patterns = ['temp', 'tmp', 'data', 'val', 'value', 'info', 'obj', 'list']

        for path, node in tree:
            #Collect variable declarations
            if isinstance(node, javalang.tree.VariableDeclarator):
                if hasattr(node, 'name'):
                    name = node.name
                    identifiers.append(name)

                    if len(name) == 1 and name not in ['i', 'j', 'k', 'x', 'y', 'z']:
                        single_letter_warnings.append(name)

                    if name.lower() in unclear_patterns:
                        unclear_names.append(name)

            #Collect method names
            elif isinstance(node, javalang.tree.MethodDeclaration):
                if hasattr(node, 'name'):
                    name = node.name
                    identifiers.append(name)

                    if name.lower() in unclear_patterns:
                        unclear_names.append(name)

        if not identifiers:
            return {
                'avg_name_length': 0,
                'single_letter_warnings': [],
                'unclear_name_flags': [],
                'sorted_name_lengths': []
            }

        name_lengths = [len(name) for name in identifiers]
        avg_length = sum(name_lengths) / len(name_lengths)

        return {
            'avg_name_length': round(avg_length, 2),
            'single_letter_warnings': list(set(single_letter_warnings)),
            'unclear_name_flags': list(set(unclear_names)),
            'sorted_name_lengths': sorted(name_lengths, reverse=True)[:10]
        }

    def _calculate_nesting_depth(self, tree) -> Dict[str, Any]:
        #Calculate maximum and average nesting depth
        max_depth = 0
        depth_samples = []

        for path, node in tree:
            if isinstance(node, javalang.tree.MethodDeclaration):
                depth = self._get_method_nesting_depth(node)
                max_depth = max(max_depth, depth)
                if depth > 0:
                    depth_samples.append(depth)

        avg_depth = sum(depth_samples) / len(depth_samples) if depth_samples else 0

        return {
            'max_depth': max_depth,
            'avg_depth': round(avg_depth, 2)
        }

    def _get_method_nesting_depth(self, method, current_depth=0) -> int:
        #Calculate nesting depth within a method
        if not hasattr(method, 'body') or not method.body:
            return current_depth

        max_nested = current_depth

        for stmt in method.body:
            if isinstance(stmt, (javalang.tree.IfStatement, javalang.tree.WhileStatement,
                                 javalang.tree.DoStatement, javalang.tree.ForStatement,
                                 javalang.tree.SwitchStatement, javalang.tree.TryStatement)):
                nested_depth = current_depth + 1
                max_nested = max(max_nested, nested_depth)

                # Recursively check nested blocks
                if hasattr(stmt, 'then_statement') and stmt.then_statement:
                    if isinstance(stmt.then_statement, list):
                        for nested in stmt.then_statement:
                            max_nested = max(max_nested, self._get_stmt_depth(nested, nested_depth))

        return max_nested

    def _get_stmt_depth(self, stmt, current_depth) -> int:
        #Get depth of a single statement
        if isinstance(stmt, (javalang.tree.IfStatement, javalang.tree.WhileStatement,
                             javalang.tree.DoStatement, javalang.tree.ForStatement)):
            return current_depth + 1
        return current_depth

    def _calculate_cognitive_complexity(self, tree) -> int:
        
        #Calculate cognitive complexity
        #Weights decision points by nesting level

        cognitive_score = 0

        for path, node in tree:
            if isinstance(node, javalang.tree.MethodDeclaration):
                cognitive_score += self._method_cognitive_complexity(node)

        return cognitive_score

    def _method_cognitive_complexity(self, method, nesting_level=0) -> int:
        score = 0

        if not hasattr(method, 'body') or not method.body:
            return score

        for stmt in method.body:
            if isinstance(stmt, (javalang.tree.IfStatement, javalang.tree.TernaryExpression)):
                score += 1 + nesting_level
            elif isinstance(stmt, (javalang.tree.WhileStatement, javalang.tree.DoStatement,
                                   javalang.tree.ForStatement)):
                score += 1 + nesting_level
            elif isinstance(stmt, javalang.tree.SwitchStatementCase):
                score += 1 + nesting_level
            elif isinstance(stmt, javalang.tree.CatchClause):
                score += 1 + nesting_level

        return score

    def get_thresholds(self) -> Dict[str, Any]:
        return self._thresholds.copy()
