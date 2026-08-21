html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #2980b9;
            margin-top: 30px;
        }
        h3 {
            color: #16a085;
            margin-top: 20px;
        }
        ul {
            padding-left: 20px;
        }
        li {
            margin-bottom: 8px;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 4px;
            font-family: monospace;
        }
        .metadata {
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin-top: 40px;
        }
    </style>
</head>
<body>
    <h1>JavaScript Reference Summary</h1>
    <p>The <strong>JavaScript Reference</strong> serves as a comprehensive repository of facts about the JavaScript language. It is designed to be <strong>environment-agnostic</strong>, covering usage in browsers, servers, and other contexts without targeting a specific platform.</p>

    <h2>📚 Structure and Content</h2>
    
    <h3>For Beginners</h3>
    <ul>
        <li><strong>Getting Started</strong>: New users are directed to a specific <strong>guide</strong> to learn fundamentals before diving into the detailed reference.</li>
    </ul>

    <h3>Core Reference Sections</h3>
    <ul>
        <li><strong>Built-ins</strong>: Covers standard objects, methods, and properties, including:
            <ul>
                <li>Value and Function properties</li>
                <li>Fundamental and Error objects</li>
                <li>Numbers, dates, and text processing</li>
                <li>Indexed and Keyed collections</li>
                <li>Structured data and memory management</li>
                <li>Control abstraction, reflection, and internationalization</li>
            </ul>
        </li>
        <li><strong>Statements</strong>: Details on control flow, variable declarations, functions, classes, and iterations.</li>
        <li><strong>Expressions and Operators</strong>: A complete breakdown of:
            <ul>
                <li>Primary and Left-hand-side expressions</li>
                <li>Increment, decrement, and unary operators</li>
                <li>Arithmetic, relational, and equality operators</li>
                <li>Bitwise, logical, and conditional (ternary) operators</li>
                <li>Assignment, yield, spread, and comma operators</li>
            </ul>
        </li>
        <li><strong>Advanced Topics</strong>: Dedicated sections for <strong>Functions</strong>, <strong>Classes</strong>, and <strong>Regular expressions</strong>.</li>
    </ul>

    <div class="metadata">
        <h2>📝 Metadata</h2>
        <ul>
            <li><strong>Source</strong>: MDN (Mozilla Developer Network)</li>
            <li><strong>Last Modified</strong>: May 22, 2026</li>
            <li><strong>Contributors</strong>: MDN community</li>
        </ul>
    </div>

    <p>This reference is intended to be the go-to resource for developers needing precise details on individual language constructs while writing code.</p>
</body>
</html>
"""

with open("javascript_reference_summary.html", "w") as f:
    f.write(html_content)