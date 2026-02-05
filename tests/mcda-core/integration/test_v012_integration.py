"""
v0.12 集成测试

验证性能测试框架、性能基准和功能正确性
"""

import pytest
from pathlib import Path
import sys

# 添加 mcda_core 到路径
mcda_core_path = Path(__file__).parent.parent.parent / "skills" / "mcda-core" / "lib"
if str(mcda_core_path) not in sys.path:
    sys.path.insert(0, str(mcda_core_path))

from mcda_core.core import MCDAOrchestrator
from performance.utils import measure_execution_time, PerformanceCriteria, generate_performance_report


class TestV012EndToEnd:
    """v0.12 端到端集成测试"""

    def test_performance_framework_e2e(self, tmp_path):
        """测试性能框架端到端流程"""
        print("\n🚀 测试性能框架端到端流程...")

        orchestrator = MCDAOrchestrator()
        fixtures_dir = Path(__file__).parent.parent / "performance" / "fixtures"

        # 测试所有规模
        test_results = {}
        test_configs = [
            ('small', 'small_10x5.yaml', 10, 5, 'small'),
            ('medium', 'medium_50x20.yaml', 50, 20, 'medium'),
            ('large', 'large_100x50.yaml', 100, 50, 'large'),
        ]

        for category, filename, alts, crits, perf_cat in test_configs:
            config_path = fixtures_dir / filename
            print(f"\n📊 测试 {category}: {alts}方案 × {crits}准则")

            # 运行性能测试
            result = measure_execution_time(
                orchestrator.run_workflow,
                str(config_path)
            )

            # 验证性能标准
            criteria = PerformanceCriteria.check_performance(
                perf_cat, alts, crits,
                result['execution_time'],
                result['memory_mb']
            )

            # 收集结果
            test_results[category] = {
                'alternatives': alts,
                'criteria': crits,
                'execution_time': result['execution_time'],
                'memory_mb': result['memory_mb'],
                'response_time_ok': criteria['response_time_ok'],
                'memory_ok': criteria['memory_ok']
            }

            # 验证性能达标
            assert criteria['response_time_ok'], \
                f"{category} 响应时间 {result['execution_time']:.3f}s 超过限制"
            assert criteria['memory_ok'], \
                f"{category} 内存使用 {result['memory_mb']:.1f}MB 超过限制"

            # 验证结果有效性
            assert result['result'] is not None
            assert hasattr(result['result'], 'rankings')
            assert len(result['result'].rankings) > 0

            print(f"   ✅ 响应时间: {result['execution_time']:.3f}s")
            print(f"   ✅ 内存使用: {result['memory_mb']:.1f}MB")
            print(f"   ✅ 排名数: {len(result['result'].rankings)}")

        # 生成性能报告
        output_file = tmp_path / "integration_performance_report.md"
        generate_performance_report(test_results, output_file)

        # 验证报告生成
        assert output_file.exists()
        content = output_file.read_text(encoding='utf-8')
        assert "性能测试报告" in content
        assert "10方案 × 5准则" in content
        assert "50方案 × 20准则" in content
        assert "100方案 × 50准则" in content

        print(f"\n✅ 性能报告生成: {output_file}")

    def test_performance_baseline_consistency(self):
        """测试性能基准一致性"""
        print("\n🔍 测试性能基准一致性...")

        orchestrator = MCDAOrchestrator()
        config_path = Path(__file__).parent.parent / "performance" / "fixtures" / "medium_50x20.yaml"

        # 运行 3 次，检查一致性
        execution_times = []
        for i in range(3):
            result = measure_execution_time(
                orchestrator.run_workflow,
                str(config_path)
            )
            execution_times.append(result['execution_time'])

        # 计算标准差
        import statistics
        mean_time = statistics.mean(execution_times)
        stdev_time = statistics.stdev(execution_times)
        cv = (stdev_time / mean_time) * 100  # 变异系数

        print(f"   平均响应时间: {mean_time:.3f}s")
        print(f"   标准差: {stdev_time:.4f}s")
        print(f"   变异系数: {cv:.2f}%")

        # 验证性能稳定性（CV < 10%）
        assert cv < 10, f"性能不稳定，变异系数 {cv:.2f}% > 10%"

        print("   ✅ 性能稳定")


class TestV012Correctness:
    """v0.12 功能正确性测试"""

    def test_all_algorithms_work_on_large_scale(self):
        """测试所有算法在大规模数据上的正确性"""
        print("\n🧪 测试所有算法在大规模数据上的正确性...")

        orchestrator = MCDAOrchestrator()
        config_path = Path(__file__).parent.parent / "performance" / "fixtures" / "small_10x5.yaml"

        algorithms = ['topsis', 'vikor', 'wsm']

        for algo in algorithms:
            print(f"\n   测试 {algo.upper()} 算法...")

            # 修改配置使用不同算法
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            config['algorithm']['name'] = algo

            # 保存临时配置
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True)
                temp_config = f.name

            try:
                # 运行算法
                result = orchestrator.run_workflow(temp_config)

                # 验证结果
                assert result is not None
                assert hasattr(result, 'rankings')
                assert len(result.rankings) > 0
                assert hasattr(result, 'metadata')
                assert result.metadata.algorithm_name == algo

                print(f"      ✅ {algo.upper()} 运行成功")
                print(f"      ✅ 生成 {len(result.rankings)} 个排名")
            finally:
                # 清理临时文件
                Path(temp_config).unlink()

    def test_ranking_consistency(self):
        """测试排名一致性"""
        print("\n🔍 测试排名一致性...")

        orchestrator = MCDAOrchestrator()
        config_path = Path(__file__).parent.parent / "performance" / "fixtures" / "small_10x5.yaml"

        # 运行 2 次，检查排名一致性
        rankings_list = []
        for i in range(2):
            result = orchestrator.run_workflow(str(config_path))
            # 提取排名（方案名）
            ranking = [r.alternative for r in result.rankings]
            rankings_list.append(ranking)

        # 验证排名一致
        assert rankings_list[0] == rankings_list[1], "排名不一致"

        print(f"   ✅ 排名一致")
        print(f"   ✅ 前3名: {rankings_list[0][:3]}")


class TestV012Documentation:
    """v0.12 文档完整性测试"""

    def test_performance_baseline_exists(self):
        """测试性能基准报告存在"""
        baseline_file = Path("docs/active/mcda-core/v0.12/v0.12-performance-baseline.md")
        assert baseline_file.exists(), "性能基准报告不存在"

        content = baseline_file.read_text(encoding='utf-8')
        assert "性能测试报告" in content
        assert "10方案 × 5准则" in content
        assert "50方案 × 20准则" in content

        print("   ✅ 性能基准报告完整")

    def test_bottleneck_analysis_exists(self):
        """测试瓶颈分析报告存在"""
        analysis_file = Path("docs/active/mcda-core/v0.12/bottleneck-analysis.md")
        assert analysis_file.exists(), "瓶颈分析报告不存在"

        content = analysis_file.read_text(encoding='utf-8')
        assert "性能瓶颈分析" in content
        assert "Top 5" in content

        print("   ✅ 瓶颈分析报告完整")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
