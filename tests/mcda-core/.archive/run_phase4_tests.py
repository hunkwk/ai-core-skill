#!/usr/bin/env python
"""Phase 4 测试运行脚本"""

import sys
import subprocess

# 运行 Phase 4 测试
tests = [
    "tests/mcda-core/test_validation.py",
    "tests/mcda-core/test_reporter.py",
    "tests/mcda-core/test_sensitivity.py",
]

result = subprocess.run(
    [sys.executable, "-m", "pytest"] + tests + ["-v", "--tb=short"],
    capture_output=False,
)

sys.exit(result.returncode)
