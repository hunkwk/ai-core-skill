#!/usr/bin/env python
"""运行 Phase 5 测试"""
import sys
import subprocess

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/mcda-core/test_utils.py",
     "tests/mcda-core/test_integration.py", "tests/mcda-core/test_cli.py",
     "-v", "--tb=short"],
    capture_output=False,
)

sys.exit(result.returncode)
