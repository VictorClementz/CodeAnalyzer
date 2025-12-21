"""
Tests for TypeScriptAnalyzer.
"""
import pytest
from infrastructure.analyzers.typescript_analyzer import TypeScriptAnalyzer


class TestTypeScriptAnalyzer:
    """Test the TypeScript code analyzer."""

    @pytest.fixture
    def analyzer(self):
        """Create a TypeScript analyzer instance."""
        return TypeScriptAnalyzer()

    def test_simple_typed_function(self, analyzer):
        """Test analysis of a simple TypeScript function with types."""
        code = """
function add(a: number, b: number): number {
    return a + b;
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'typescript'
        assert results['lines_of_code'] > 0
        assert results['cyclomatic_complexity'] >= 0

    def test_interface_stripping(self, analyzer):
        """Test that interfaces are stripped correctly."""
        code = """
interface User {
    name: string;
    age: number;
}

function greet(user: User): string {
    return `Hello, ${user.name}!`;
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'typescript'

    def test_type_alias_stripping(self, analyzer):
        """Test that type aliases are stripped correctly."""
        code = """
type ID = string | number;
type Callback = (data: string) => void;

function process(id: ID, callback: Callback): void {
    callback("Processing " + id);
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'typescript'

    def test_class_with_modifiers(self, analyzer):
        """Test classes with TypeScript-specific modifiers."""
        code = """
class Calculator {
    private value: number;

    constructor(initial: number) {
        this.value = initial;
    }

    public add(x: number): number {
        return this.value + x;
    }

    protected subtract(x: number): number {
        return this.value - x;
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'typescript'
        assert results['lines_of_code'] > 0

    def test_generic_types(self, analyzer):
        """Test generic type parameters."""
        code = """
function identity<T>(arg: T): T {
    return arg;
}

class Container<T> {
    private value: T;

    constructor(val: T) {
        this.value = val;
    }

    getValue(): T {
        return this.value;
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'typescript'

    def test_enum_stripping(self, analyzer):
        """Test that enums are stripped correctly."""
        code = """
enum Color {
    Red,
    Green,
    Blue
}

function getColorName(c: Color): string {
    return Color[c];
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'typescript'

    def test_optional_parameters(self, analyzer):
        """Test optional parameters."""
        code = """
function buildName(firstName: string, lastName?: string): string {
    if (lastName) {
        return firstName + " " + lastName;
    }
    return firstName;
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'typescript'
        assert results['cyclomatic_complexity'] > 1

    def test_arrow_function_with_types(self, analyzer):
        """Test arrow functions with type annotations."""
        code = """
const multiply = (a: number, b: number): number => {
    return a * b;
};

const divide = (x: number, y: number): number => x / y;
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'typescript'

    def test_type_assertions(self, analyzer):
        """Test type assertions (as keyword)."""
        code = """
function getLength(obj: any): number {
    return (obj as string).length;
}

const value = getSomething() as number;
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'typescript'

    def test_readonly_modifier(self, analyzer):
        """Test readonly modifier."""
        code = """
class Point {
    readonly x: number;
    readonly y: number;

    constructor(x: number, y: number) {
        this.x = x;
        this.y = y;
    }
}
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'typescript'

    def test_all_metrics_present(self, analyzer):
        """Test that all expected metrics are present in results."""
        code = """
interface Person {
    name: string;
    age: number;
}

function greet(person: Person): string {
    if (person.age >= 18) {
        return `Hello, adult ${person.name}!`;
    } else {
        return `Hello, young ${person.name}!`;
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

    def test_get_thresholds(self, analyzer):
        """Test that analyzer provides TypeScript-specific thresholds."""
        thresholds = analyzer.get_thresholds()

        assert isinstance(thresholds, dict)
        assert thresholds['max_function_length'] == 35
        assert thresholds['max_complexity'] == 8
        assert thresholds['ideal_avg_name_length'] == 10
        assert thresholds['min_comment_density'] == 8

    def test_complex_typescript_features(self, analyzer):
        """Test union types and object spread."""
        code = """
type Status = 'active' | 'inactive' | 'pending';

function updatePerson(person, updates) {
    return { ...person, ...updates };
}

const status: Status = 'active';
"""
        results = analyzer.analyze(code)

        assert 'error' not in results
        assert results['language'] == 'typescript'
