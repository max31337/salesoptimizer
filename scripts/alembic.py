#!/usr/bin/env python3
"""
Alembic migration helper script.
Usage: python migrate.py [alembic_commands]
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get the directory where this script is located (project root)
    script_dir = Path(__file__).parent  # scripts directory
    project_root = script_dir.parent    # project root directory  
    alembic_dir = project_root / "infrastructure" / "db" / "alembic"
    
    # Check if alembic directory exists
    if not alembic_dir.exists():
        print(f"❌ Alembic directory not found: {alembic_dir}")
        sys.exit(1)
    
    # Change to alembic directory
    original_cwd = os.getcwd()
    os.chdir(alembic_dir)
    
    try:
        # Run alembic with all provided arguments
        cmd = ["alembic"] + sys.argv[1:]
        print(f"🚀 Running: {' '.join(cmd)}")
        print(f"📁 In directory: {alembic_dir}")
        
        result = subprocess.run(cmd, capture_output=False)
        sys.exit(result.returncode)
        
    except KeyboardInterrupt:
        print("\n⚠️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        sys.exit(1)
    finally:
        # Always return to original directory
        os.chdir(original_cwd)

if __name__ == "__main__":
    main()