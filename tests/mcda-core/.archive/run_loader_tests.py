"""运行测试脚本"""
import sys
import pytest

if __name__ == "__main__":
    sys.exit(pytest.main([
        "tests/mcda-core/test_loaders/test_loaders.py",
        "-v",
        "--tb=short"
    ]))
