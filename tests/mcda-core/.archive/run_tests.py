#!/usr/bin/env python
"""运行测试并显示结果"""
import sys
import subprocess

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/mcda-core/test_validation.py",
     "tests/mcda-core/test_reporter.py", "tests/mcda-core/test_sensitivity.py",
     "-v", "--tb=short"],
    capture_output=False,
)

sys.exit(result.returncode)
