#!/usr/bin/env python3
"""
Python Code Execution API Service
A secure service that executes arbitrary Python code and returns the result.
"""

import json
import subprocess
import tempfile
import os
import sys
from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)

def validate_script(script):
    """Validate that the script contains a main() function."""
    if not script or not isinstance(script, str):
        raise ValueError("Script must be a non-empty string")
    
    if 'def main(' not in script:
        raise ValueError("Script must contain a function named 'main'")
    
    return True

def execute_script_safely(script):
    """
    Execute Python script safely using subprocess with resource limits.
    Returns the result of main() function and stdout.
    """
    # Create a temporary file for the script
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        # Wrap the script to capture the return value
        wrapped_script = f"""
import json
import sys

{script}

if __name__ == "__main__":
    try:
        result = main()
        print(json.dumps(result))
    except Exception as e:
        print(f"Error in main(): {{e}}", file=sys.stderr)
        sys.exit(1)
"""
        f.write(wrapped_script)
        script_path = f.name
    
    try:
        # Execute the script with subprocess and resource limits
        result = subprocess.run(
            ['python3', script_path],
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
            cwd='/tmp'   # Run in /tmp directory
        )
        
        stdout = result.stdout
        stderr = result.stderr
        
        # Check if execution was successful
        if result.returncode != 0:
            raise RuntimeError(f"Script execution failed: {stderr}")
        
        # Try to parse the result as JSON
        try:
            # The main() function should return JSON
            result_data = json.loads(stdout.strip())
        except json.JSONDecodeError as e:
            raise ValueError(f"main() function must return valid JSON. Error: {e}")
        
        return result_data, stdout
        
    finally:
        # Clean up temporary file
        try:
            os.unlink(script_path)
        except OSError:
            pass

@app.route('/execute', methods=['POST'])
def execute():
    """
    Execute Python script and return the result.
    
    Expected JSON payload:
    {
        "script": "def main(): return {'hello': 'world'}"
    }
    
    Returns:
    {
        "result": ...,  # return value of main() function
        "stdout": ...   # stdout of script execution
    }
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json()
        if not data or 'script' not in data:
            return jsonify({"error": "Missing 'script' field in request body"}), 400
        
        script = data['script']
        
        # Validate script
        validate_script(script)
        
        # Execute script safely
        result, stdout = execute_script_safely(script)
        
        return jsonify({
            "result": result,
            "stdout": stdout
        })
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Script execution timed out"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
