"""Script to run different test suites."""

import subprocess
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def run_command(command: str) -> int:
    """Run command and return exit code."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=project_root)
    return result.returncode


def run_unit_tests() -> int:
    """Run unit tests."""
    print("🧪 Running unit tests...")
    return run_command("pytest tests/test_domain tests/test_application -v")


def run_infrastructure_tests() -> int:
    """Run infrastructure tests."""
    print("🔧 Running infrastructure tests...")
    return run_command("pytest tests/test_infrastructure -v")


def run_api_tests() -> int:
    """Run API tests."""
    print("🌐 Running API tests...")
    return run_command("pytest tests/test_api -v")


def run_integration_tests() -> int:
    """Run integration tests."""
    print("🔗 Running integration tests...")
    return run_command("pytest tests/test_integration -v -m integration")


def run_all_tests() -> int:
    """Run all tests."""
    print("🚀 Running all tests...")
    return run_command("pytest tests/ -v")


def run_coverage() -> int:
    """Run tests with coverage report."""
    print("📊 Running tests with coverage...")
    return run_command("pytest tests/ --cov=domain --cov=application --cov=infrastructure --cov=api --cov-report=html --cov-report=term")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_tests.py [unit|infrastructure|api|integration|all|coverage]")
        sys.exit(1)
    
    test_type = sys.argv[1].lower()
    
    if test_type == "unit":
        exit_code = run_unit_tests()
    elif test_type == "infrastructure":
        exit_code = run_infrastructure_tests()
    elif test_type == "api":
        exit_code = run_api_tests()
    elif test_type == "integration":
        exit_code = run_integration_tests()
    elif test_type == "all":
        exit_code = run_all_tests()
    elif test_type == "coverage":
        exit_code = run_coverage()
    else:
        print(f"Unknown test type: {test_type}")
        exit_code = 1
    
    sys.exit(exit_code)