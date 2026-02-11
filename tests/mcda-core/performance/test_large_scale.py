"""
大规模数据性能测试
"""

import pytest
from pathlib import Path
import sys

# 添加 mcda_core 到路径
mcda_core_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "scripts"
if str(mcda_core_path) not in sys.path:
    sys.path.insert(0, str(mcda_core_path))

from mcda_core.core import MCDAOrchestrator
from .utils import measure_execution_time, PerformanceCriteria, generate_performance_report


class TestLargeScalePerformance:
    """大规模数据性能测试"""

    def test_small_scale_performance(self):
        """小规模性能测试: 10方案 × 5准则"""
        config_path = Path(__file__).parent / "fixtures" / "small_10x5.yaml"
        orchestrator = MCDAOrchestrator()

        result = measure_execution_time(
            orchestrator.run_workflow,
            str(config_path)
        )

        criteria = PerformanceCriteria.check_performance(
            'small', 10, 5,
            result['execution_time'],
            result['memory_mb']
        )

        # 验证性能标准
        assert criteria['response_time_ok'], \
            f"响应时间 {result['execution_time']:.3f}s 超过限制 {criteria['time_limit']}s"
        assert criteria['memory_ok'], \
            f"内存使用 {result['memory_mb']:.1f}MB 超过限制 {criteria['memory_limit']}MB"

        # 验证结果有效性
        assert result['result'] is not None
        assert hasattr(result['result'], 'rankings')
        assert len(result['result'].rankings) > 0

        print(f"\n✅ 小规模测试通过:")
        print(f"   响应时间: {result['execution_time']:.3f}s (限制: < {criteria['time_limit']}s)")
        print(f"   内存使用: {result['memory_mb']:.1f}MB (限制: < {criteria['memory_limit']}MB)")

    def test_medium_scale_performance(self):
        """中规模性能测试: 50方案 × 20准则"""
        config_path = Path(__file__).parent / "fixtures" / "medium_50x20.yaml"
        orchestrator = MCDAOrchestrator()

        result = measure_execution_time(
            orchestrator.run_workflow,
            str(config_path)
        )

        criteria = PerformanceCriteria.check_performance(
            'medium', 50, 20,
            result['execution_time'],
            result['memory_mb']
        )

        # 验证性能标准
        assert criteria['response_time_ok'], \
            f"响应时间 {result['execution_time']:.3f}s 超过限制 {criteria['time_limit']}s"
        assert criteria['memory_ok'], \
            f"内存使用 {result['memory_mb']:.1f}MB 超过限制 {criteria['memory_limit']}MB"

        # 验证结果有效性
        assert result['result'] is not None
        assert hasattr(result['result'], 'rankings')
        assert len(result['result'].rankings) > 0

        print(f"\n✅ 中规模测试通过:")
        print(f"   响应时间: {result['execution_time']:.3f}s (限制: < {criteria['time_limit']}s)")
        print(f"   内存使用: {result['memory_mb']:.1f}MB (限制: < {criteria['memory_limit']}MB)")

    def test_large_scale_performance(self):
        """大规模性能测试: 100方案 × 50准则"""
        config_path = Path(__file__).parent / "fixtures" / "large_100x50.yaml"
        orchestrator = MCDAOrchestrator()

        result = measure_execution_time(
            orchestrator.run_workflow,
            str(config_path)
        )

        criteria = PerformanceCriteria.check_performance(
            'large', 100, 50,
            result['execution_time'],
            result['memory_mb']
        )

        # 验证性能标准
        assert criteria['response_time_ok'], \
            f"响应时间 {result['execution_time']:.3f}s 超过限制 {criteria['time_limit']}s"
        assert criteria['memory_ok'], \
            f"内存使用 {result['memory_mb']:.1f}MB 超过限制 {criteria['memory_limit']}MB"

        # 验证结果有效性
        assert result['result'] is not None
        assert hasattr(result['result'], 'rankings')
        assert len(result['result'].rankings) > 0

        print(f"\n✅ 大规模测试通过:")
        print(f"   响应时间: {result['execution_time']:.3f}s (限制: < {criteria['time_limit']}s)")
        print(f"   内存使用: {result['memory_mb']:.1f}MB (限制: < {criteria['memory_limit']}MB)")


class TestPerformanceBenchmarking:
    """性能基准测试"""

    def test_generate_benchmark_report(self, tmp_path):
        """生成性能基准报告"""
        # 收集所有规模的测试结果
        test_results = {}
        orchestrator = MCDAOrchestrator()

        # 小规模测试
        config_path = Path(__file__).parent / "fixtures" / "small_10x5.yaml"
        result = measure_execution_time(orchestrator.run_workflow, str(config_path))
        criteria = PerformanceCriteria.check_performance('small', 10, 5, result['execution_time'], result['memory_mb'])

        test_results['small'] = {
            'alternatives': 10,
            'criteria': 5,
            'execution_time': result['execution_time'],
            'memory_mb': result['memory_mb'],
            'response_time_ok': criteria['response_time_ok'],
            'memory_ok': criteria['memory_ok']
        }

        # 中规模测试
        config_path = Path(__file__).parent / "fixtures" / "medium_50x20.yaml"
        result = measure_execution_time(orchestrator.run_workflow, str(config_path))
        criteria = PerformanceCriteria.check_performance('medium', 50, 20, result['execution_time'], result['memory_mb'])

        test_results['medium'] = {
            'alternatives': 50,
            'criteria': 20,
            'execution_time': result['execution_time'],
            'memory_mb': result['memory_mb'],
            'response_time_ok': criteria['response_time_ok'],
            'memory_ok': criteria['memory_ok']
        }

        # 大规模测试
        config_path = Path(__file__).parent / "fixtures" / "large_100x50.yaml"
        result = measure_execution_time(orchestrator.run_workflow, str(config_path))
        criteria = PerformanceCriteria.check_performance('large', 100, 50, result['execution_time'], result['memory_mb'])

        test_results['large'] = {
            'alternatives': 100,
            'criteria': 50,
            'execution_time': result['execution_time'],
            'memory_mb': result['memory_mb'],
            'response_time_ok': criteria['response_time_ok'],
            'memory_ok': criteria['memory_ok']
        }

        # 生成报告
        output_file = tmp_path / "performance_report.md"
        generate_performance_report(test_results, output_file)

        # 验证报告生成
        assert output_file.exists()
        content = output_file.read_text(encoding='utf-8')
        assert "性能测试报告" in content
        assert "10方案 × 5准则" in content
        assert "50方案 × 20准则" in content
        assert "100方案 × 50准则" in content

        print(f"\n✅ 性能基准报告生成: {output_file}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
