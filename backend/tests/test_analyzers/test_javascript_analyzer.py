"""
Tests for JavaScriptAnalyzer.
"""
import pytest
from infrastructure.analyzers.javascript_analyzer import JavaScriptAnalyzer


class TestJavaScriptAnalyzer:
    """Test the JavaScript code analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create a JavaScript analyzer instance."""
        return JavaScriptAnalyzer()

    def test_simple_function(self, analyzer):
        """Test analysis of a simple JavaScript function."""
        code = """
function helloWorld() {
    console.log("Hello, World!");
    return true;
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'javascript'
        assert results['lines_of_code'] > 0
        assert results['cyclomatic_complexity'] >= 0
        assert 0 <= results['maintainability_index'] <= 100
        assert 0 <= results['readability_score'] <= 100

    def test_arrow_function(self, analyzer):
        """Test analysis of arrow functions."""
        code = """
const add = (a, b) => {
    return a + b;
};

const multiply = (x, y) => x * y;
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'javascript'
        assert results['cyclomatic_complexity'] >= 0

    def test_complex_control_flow(self, analyzer):
        """Test analysis of complex JavaScript code with control flow."""
        code = """
function calculateGrade(score) {
    if (score >= 90) {
        return 'A';
    } else if (score >= 80) {
        return 'B';
    } else if (score >= 70) {
        return 'C';
    } else if (score >= 60) {
        return 'D';
    } else {
        return 'F';
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['cyclomatic_complexity'] > 1
        assert results['max_nesting_depth'] >= 1

    def test_nested_loops(self, analyzer):
        """Test analysis of nested loops."""
        code = """
function nestedLoops() {
    for (let i = 0; i < 10; i++) {
        for (let j = 0; j < 10; j++) {
            if (i === j) {
                console.log(i, j);
            }
        }
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['max_nesting_depth'] >= 2
        assert results['cognitive_complexity'] > 0

    def test_comments_detection(self, analyzer):
        """Test comment density calculation."""
        code = """
// This is a comment
function foo() {
    // Another comment
    /* Block comment
       spanning multiple lines */
    const x = 1;
    return x;
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['comment_density'] > 0

    def test_naming_quality(self, analyzer):
        """Test naming quality metrics."""
        code = """
function myFunction() {
    const veryLongDescriptiveVariableName = 42;
    const x = 1;
    const temp = 2;
    return veryLongDescriptiveVariableName + x + temp;
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['avg_name_length'] > 0
        assert isinstance(results['single_letter_warnings'], list)
        assert isinstance(results['unclear_name_flags'], list)

    def test_switch_statement(self, analyzer):
        """Test analysis of switch statements."""
        code = """
function getDayName(day) {
    switch(day) {
        case 0:
            return 'Sunday';
        case 1:
            return 'Monday';
        case 2:
            return 'Tuesday';
        default:
            return 'Unknown';
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['cyclomatic_complexity'] > 1

    def test_logical_operators(self, analyzer):
        """Test that logical operators add to complexity."""
        code = """
function validate(x, y, z) {
    if (x && y || z) {
        return true;
    }
    return false;
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['cyclomatic_complexity'] > 1

    def test_try_catch(self, analyzer):
        """Test try-catch error handling."""
        code = """
function riskyOperation() {
    try {
        doSomething();
    } catch (error) {
        handleError(error);
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['cyclomatic_complexity'] > 1

    def test_all_metrics_present(self, analyzer):
        """Test that all expected metrics are present in results."""
        code = """
function sampleFunction(x, y) {
    // A sample function
    if (x > y) {
        return x;
    } else {
        return y;
    }
}
"""
        results = analyzer.analyze(code)

        expected_metrics = [
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
            'language'
        ]

        for metric in expected_metrics:
            assert metric in results, f"Missing metric: {metric}"

    def test_es6_features(self, analyzer):
        """Test analysis of ES6 features."""
        code = """
const numbers = [1, 2, 3, 4, 5];
const doubled = numbers.map(n => n * 2);
const evens = numbers.filter(n => n % 2 === 0);

class Calculator {
    add(a, b) {
        return a + b;
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['lines_of_code'] > 0

    def test_get_thresholds(self, analyzer):
        """Test that analyzer provides JavaScript-specific thresholds."""
        thresholds = analyzer.get_thresholds()

        assert isinstance(thresholds, dict)
        assert thresholds['max_function_length'] == 30
        assert thresholds['max_complexity'] == 8
        assert thresholds['ideal_avg_name_length'] == 8
        assert thresholds['min_comment_density'] == 10

    def test_syntax_error(self, analyzer):
        """Test handling of JavaScript syntax errors."""
        code = """
function badFunction( {
    console.log("Missing closing parenthesis"
"""
        results = analyzer.analyze(code)

        assert 'error' in results
        assert results['language'] == 'javascript'
