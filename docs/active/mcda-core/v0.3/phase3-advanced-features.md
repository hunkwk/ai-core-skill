# MCDA Core v0.3 Phase 3 - 高级功能 TDD 开发

**开始时间**: 2026-02-01
**状态**: 🔴 RED
**阶段**: Phase 3 - 高级功能实现

---

## 🎯 Phase 3 目标

### 核心功能
1. **算法结果对比服务**
   - 多算法结果对比
   - 排名相关性分析
   - 一致性评估

2. **敏感性分析增强**
   - 权重扰动分析
   - 准则敏感性评估
   - 稳定性指标

3. **可视化功能**
   - ASCII 图表（柱状图、雷达图）
   - HTML 报告生成（可选，使用 Jinja2）

---

## 📚 功能详细设计

### 1. 算法结果对比服务

**功能**:
- 运行多个算法并对比结果
- 计算排名相关性（Spearman 相关系数）
- 识别排名差异
- 生成对比报告

**API 设计**:
```python
class ComparisonService:
    def compare_algorithms(
        decision_matrix,
        weights,
        algorithms,
        criteria_directions=None
    ) -> dict:
        """对比多个算法的排序结果"""

    def calculate_ranking_correlation(
        ranking1,
        ranking2
    ) -> float:
        """计算 Spearman 相关系数"""

    def identify_ranking_differences(
        rankings
    ) -> list:
        """识别排名差异"""
```

### 2. 敏感性分析增强

**功能**:
- 单准则权重扰动分析
- 全局敏感性分析
- 排名稳定性评估

**API 设计**:
```python
class SensitivityAnalysisService:
    def single_criterion_sensitivity(
        decision_matrix,
        weights,
        criterion_index,
        n_samples=100
    ) -> dict:
        """单准则权重敏感性分析"""

    def global_sensitivity(
        decision_matrix,
        weights,
        n_samples=1000
    ) -> dict:
        """全局敏感性分析"""

    def ranking_stability(
        base_ranking,
        perturbed_rankings
    ) -> dict:
        """排名稳定性评估"""
```

### 3. 可视化功能

#### ASCII 图表
```python
class ASCIIVisualizer:
    def bar_chart(
        data,
        title,
        width=60
    ) -> str:
        """生成 ASCII 柱状图"""

    def radar_chart(
        scores,
        labels,
        title
    ) -> str:
        """生成 ASCII 雷达图"""

    def ranking_comparison(
        rankings,
        title
    ) -> str:
        """生成排名对比图"""
```

#### HTML 报告（可选）
```python
class HTMLReporter:
    def generate_report(
        results,
        template_name="default",
        theme="light"
    ) -> str:
        """生成 HTML 报告"""
```

---

## 🧪 测试计划

### 算法对比测试
- test_compare_two_algorithms - 对比两个算法
- test_compare_multiple_algorithms - 对比多个算法
- test_ranking_correlation - 排名相关性计算
- test_identify_differences - 识别差异

### 敏感性分析测试
- test_single_criterion_sensitivity - 单准则敏感性
- test_global_sensitivity - 全局敏感性
- test_ranking_stability - 排名稳定性
- test_edge_cases - 边界条件

### 可视化测试
- test_ascii_bar_chart - ASCII 柱状图
- test_ascii_radar_chart - ASCII 雷达图
- test_html_report_generation - HTML 报告（可选）

---

## 📁 文件结构

```
skills/mcda-core/lib/
├── services/
│   ├── comparison_service.py      # 算法对比服务
│   └── sensitivity_service.py     # 敏感性分析服务（增强）
├── visualization/
    ├── ascii_visualizer.py        # ASCII 可视化
    └── html_reporter.py           # HTML 报告（可选）

tests/mcda-core/
├── test_services/
│   ├── test_comparison_service.py
│   └── test_sensitivity_service.py
└── test_visualization/
    ├── test_ascii_visualizer.py
    └── test_html_reporter.py
```

---

## 🔬 TDD 循环

### 🔴 RED - 编写测试
- [ ] 创建算法对比测试
- [ ] 创建敏感性分析测试
- [ ] 创建可视化测试

### 🟢 GREEN - 最小实现
- [ ] 实现 ComparisonService
- [ ] 增强 SensitivityAnalysisService
- [ ] 实现 ASCIIVisualizer
- [ ] 实现 HTMLReporter（可选）

### 🔵 REFACTOR - 重构优化
- [ ] 优化计算性能
- [ ] 改进图表质量
- [ ] 添加更多可视化选项

### ✅ DONE - 验收
- [ ] 所有测试通过
- [ ] 测试覆盖率 ≥ 90%
- [ ] 文档更新

---

## 📊 进度追踪

| 任务 | 状态 | 时间 |
|-----|------|------|
| RED 阶段 | 🔴 进行中 | - |
| GREEN 阶段 | ⏳ 待开始 | - |
| REFACTOR 阶段 | ⏳ 待开始 | - |
| DONE 阶段 | ⏳ 待开始 | - |

---

## 📝 更新日志

### 2026-02-01
- 🔴 开始 RED 阶段 - 编写测试用例

---

**当前状态**: 🔴 RED - 编写测试
**下一步**: 创建测试文件并编写测试用例
