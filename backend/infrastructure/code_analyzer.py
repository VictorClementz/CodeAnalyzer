from radon.raw import analyze

def analyze_code(code, language):
  
    raw_metrics = analyze(code)

    lines_of_code = raw_metrics.sloc #lines of real lines of code
    
    # Return results
    return {
        'lines_of_code': lines_of_code
    }