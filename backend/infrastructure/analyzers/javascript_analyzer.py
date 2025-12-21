
#JavaScript code analyzer using Esprima AST parser.


import esprima
from typing import Dict, Any, List, Set
from .base_analyzer import BaseAnalyzer
from ..scoring import calculate_readability_score
from ..config.thresholds import get_language_config


class JavaScriptAnalyzer(BaseAnalyzer):
    def __init__(self):
        self.language = 'javascript'
        self._thresholds = get_language_config('javascript')

    def analyze(self, code: str) -> Dict[str, Any]:
        try:
            # Parse JavaScript code into AST
            tree = esprima.parseScript(code, {
                'loc': True,
                'range': True,
                'comment': True,
                'tokens': True
            })

            # Calculate all metrics
            lines_of_code = self._count_sloc(code)
            complexity_result = self._calculate_complexity(tree)
            maintainability = self._calculate_maintainability(
                lines_of_code,
                complexity_result['total_complexity'],
                complexity_result['function_count']
            )
            comment_density = self._calculate_comment_density(tree, code)
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

        except Exception as e:
            return {
                'error': f'JavaScript analysis failed: {str(e)}',
                'lines_of_code': len([l for l in code.split('\n') if l.strip()]),
                'language': self.language
            }

    def _count_sloc(self, code: str) -> int:
        #Count Source Lines of Code
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
        function_count = 0

        def visit_node(node):
            nonlocal complexity_sum, function_count

            if not hasattr(node, 'type'):
                return

            # Count functions
            if node.type in ['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression']:
                function_count += 1
                complexity_sum += 1  # Base complexity

            # Count decision points
            elif node.type in ['IfStatement', 'ConditionalExpression']:
                complexity_sum += 1
            elif node.type in ['WhileStatement', 'DoWhileStatement', 'ForStatement', 'ForInStatement', 'ForOfStatement']:
                complexity_sum += 1
            elif node.type == 'SwitchCase' and node.test is not None:  # Each case adds complexity
                complexity_sum += 1
            elif node.type == 'LogicalExpression' and node.operator in ['&&', '||']:
                complexity_sum += 1
            elif node.type == 'CatchClause':
                complexity_sum += 1

            # Recursively visit child nodes
            for key, value in node.__dict__.items():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, 'type'):
                            visit_node(item)
                elif hasattr(value, 'type'):
                    visit_node(value)

        visit_node(tree)

        avg_complexity = round(complexity_sum / max(function_count, 1), 2)

        return {
            'total_complexity': complexity_sum,
            'function_count': function_count,
            'avg_complexity': avg_complexity
        }

    def _calculate_maintainability(self, lines: int, complexity: int, function_count: int) -> float:
        # Simplified Halstead volume estimation
        volume = (lines + function_count) * 2.4  # Rough approximation

        # Maintainability Index formula (simplified)
        # MI = max(0, (171 - 5.2 * ln(V) - 0.23 * G - 16.2 * ln(LOC)) * 100 / 171)
        import math

        if volume <= 0 or lines <= 0:
            return 100

        try:
            mi = 171 - 5.2 * math.log(volume) - 0.23 * complexity - 16.2 * math.log(lines)
            mi = max(0, (mi * 100) / 171)
            return round(min(100, mi), 2)
        except:
            return 50  # Default moderate score on calculation error

    def _calculate_comment_density(self, tree, code: str) -> float:
        if not hasattr(tree, 'comments') or not tree.comments:
            return 0.0

        total_lines = len(code.split('\n'))
        if total_lines == 0:
            return 0.0

        comment_lines = 0
        for comment in tree.comments:
            if comment.type == 'Line':
                comment_lines += 1
            elif comment.type == 'Block':
                # Count lines in block comment
                comment_text = comment.value if comment.value else ''
                comment_lines += len(comment_text.split('\n'))

        density = (comment_lines / total_lines) * 100
        return round(density, 2)

    def _calculate_function_lengths(self, tree) -> Dict[str, Any]:
        function_lengths = []

        def visit_node(node):
            if not hasattr(node, 'type'):
                return

            # Check for function declarations/expressions
            if node.type in ['FunctionDeclaration', 'FunctionExpression', 'ArrowFunctionExpression']:
                if hasattr(node, 'loc') and node.loc:
                    start_line = node.loc.start.line
                    end_line = node.loc.end.line
                    length = end_line - start_line + 1
                    function_lengths.append(length)

            # Recursively visit children
            for key, value in node.__dict__.items():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, 'type'):
                            visit_node(item)
                elif hasattr(value, 'type'):
                    visit_node(value)

        visit_node(tree)

        if not function_lengths:
            return {'avg': 0, 'max': 0}

        return {
            'avg': round(sum(function_lengths) / len(function_lengths), 2),
            'max': max(function_lengths)
        }

    def _calculate_duplication(self, tree) -> Dict[str, Any]:
        #duplication detection
        statement_blocks = []

        def extract_blocks(node, depth=0):
            if not hasattr(node, 'type'):
                return

            # Extract blocks of statements
            if hasattr(node, 'body') and isinstance(node.body, list):
                if len(node.body) >= 3:  # At least 3 statements to consider duplication
                    block_signature = self._create_block_signature(node.body[:3])
                    statement_blocks.append(block_signature)

            # Recursively visit children
            for key, value in node.__dict__.items():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, 'type'):
                            extract_blocks(item, depth + 1)
                elif hasattr(value, 'type'):
                    extract_blocks(value, depth + 1)

        extract_blocks(tree)

        # Find duplicates
        duplicates = []
        seen = {}
        for i, signature in enumerate(statement_blocks):
            if signature in seen:
                duplicates.append({'block': i, 'duplicate_of': seen[signature]})
            else:
                seen[signature] = i

        total_blocks = len(statement_blocks)
        duplicate_count = len(duplicates)

        percentage = (duplicate_count / max(total_blocks, 1)) * 100 if total_blocks > 0 else 0

        return {
            'percentage': round(percentage, 2),
            'blocks': duplicates
        }

    def _create_block_signature(self, statements: List) -> str:
        signature_parts = []
        for stmt in statements:
            if hasattr(stmt, 'type'):
                signature_parts.append(stmt.type)
        return '-'.join(signature_parts)

    def _calculate_naming_quality(self, tree) -> Dict[str, Any]:
        identifiers = []
        single_letter_warnings = []
        unclear_names = []
        unclear_patterns = ['temp', 'tmp', 'data', 'val', 'value', 'info', 'item']

        def visit_node(node):
            if not hasattr(node, 'type'):
                return

            # Collect identifier names
            if node.type == 'Identifier' and hasattr(node, 'name') and node.name:
                name = node.name
                identifiers.append(name)

                # Check for single-letter names (excluding common loop variables)
                if len(name) == 1 and name not in ['i', 'j', 'k', 'x', 'y', 'z']:
                    single_letter_warnings.append(name)

                # Check for unclear names
                if name.lower() in unclear_patterns:
                    unclear_names.append(name)

            # Recursively visit children
            for key, value in node.__dict__.items():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, 'type'):
                            visit_node(item)
                elif hasattr(value, 'type'):
                    visit_node(value)

        visit_node(tree)

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
        """Calculate maximum and average nesting depth."""
        max_depth = 0
        depth_samples = []

        def visit_node(node, current_depth=0):
            nonlocal max_depth

            if not hasattr(node, 'type'):
                return

            # Track nesting depth for control structures
            if node.type in ['IfStatement', 'WhileStatement', 'DoWhileStatement', 'ForStatement',
                             'ForInStatement', 'ForOfStatement', 'SwitchStatement', 'TryStatement']:
                current_depth += 1
                max_depth = max(max_depth, current_depth)
                depth_samples.append(current_depth)

            # Recursively visit children
            for key, value in node.__dict__.items():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, 'type'):
                            visit_node(item, current_depth)
                elif hasattr(value, 'type'):
                    visit_node(value, current_depth)

        visit_node(tree)

        avg_depth = sum(depth_samples) / len(depth_samples) if depth_samples else 0

        return {
            'max_depth': max_depth,
            'avg_depth': round(avg_depth, 2)
        }

    def _calculate_cognitive_complexity(self, tree) -> int:
        """
        Calculate cognitive complexity.

        Weights decision points by nesting level to measure mental burden.
        """
        cognitive_score = 0

        def visit_node(node, nesting_level=0):
            nonlocal cognitive_score

            if not hasattr(node, 'type'):
                return

            # Increment for control flow structures, weighted by nesting
            if node.type in ['IfStatement', 'ConditionalExpression']:
                cognitive_score += 1 + nesting_level
                nesting_level += 1
            elif node.type in ['WhileStatement', 'DoWhileStatement', 'ForStatement',
                               'ForInStatement', 'ForOfStatement']:
                cognitive_score += 1 + nesting_level
                nesting_level += 1
            elif node.type == 'SwitchCase' and node.test is not None:
                cognitive_score += 1 + nesting_level
            elif node.type == 'LogicalExpression':
                cognitive_score += 1
            elif node.type == 'CatchClause':
                cognitive_score += 1 + nesting_level
                nesting_level += 1

            # Recursively visit children
            for key, value in node.__dict__.items():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, 'type'):
                            visit_node(item, nesting_level)
                elif hasattr(value, 'type'):
                    visit_node(value, nesting_level)

        visit_node(tree)

        return cognitive_score

    def get_thresholds(self) -> Dict[str, Any]:
        """
        Get JavaScript-specific thresholds and configuration.

        Returns:
            Dictionary containing JavaScript-specific thresholds
        """
        return self._thresholds.copy()
