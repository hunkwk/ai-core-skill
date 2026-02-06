# 报告生成增强和数据导出增强 - 执行计划

**版本**: v0.11（可选版本）
**功能**: 报告生成增强 + 数据导出增强
**创建日期**: 2026-02-05
**状态**: 📋 计划中

---

## 📊 执行总结

### 目标

增强 MCDA Core 的报告生成和数据导出功能，提供更丰富的输出格式：

1. **HTML 报告生成**（带样式）
2. **PDF 报告导出**
3. **Excel 数据导出**

### 工作量估算

| Phase | 内容 | 工作量 | 状态 |
|-------|------|--------|------|
| **Phase 1** | HTML 报告生成器 | 1.5 人日 | 📋 待开始 |
| **Phase 2** | PDF 报告生成器 | 1.5 人日 | 📋 待开始 |
| **Phase 3** | Excel 导出功能 | 1 人日 | 📋 待开始 |
| **Phase 4** | CLI 集成和文档 | 1 人日 | 📋 待开始 |
| **总计** | | **5 人日** | |

---

## 📋 Phase 1: HTML 报告生成器（1.5 人日）

### 目标

创建带样式的 HTML 报告生成器，提供比 Markdown 更丰富的视觉呈现。

### 功能需求

#### 1.1 HTML 报告生成器（1 人日）

**核心功能**:
- 完整的 HTML 结构（包含 `<head>`、`<body>`、CSS 样式）
- 响应式设计（适配不同屏幕）
- 美观的表格样式
- 图表嵌入（base64 编码）
- 打印友好样式

**报告内容**:
- 决策问题概述（方案、准则、权重）
- 决策结果排名（表格 + 可视化条形图）
- 准则对比表
- 算法元数据
- 生成时间戳

**样式设计**:
- 现代简洁风格
- 表格斑马纹
- 响应式布局
- 色彩方案：蓝色系（专业风格）

#### 1.2 单元测试（0.5 人日）

**测试覆盖**:
- HTML 结构验证
- CSS 样式验证
- 表格内容正确性
- 中文编码测试
- 图表嵌入测试

### 技术实现

**文件结构**:
```
skills/mcda-core/lib/
├── reports/
│   ├── __init__.py
│   ├── html_generator.py    # HTML 报告生成器
│   └── templates/
│       └── report_template.html  # HTML 模板（可选）
```

**依赖库**:
- `jinja2`（可选，用于模板渲染）
- `matplotlib`（图表生成）

**API 设计**:
```python
class HTMLReportGenerator:
    def generate_html(
        self,
        problem: DecisionProblem,
        result: DecisionResult,
        *,
        title: str = "MCDA 决策分析报告",
        include_chart: bool = True,
    ) -> str:
        """生成 HTML 报告"""

    def save_html(
        self,
        problem: DecisionProblem,
        result: DecisionResult,
        file_path: str,
        *,
        title: str = "MCDA 决策分析报告",
        include_chart: bool = True,
    ) -> None:
        """保存 HTML 报告到文件"""
```

---

## 📋 Phase 2: PDF 报告生成器（1.5 人日）

### 目标

创建 PDF 报告导出功能，生成专业格式的 PDF 文档。

### 功能需求

#### 2.1 PDF 生成器（1 人日）

**核心功能**:
- 从 HTML 转换为 PDF（推荐方案）
- 支持中文显示
- 分页控制
- 页眉页脚
- 目录生成（可选）

**技术方案**:
- **方案 A**: 使用 `weasyprint`（推荐）
  - 优点：支持 CSS 样式，HTML → PDF 转换简单
  - 缺点：依赖较多
- **方案 B**: 使用 `reportlab`
  - 优点：纯 Python，功能强大
  - 缺点：API 复杂，需要手动布局

**推荐**: 方案 A（weasyprint）

#### 2.2 单元测试（0.5 人日）

**测试覆盖**:
- PDF 生成测试
- 中文显示测试
- 分页测试
- 文件完整性测试

### 技术实现

**文件结构**:
```
skills/mcda-core/lib/reports/
├── pdf_generator.py           # PDF 生成器
```

**依赖库**:
- `weasyprint`（推荐）或 `reportlab`

**API 设计**:
```python
class PDFReportGenerator:
    def __init__(self, html_generator: HTMLReportGenerator):
        """初始化 PDF 生成器"""
        self.html_generator = html_generator

    def generate_pdf(
        self,
        problem: DecisionProblem,
        result: DecisionResult,
        *,
        title: str = "MCDA 决策分析报告",
        include_chart: bool = True,
    ) -> bytes:
        """生成 PDF 字节流"""

    def save_pdf(
        self,
        problem: DecisionProblem,
        result: DecisionResult,
        file_path: str,
        *,
        title: str = "MCDA 决策分析报告",
        include_chart: bool = True,
    ) -> None:
        """保存 PDF 报告到文件"""
```

---

## 📋 Phase 3: Excel 导出功能（1 人日）

### 目标

创建 Excel 格式导出功能，支持带格式的 Excel 文件导出。

### 功能需求

#### 3.1 Excel 导出器（0.7 人日）

**核心功能**:
- 多工作表导出（Overview、Rankings、Details）
- 单元格格式化（数值、百分比）
- 条件格式（颜色标记）
- 自动列宽
- 图表嵌入（可选）

**工作表结构**:

**Sheet 1: Overview**
- 决策问题基本信息
- 算法元数据
- 生成时间

**Sheet 2: Rankings**
- 排名表格（排名、方案、评分）

**Sheet 3: Scores Matrix**
- 完整评分矩阵（方案 × 准则）

**Sheet 4: Criteria**（可选）
- 准则详情（名称、权重、方向）

#### 3.2 单元测试（0.3 人日）

**测试覆盖**:
- Excel 文件生成测试
- 多工作表测试
- 格式化测试
- 数据正确性测试

### 技术实现

**文件结构**:
```
skills/mcda-core/lib/
├── export/
│   ├── __init__.py
│   └── excel_exporter.py     # Excel 导出器
```

**依赖库**:
- `openpyxl`（已安装）

**API 设计**:
```python
class ExcelExporter:
    def export_excel(
        self,
        problem: DecisionProblem,
        result: DecisionResult,
        *,
        include_charts: bool = False,
    ) -> bytes:
        """导出 Excel 字节流"""

    def save_excel(
        self,
        problem: DecisionProblem,
        result: DecisionResult,
        file_path: str,
        *,
        include_charts: bool = False,
    ) -> None:
        """保存 Excel 文件"""

    def _create_overview_sheet(
        self,
        wb: Workbook,
        problem: DecisionProblem,
        result: DecisionResult,
    ) -> None:
        """创建 Overview 工作表"""

    def _create_rankings_sheet(
        self,
        wb: Workbook,
        result: DecisionResult,
    ) -> None:
        """创建 Rankings 工作表"""

    def _create_scores_sheet(
        self,
        wb: Workbook,
        problem: DecisionProblem,
    ) -> None:
        """创建 Scores Matrix 工作表"""
```

---

## 📋 Phase 4: CLI 集成和文档（1 人日）

### 目标

将报告生成和导出功能集成到 CLI，并完善文档。

### 功能需求

#### 4.1 CLI 集成（0.5 人日）

**新增选项**:
```bash
mcda analyze config.yaml \
    --output report.html \        # 输出文件扩展名决定格式
    --format html \               # 显式指定格式
    --include-chart               # 包含图表
```

**支持格式**:
- `markdown` / `md`
- `json`
- `html`
- `pdf`
- `excel` / `xlsx`

#### 4.2 文档和示例（0.5 人日）

**文档内容**:
- HTML 报告使用示例
- PDF 报告使用示例
- Excel 导出使用示例
- 最佳实践

**示例文件**:
- 生成 HTML 报告示例
- 生成 PDF 报告示例
- 导出 Excel 示例

### 技术实现

**CLI 修改**:
```python
# cli.py 修改
parser.add_argument(
    '--format', '-f',
    choices=['markdown', 'json', 'html', 'pdf', 'excel'],
    help='输出格式（默认：markdown）'
)
parser.add_argument(
    '--include-chart',
    action='store_true',
    help='包含图表（仅 HTML/PDF）'
)
```

---

## 🎯 验收标准

### Phase 1: HTML 报告生成器

- [ ] HTML 报告生成功能正常
- [ ] CSS 样式美观，响应式布局
- [ ] 单元测试覆盖率 ≥ 90%
- [ ] 中文显示正常

### Phase 2: PDF 报告生成器

- [ ] PDF 生成功能正常
- [ ] 中文显示正常
- [ ] 分页合理
- [ ] 单元测试覆盖率 ≥ 90%

### Phase 3: Excel 导出功能

- [ ] Excel 文件生成正常
- [ ] 多工作表正确
- [ ] 格式化正确
- [ ] 单元测试覆盖率 ≥ 90%

### Phase 4: CLI 集成和文档

- [ ] CLI 支持所有格式
- [ ] 使用文档完整
- [ ] 示例代码可运行

---

## 📝 依赖库清单

### 新增依赖

```txt
# HTML 报告（可选，用于模板）
jinja2>=3.1.0

# PDF 报告（二选一）
weasyprint>=60.0  # 推荐
# 或
reportlab>=4.0.0  # 备选
```

### 已有依赖

```txt
# Excel 导出（已安装）
openpyxl>=3.1.0

# 图表生成（已安装）
matplotlib>=3.8.0
```

---

## 🔍 技术决策

### PDF 生成方案选择

**推荐方案**: `weasyprint`

**理由**:
1. **CSS 支持**: 完整支持 CSS3，样式控制简单
2. **HTML 转换**: 可直接复用 HTML 报告生成器
3. **中文支持**: 配置字体后支持中文
4. **代码简洁**: API 简单，易于维护

**备选方案**: `reportlab`

**适用场景**:
- 对 PDF 细粒度控制要求高
- 不想依赖外部 CSS 库

### HTML 生成方案

**推荐方案**: 字符串拼接 + CSS 内联

**理由**:
1. **零依赖**: 不需要 jinja2 等模板引擎
2. **简单直接**: 代码清晰易懂
3. **易于维护**: 修改方便

**备选方案**: 使用 jinja2 模板

**适用场景**:
- 报告格式复杂，需要灵活配置
- 需要支持自定义模板

---

## 🎓 TDD 方法论

每个 Phase 遵循 TDD 流程：

```
RED Phase（编写失败测试）
↓
GREEN Phase（实现功能）
↓
REFACTOR Phase（重构优化）
↓
100% 测试通过
```

### 测试文件结构

```
tests/mcda-core/unit/test_reports/
├── test_html_generator.py
├── test_pdf_generator.py
└── ../test_export/
    └── test_excel_exporter.py
```

---

## 📊 进度追踪

**创建时间**: 2026-02-05
**当前状态**: 📋 计划中
**下一里程碑**: Phase 1.1 开始

---

**执行计划创建日期**: 2026-02-05
**创建人**: Claude Sonnet 4.5
**计划状态**: ✅ 待用户确认
