
import ast


def analyze_code(code):
    """
    Analyze Python source code and return detected issues.

    Each finding contains:
    type, severity, line, message, suggestion
    """

    findings = []

    # Validate input
    if not isinstance(code, str):
        return [{
            "type": "Input Error",
            "severity": "High",
            "line": 1,
            "message": "The submitted code must be a string.",
            "suggestion": "Upload a valid Python (.py) file."
        }]

    if not code.strip():
        return [{
            "type": "Input Error",
            "severity": "Medium",
            "line": 1,
            "message": "The uploaded Python file is empty.",
            "suggestion": "Add Python code before running the analysis."
        }]

    # Step 1: Check Python syntax
    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        return [{
            "type": "Syntax Error",
            "severity": "High",
            "line": error.lineno or 1,
            "message": error.msg,
            "suggestion": "Correct the Python syntax on this line."
        }]

    # Step 2: Analyze code using AST
    for node in ast.walk(tree):

        # Detect eval() and exec()
        if isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                if node.func.id == "eval":
                    findings.append({
                        "type": "Security Risk",
                        "severity": "High",
                        "line": node.lineno,
                        "message": "Use of eval() detected.",
                        "suggestion": (
                            "Avoid eval() when processing untrusted input. "
                            "Use safer alternatives such as ast.literal_eval()."
                        )
                    })

                elif node.func.id == "exec":
                    findings.append({
                        "type": "Security Risk",
                        "severity": "High",
                        "line": node.lineno,
                        "message": "Use of exec() detected.",
                        "suggestion": (
                            "Avoid executing dynamically supplied code. "
                            "Use predefined functions instead."
                        )
                    })

        # Detect bare except blocks
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                findings.append({
                    "type": "Code Quality",
                    "severity": "Medium",
                    "line": node.lineno,
                    "message": "Bare except block detected.",
                    "suggestion": (
                        "Catch a specific exception instead of using "
                        "a bare except block."
                    )
                })

        # Detect mutable default arguments
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

            defaults = list(node.args.defaults)
            defaults.extend(
                default
                for default in node.args.kw_defaults
                if default is not None
            )

            for default in defaults:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    findings.append({
                        "type": "Potential Bug",
                        "severity": "Medium",
                        "line": node.lineno,
                        "message": "Mutable default argument detected.",
                        "suggestion": (
                            "Use None as the default value and create "
                            "the mutable object inside the function."
                        )
                    })
                    break

    # Step 3: Sort findings by line number
    findings.sort(key=lambda item: item["line"])

    return findings
