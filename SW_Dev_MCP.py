from fastmcp import FastMCP
from datetime import datetime
import os
import json
import re
import subprocess
from pathlib import Path
from typing import Optional, List
from collections import Counter

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

@mcp.tool
def get_current_time(format: Optional[str] = None) -> str:
    """Get the current date and time.
    
    Args:
        format: Optional datetime format string (e.g., '%Y-%m-%d %H:%M:%S').
                If not provided, returns ISO format.
    """
    if format:
        return datetime.now().strftime(format)
    return datetime.now().isoformat()

@mcp.tool
def read_file_content(file_path: str) -> str:
    """Read the contents of a file.
    
    Args:
        file_path: Path to the file to read.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool
def write_file(file_path: str, content: str, append: bool = False) -> str:
    """Write content to a file.
    
    Args:
        file_path: Path to the file to write.
        content: Content to write to the file.
        append: If True, append to file; otherwise overwrite.
    """
    try:
        mode = 'a' if append else 'w'
        with open(file_path, mode, encoding='utf-8') as f:
            f.write(content)
        return f"Successfully {'appended to' if append else 'wrote'} {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool
def list_directory(path: str = ".") -> str:
    """List files and directories in a given path.
    
    Args:
        path: Directory path to list (defaults to current directory).
    """
    try:
        items = []
        for item in Path(path).iterdir():
            item_type = "DIR" if item.is_dir() else "FILE"
            size = item.stat().st_size if item.is_file() else 0
            items.append(f"{item_type:4} {size:10} {item.name}")
        return "\n".join(items) if items else "Directory is empty"
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@mcp.tool
def get_environment_variable(name: str) -> str:
    """Get the value of an environment variable.
    
    Args:
        name: Name of the environment variable.
    """
    value = os.getenv(name)
    return value if value is not None else f"Environment variable '{name}' not found"

@mcp.tool
def format_json(data: str, indent: int = 2) -> str:
    """Format a JSON string with proper indentation.
    
    Args:
        data: JSON string to format.
        indent: Number of spaces for indentation (default: 2).
    """
    try:
        parsed = json.loads(data)
        return json.dumps(parsed, indent=indent)
    except Exception as e:
        return f"Error formatting JSON: {str(e)}"

@mcp.tool
def calculate(expression: str) -> str:
    """Safely evaluate a simple mathematical expression.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5').
    """
    try:
        # Only allow basic math operations for safety
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters"
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"Error calculating: {str(e)}"

@mcp.tool
def get_system_info() -> str:
    """Get basic system information."""
    info = {
        "platform": os.name,
        "current_directory": os.getcwd(),
        "home_directory": os.path.expanduser("~"),
    }
    return json.dumps(info, indent=2)

@mcp.tool
def search_code(pattern: str, directory: str = ".", file_extensions: Optional[str] = None) -> str:
    """Search for a pattern in code files (like grep).
    
    Args:
        pattern: Regular expression pattern to search for.
        directory: Directory to search in (defaults to current directory).
        file_extensions: Comma-separated file extensions to search (e.g., "py,js,ts").
                        If None, searches all text files.
    """
    try:
        results = []
        path = Path(directory)
        extensions = [ext.strip() for ext in file_extensions.split(",")] if file_extensions else None
        
        for file_path in path.rglob("*"):
            if file_path.is_file():
                if extensions and file_path.suffix[1:] not in extensions:
                    continue
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                results.append(f"{file_path}:{line_num}: {line.strip()}")
                except:
                    continue
        
        if results:
            return "\n".join(results[:100])  # Limit to 100 results
        return f"No matches found for pattern '{pattern}'"
    except Exception as e:
        return f"Error searching code: {str(e)}"

@mcp.tool
def find_files(pattern: str, directory: str = ".") -> str:
    """Find files matching a pattern (glob or regex).
    
    Args:
        pattern: File name pattern to search for (supports * wildcards).
        directory: Directory to search in (defaults to current directory).
    """
    try:
        path = Path(directory)
        matches = []
        for file_path in path.rglob(pattern):
            if file_path.is_file():
                matches.append(str(file_path))
        return "\n".join(matches) if matches else f"No files found matching '{pattern}'"
    except Exception as e:
        return f"Error finding files: {str(e)}"

@mcp.tool
def count_lines_of_code(directory: str = ".", file_extensions: Optional[str] = None) -> str:
    """Count lines of code in a directory.
    
    Args:
        directory: Directory to analyze (defaults to current directory).
        file_extensions: Comma-separated file extensions to count (e.g., "py,js,ts").
                        If None, counts all text files.
    """
    try:
        path = Path(directory)
        extensions = [ext.strip() for ext in file_extensions.split(",")] if file_extensions else None
        stats = Counter()
        total_lines = 0
        total_files = 0
        
        for file_path in path.rglob("*"):
            if file_path.is_file():
                if extensions and file_path.suffix[1:] not in extensions:
                    continue
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = sum(1 for _ in f)
                        ext = file_path.suffix[1:] or "no extension"
                        stats[ext] += lines
                        total_lines += lines
                        total_files += 1
                except:
                    continue
        
        result = {
            "total_files": total_files,
            "total_lines": total_lines,
            "by_extension": dict(stats)
        }
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error counting lines: {str(e)}"

@mcp.tool
def find_todos(directory: str = ".") -> str:
    """Find TODO, FIXME, and NOTE comments in code.
    
    Args:
        directory: Directory to search in (defaults to current directory).
    """
    try:
        todos = []
        path = Path(directory)
        pattern = re.compile(r'(TODO|FIXME|NOTE|XXX|HACK):\s*(.+)', re.IGNORECASE)
        
        for file_path in path.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            match = pattern.search(line)
                            if match:
                                todos.append(f"{file_path}:{line_num} - {match.group(1).upper()}: {match.group(2).strip()}")
                except:
                    continue
        
        return "\n".join(todos) if todos else "No TODOs/FIXMEs found"
    except Exception as e:
        return f"Error finding TODOs: {str(e)}"

@mcp.tool
def git_status(directory: str = ".") -> str:
    """Get git status for a repository.
    
    Args:
        directory: Git repository directory (defaults to current directory).
    """
    try:
        result = subprocess.run(
            ['git', 'status', '--short'],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout if result.stdout.strip() else "Working tree clean"
        return f"Error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out"
    except FileNotFoundError:
        return "Error: Git not found. Is git installed?"
    except Exception as e:
        return f"Error getting git status: {str(e)}"

@mcp.tool
def git_log(count: int = 10, directory: str = ".") -> str:
    """Get recent git commit history.
    
    Args:
        count: Number of commits to show (default: 10).
        directory: Git repository directory (defaults to current directory).
    """
    try:
        result = subprocess.run(
            ['git', 'log', f'-{count}', '--oneline', '--decorate'],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout if result.stdout.strip() else "No commits found"
        return f"Error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out"
    except FileNotFoundError:
        return "Error: Git not found. Is git installed?"
    except Exception as e:
        return f"Error getting git log: {str(e)}"

@mcp.tool
def validate_json(json_string: str) -> str:
    """Validate if a string is valid JSON.
    
    Args:
        json_string: JSON string to validate.
    """
    try:
        json.loads(json_string)
        return "Valid JSON"
    except json.JSONDecodeError as e:
        return f"Invalid JSON: {str(e)}"

@mcp.tool
def get_file_stats(file_path: str) -> str:
    """Get statistics about a file (lines, words, characters, size).
    
    Args:
        file_path: Path to the file to analyze.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found"
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            words = content.split()
            
        stats = {
            "file": str(path),
            "size_bytes": path.stat().st_size,
            "lines": len(lines),
            "words": len(words),
            "characters": len(content),
            "non_empty_lines": len([l for l in lines if l.strip()]),
            "extension": path.suffix
        }
        return json.dumps(stats, indent=2)
    except Exception as e:
        return f"Error getting file stats: {str(e)}"

@mcp.tool
def find_duplicate_lines(file_path: str, min_length: int = 10) -> str:
    """Find duplicate lines in a file.
    
    Args:
        file_path: Path to the file to analyze.
        min_length: Minimum line length to consider (default: 10).
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found"
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.rstrip() for line in f if len(line.strip()) >= min_length]
        
        line_counts = Counter(lines)
        duplicates = {line: count for line, count in line_counts.items() if count > 1}
        
        if duplicates:
            result = []
            for line, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True):
                result.append(f"({count}x) {line[:80]}...")
            return "\n".join(result[:20])  # Limit to top 20
        return "No duplicate lines found"
    except Exception as e:
        return f"Error finding duplicates: {str(e)}"

@mcp.tool
def extract_imports(file_path: str) -> str:
    """Extract import statements from a code file.
    
    Args:
        file_path: Path to the code file.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return f"Error: File '{file_path}' not found"
        
        imports = []
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                # Python imports
                if re.match(r'^(import |from .+ import )', line.strip()):
                    imports.append(line.strip())
                # JavaScript/TypeScript imports
                elif re.match(r'^(import |const .+ = require\(|var .+ = require\()', line.strip()):
                    imports.append(line.strip())
        
        return "\n".join(imports) if imports else "No imports found"
    except Exception as e:
        return f"Error extracting imports: {str(e)}"

@mcp.tool
def generate_uuid() -> str:
    """Generate a UUID (Universally Unique Identifier)."""
    import uuid
    return str(uuid.uuid4())

@mcp.tool
def base64_encode(text: str) -> str:
    """Encode text to base64.
    
    Args:
        text: Text to encode.
    """
    import base64
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

@mcp.tool
def base64_decode(encoded: str) -> str:
    """Decode base64 text.
    
    Args:
        encoded: Base64 encoded string to decode.
    """
    import base64
    try:
        return base64.b64decode(encoded).decode('utf-8')
    except Exception as e:
        return f"Error decoding: {str(e)}"

if __name__ == "__main__":
    mcp.run()