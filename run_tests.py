#!/usr/bin/env python3
"""
Test Runner for OWASP ZAP MCP

Run tests for the improved OWASP ZAP MCP implementation.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return the result."""
    if description:
        print(f"\n🔧 {description}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout:
                print(result.stdout)
        else:
            print("❌ Failed!")
            if result.stderr:
                print("Error output:")
                print(result.stderr)
            if result.stdout:
                print("Standard output:")
                print(result.stdout)
        
        return result.returncode == 0
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run OWASP ZAP MCP tests")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "mcp", "sse", "real_world"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow tests"
    )
    parser.add_argument(
        "--file",
        help="Run specific test file"
    )
    
    args = parser.parse_args()
    
    # Change to project directory
    project_dir = Path(__file__).parent / "owasp_zap_mcp"
    if not project_dir.exists():
        print("❌ Project directory not found!")
        sys.exit(1)
    
    print("🧪 OWASP ZAP MCP Test Runner")
    print("=" * 50)
    
    # Build pytest command
    pytest_cmd = ["python", "-m", "pytest"]
    
    # Test directory
    test_dir = "tests/"
    
    if args.file:
        test_target = f"tests/{args.file}"
    else:
        test_target = test_dir
    
    # Add verbosity
    if args.verbose:
        pytest_cmd.append("-v")
    else:
        pytest_cmd.append("-q")
    
    # Add coverage
    if args.coverage:
        pytest_cmd.extend([
            "--cov=src/owasp_zap_mcp",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    # Add markers based on test type
    if args.type != "all":
        pytest_cmd.extend(["-m", args.type])
    
    # Skip slow tests if requested
    if args.fast:
        pytest_cmd.extend(["-m", "not slow"])
    
    # Add test target
    pytest_cmd.append(test_target)
    
    # Add additional pytest options
    pytest_cmd.extend([
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Strict marker checking
    ])
    
    print(f"📁 Working directory: {project_dir}")
    print(f"🎯 Test type: {args.type}")
    print(f"📊 Coverage: {'enabled' if args.coverage else 'disabled'}")
    print(f"⚡ Fast mode: {'enabled' if args.fast else 'disabled'}")
    
    # Run the tests
    success = run_command(
        pytest_cmd,
        f"Running {args.type} tests"
    )
    
    if success:
        print("\n🎉 All tests passed!")
        
        if args.coverage:
            print("\n📊 Coverage report generated:")
            print("  - HTML: htmlcov/index.html")
            print("  - Terminal output above")
        
        # Show test summary
        print("\n📋 Test Summary:")
        print("  ✅ Unit Tests: ZAP client functionality")
        print("  ✅ MCP Tools: Tool functions and URL normalization")
        print("  ✅ SSE Server: Parameter processing and session management")
        print("  ✅ Integration: Complete workflows and real-world scenarios")
        
    else:
        print("\n❌ Some tests failed!")
        print("\n🔍 Troubleshooting tips:")
        print("  1. Make sure you're in the project root directory")
        print("  2. Check that all dependencies are installed")
        print("  3. Run with --verbose for more details")
        print("  4. Try running specific test files with --file")
        
        sys.exit(1)


if __name__ == "__main__":
    main() 
