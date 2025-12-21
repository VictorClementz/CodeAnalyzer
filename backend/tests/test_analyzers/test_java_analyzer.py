"""
Tests for JavaAnalyzer.
"""
import pytest
from infrastructure.analyzers.java_analyzer import JavaAnalyzer


class TestJavaAnalyzer:
    """Test the Java code analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create a Java analyzer instance."""
        return JavaAnalyzer()

    def test_simple_method(self, analyzer):
        """Test analysis of a simple Java method."""
        code = """
public class HelloWorld {
    public void sayHello() {
        System.out.println("Hello, World!");
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'java'
        assert results['lines_of_code'] > 0
        assert results['cyclomatic_complexity'] >= 0
        assert 0 <= results['maintainability_index'] <= 100
        assert 0 <= results['readability_score'] <= 100

    def test_complex_control_flow(self, analyzer):
        """Test analysis of complex Java code with control flow."""
        code = """
public class GradeCalculator {
    public String calculateGrade(int score) {
        if (score >= 90) {
            return "A";
        } else if (score >= 80) {
            return "B";
        } else if (score >= 70) {
            return "C";
        } else if (score >= 60) {
            return "D";
        } else {
            return "F";
        }
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
public class NestedLoops {
    public void printGrid() {
        for (int i = 0; i < 10; i++) {
            for (int j = 0; j < 10; j++) {
                if (i == j) {
                    System.out.println(i + ", " + j);
                }
            }
        }
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['max_nesting_depth'] >= 1  # Nested loops detected
        assert results['cognitive_complexity'] > 0

    def test_comments_detection(self, analyzer):
        """Test comment density calculation."""
        code = """
// This is a comment
public class Example {
    // Another comment
    /* Multi-line comment
       spanning multiple lines */
    public int getValue() {
        int x = 1;
        return x;
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['comment_density'] > 0

    def test_naming_quality(self, analyzer):
        """Test naming quality metrics."""
        code = """
public class Example {
    public int myMethod() {
        int veryLongDescriptiveVariableName = 42;
        int x = 1;
        int temp = 2;
        return veryLongDescriptiveVariableName + x + temp;
    }
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
public class DayName {
    public String getDayName(int day) {
        switch(day) {
            case 0:
                return "Sunday";
            case 1:
                return "Monday";
            case 2:
                return "Tuesday";
            default:
                return "Unknown";
        }
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['cyclomatic_complexity'] > 1

    def test_try_catch(self, analyzer):
        """Test try-catch error handling."""
        code = """
public class Example {
    public void riskyOperation() {
        try {
            doSomething();
        } catch (Exception e) {
            handleError(e);
        }
    }

    private void doSomething() {}
    private void handleError(Exception e) {}
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['cyclomatic_complexity'] > 1

    def test_multiple_methods(self, analyzer):
        """Test class with multiple methods."""
        code = """
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }

    public int subtract(int a, int b) {
        return a - b;
    }

    public int multiply(int a, int b) {
        return a * b;
    }

    public int divide(int a, int b) {
        if (b == 0) {
            throw new IllegalArgumentException("Division by zero");
        }
        return a / b;
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['lines_of_code'] > 0
        assert results['cyclomatic_complexity'] > 1

    def test_while_loop(self, analyzer):
        """Test while loop complexity."""
        code = """
public class Example {
    public void processWhile(int n) {
        while (n > 0) {
            System.out.println(n);
            n--;
        }
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['cyclomatic_complexity'] > 1

    def test_all_metrics_present(self, analyzer):
        """Test that all expected metrics are present in results."""
        code = """
public class Sample {
    // A sample method
    public int max(int x, int y) {
        if (x > y) {
            return x;
        } else {
            return y;
        }
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

    def test_interface(self, analyzer):
        """Test interface analysis."""
        code = """
public interface Drawable {
    void draw();
    int getSize();
}

public class Circle implements Drawable {
    public void draw() {
        System.out.println("Drawing circle");
    }

    public int getSize() {
        return 10;
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['lines_of_code'] > 0

    def test_get_thresholds(self, analyzer):
        """Test that analyzer provides Java-specific thresholds."""
        thresholds = analyzer.get_thresholds()

        assert isinstance(thresholds, dict)
        assert thresholds['max_function_length'] == 50
        assert thresholds['max_complexity'] == 12
        assert thresholds['ideal_avg_name_length'] == 15
        assert thresholds['min_comment_density'] == 20

    def test_syntax_error(self, analyzer):
        """Test handling of Java syntax errors."""
        code = """
public class BadClass {
    public void badMethod( {
        System.out.println("Missing closing parenthesis"
"""
        results = analyzer.analyze(code)

        assert 'error' in results
        assert results['language'] == 'java'

    def test_ternary_operator(self, analyzer):
        """Test ternary operator complexity."""
        code = """
public class Example {
    public int abs(int x) {
        return x >= 0 ? x : -x;
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['cyclomatic_complexity'] > 1
