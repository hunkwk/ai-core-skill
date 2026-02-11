"""
性能测量工具单元测试
"""

import pytest
import time
from pathlib import Path
import sys

# 添加 mcda_core 到路径
mcda_core_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "scripts"
if str(mcda_core_path) not in sys.path:
    sys.path.insert(0, str(mcda_core_path))

from performance.utils import measure_execution_time, PerformanceCriteria, generate_performance_report


class TestMeasureExecutionTime:
    """测试 measure_execution_time 函数"""

    def test_measure_simple_function(self):
        """测试简单函数的执行时间测量"""
        def simple_function():
            return 42

        result = measure_execution_time(simple_function)

        assert 'execution_time' in result
        assert 'result' in result
        assert 'memory_mb' in result
        assert 'memory_peak_mb' in result
        assert result['result'] == 42
        assert result['execution_time'] >= 0

    def test_measure_function_with_args(self):
        """测试带参数函数的执行时间测量"""
        def add(a, b):
            return a + b

        result = measure_execution_time(add, 2, 3)

        assert result['result'] == 5
        assert result['execution_time'] >= 0

    def test_measure_function_with_delay(self):
        """测试带延迟函数的执行时间测量"""
        def delayed_function():
            time.sleep(0.1)
            return "done"

        result = measure_execution_time(delayed_function)

        assert result['result'] == "done"
        assert result['execution_time'] >= 0.1
        assert result['execution_time'] < 1.0  # 应该在合理范围内


class TestPerformanceCriteria:
    """测试 PerformanceCriteria 类"""

    def test_small_scale_criteria(self):
        """测试小规模性能标准"""
        criteria = PerformanceCriteria.check_performance(
            category='small',
            alternatives=10,
            criteria=5,
            exec_time=0.3,
            memory_mb=30
        )

        assert criteria['response_time_ok'] == True
        assert criteria['memory_ok'] == True
        assert criteria['category'] == 'small'
        assert criteria['time_limit'] == 0.5
        assert criteria['memory_limit'] == 50

    def test_medium_scale_criteria_pass(self):
        """测试中规模性能标准（通过）"""
        criteria = PerformanceCriteria.check_performance(
            category='medium',
            alternatives=50,
            criteria=20,
            exec_time=1.5,
            memory_mb=150
        )

        assert criteria['response_time_ok'] == True
        assert criteria['memory_ok'] == True

    def test_medium_scale_criteria_fail_time(self):
        """测试中规模性能标准（时间超限）"""
        criteria = PerformanceCriteria.check_performance(
            category='medium',
            alternatives=50,
            criteria=20,
            exec_time=3.0,  # 超过 2s 限制
            memory_mb=150
        )

        assert criteria['response_time_ok'] == False
        assert criteria['memory_ok'] == True

    def test_large_scale_criteria_fail_memory(self):
        """测试大规模性能标准（内存超限）"""
        criteria = PerformanceCriteria.check_performance(
            category='large',
            alternatives=200,
            criteria=50,
            exec_time=5.0,
            memory_mb=1500  # 超过 1024MB 限制
        )

        assert criteria['response_time_ok'] == True
        assert criteria['memory_ok'] == False


class TestGeneratePerformanceReport:
    """测试 generate_performance_report 函数"""

    def test_generate_report(self, tmp_path):
        """测试生成性能报告"""
        test_results = {
            'small': {
                'alternatives': 10,
                'criteria': 5,
                'execution_time': 0.3,
                'memory_mb': 30,
                'response_time_ok': True,
                'memory_ok': True
            },
            'medium': {
                'alternatives': 50,
                'criteria': 20,
                'execution_time': 1.5,
                'memory_mb': 150,
                'response_time_ok': True,
                'memory_ok': True
            }
        }

        output_file = tmp_path / "performance_report.md"
        generate_performance_report(test_results, output_file)

        assert output_file.exists()

        # 验证报告内容
        content = output_file.read_text(encoding='utf-8')
        assert "性能测试报告" in content
        assert "10方案 × 5准则" in content
        assert "50方案 × 20准则" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
