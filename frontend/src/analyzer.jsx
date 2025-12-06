// src/Analyzer.jsx - Clean Markup

// ... (imports and helper functions remain the same) ...

function Analyzer() {
    // ... (state and handleAnalyze logic remain the same) ...

    const renderResults = () => {
        if (loading) return <p>Processing analysis...</p>;
        if (error) return <p className="error">🚫 {error}</p>;
        if (!results) return <p>Paste your code snippet above and click "Analyze Code" to evaluate its readability.</p>;

        const score = results.readability_score || 'N/A';
        const complexity = results.cyclomatic_complexity || 'N/A';
        const maintainability = results.maintainability_index || 'N/A';
        const message = results.message || '';

        return (
            <>
                <h3>Analysis Summary</h3>
                <p>
                    <strong>Overall Readability Score:</strong> 
                    <span 
                        className={getScoreClass(score)}
                        style={{ fontSize: '1.4em' }}
                    >
                        {score}/100
                    </span>
                </p>
                <ul>
                    <li><strong>Cyclomatic Complexity (Avg.):</strong> {complexity} (Low is better)</li>
                    <li><strong>Maintainability Index:</strong> {maintainability} ({results.maintainability_rank})</li>
                </ul>
                {message && <p className="message">💡 **Feedback:** {message}</p>}
            </>
        );
    };

    return (
        <div className="container">
            <h1>Code Readability Analyzer</h1>
            <p>A simple, clean tool for developers to objectively evaluate Python code snippets.</p>
            
            <textarea
                className="code-input"
                placeholder="Paste your Python code snippet here..."
                value={codeSnippet}
                onChange={(e) => setCodeSnippet(e.target.value)}
            />

            <button onClick={handleAnalyze} disabled={loading}>
                {loading ? 'Analyzing...' : 'Analyze Code'}
            </button>

            <div className="results">
                {renderResults()}
            </div>
        </div>
    );
}

// ... (export default Analyzer) ...