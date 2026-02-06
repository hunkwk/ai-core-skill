# MCDA-Core 代码审查报告 V4

**审查日期**: 2026-02-06
**审查范围**: `skills/mcda-core/lib/` 目录下的全部 Python 代码
**审查人员**: AI Code Reviewer (Senior Python Code Reviewer)
**报告版本**: V4（全面审查）

---

## 执行摘要

本次审查对 MCDA-Core 项目进行了全面的静态代码分析，涵盖安全性、性能、代码规范、异常处理、资源管理、类型安全等多个维度。

| 级别 | 数量 | 占比 |
|------|------|------|
| 🔴 **Critical** | 0 | 0% |
| 🟠 **High** | 8 | 28% |
| 🟡 **Medium** | 14 | 48% |
| 🟢 **Low** | 7 | 24% |
| **总计** | **29** | 100% |

### 审查结论

**批准状态**: ⚠️ **WARNING** (Medium 级别问题较多，可以谨慎合并)

---

## 详细问题清单

### 🔴 Critical (0个)
无 Critical 级别问题

### 🟠 High Priority (8个)

#### 1. CSV/Excel 注入防护不完整
**文件**: `lib/loaders/csv_loader.py` 第 186-193 行

**问题**: CSV 检查只检查第一个字符，攻击者可以在前面添加空格绕过

**修复建议**:
```python
def _check_csv_injection(self, value: str) -> None:
    value_stripped = value.strip() if value else ""
    dangerous_prefixes = {'=', '+', '$', '@', '\t', '\n', '\r'}
    if value_stripped and value_stripped[0] in dangerous_prefixes:
        raise ValueError(...)
```

#### 2. ChartGenerator.__del__ 不可靠
**文件**: `lib/visualization/charts.py` 第 618-623 行

**问题**: `__del__` 方法调用时机不确定，可能导致内存泄漏

**修复建议**:
```python
class ChartGenerator:
    def __init__(self):
        self.figures = []
        self._closed = False

    def close(self) -> None:
        """显式关闭所有图表"""
        if not self._closed:
            for fig in self.figures:
                plt.close(fig)
            self.figures.clear()
            self._closed = True
```

#### 3. Excel 文件未使用上下文管理器
**文件**: `lib/loaders/excel_loader.py` 第 96 行

**问题**: Excel 工作簿没有使用上下文管理器，异常时可能不会关闭文件

**修复建议**:
```python
from contextlib import closing

with closing(openpyxl.load_workbook(source_path, data_only=True)) as wb:
    # 处理逻辑
```

#### 4-8. 其他 High Priority 问题详见完整报告
- 异常类型不一致
- 算法验证代码重复
- 资源泄漏风险
- 等

### 🟡 Medium Priority (14个)

#### 1. NumPy dtype=object 性能损失
**文件**: `lib/algorithms/topsis_interval.py` 第 102, 174, 226 行

**问题**: 使用 `dtype=object` 会失去 NumPy 的向量化性能优势

#### 2. 魔法数字未定义常量
**文件**: 多个文件

**问题**: 硬编码的 `1e-10`, `0.1`, `0.5` 等魔法数字

#### 3-14. 其他 Medium 问题详见完整报告

---

## 修复优先级

### 立即修复（阻断级）
无

### 短期修复（高级别）- 本周内
1. Excel 文件资源泄漏
2. CSV 注入防护绕过
3. ChartGenerator 资源清理
4. 统一异常类型
5. 提取算法公共验证逻辑

### 中期改进（中级别）- 本月内
1. NumPy dtype=object 性能优化
2. 统一类型注解风格
3. 定义魔法数字为常量

---

*报告生成时间: 2026-02-06*
