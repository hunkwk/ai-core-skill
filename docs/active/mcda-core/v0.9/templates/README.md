# MCDA Core v0.9 数据导入模板

本目录包含 MCDA Core v0.9 的数据导入模板文件。

## 📁 模板文件

### 1. CSV 模板（csv_template.csv）

标准 CSV 格式的决策数据模板。

**格式说明**：
```
方案A,方案B,方案C
性能,0.4,higher,85,90,88
成本,0.3,lower,50,60,55
可靠性,0.2,higher,90,85,92
易用性,0.1,higher,80,75,78
```

**结构**：
- 第 1 行：备选方案名称（逗号分隔）
- 第 2+ 行：准则数据
- 列结构：[准则名称, 权重, 方向, 方案1得分, 方案2得分, ...]

**区间数格式**：
- 逗号分隔：`80,90`
- 方括号格式：`[80,90]`

### 2. Excel 模板（excel_template.xlsx）

Excel 格式的决策数据模板。

**Sheet1: 决策矩阵**

|         | 权重   | 方向   | 方案A | 方案B | 方案C |
|---------|--------|--------|-------|-------|-------|
| 性能    | 0.4    | higher | 85    | 90    | 88    |
| 成本    | 0.3    | lower  | 50    | 60    | 55    |
| 可靠性  | 0.2    | higher | 90    | 85    | 92    |
| 易用性  | 0.1    | higher | 80    | 75    | 78    |

**Sheet2: 元信息（可选）**

| 项目     | 内容       |
|---------|-----------|
| 问题名称 | 供应商选择 |
| 算法     | topsis    |
| 描述     | ...       |

## 🚀 使用方法

### 方法 1: CLI 命令

```bash
# CSV 文件
mcda-decision data.csv --algorithm topsis

# Excel 文件
mcda-decision data.xlsx --algorithm topsis --sheet Sheet1
```

### 方法 2: Python API

```python
from mcda_core import load_data, MCDAProcessor

# CSV
data = load_data("decision_data.csv")
processor = MCDAProcessor(data)
result = processor.decide("topsis")

# Excel
data = load_data("decision_data.xlsx", sheet="Sheet1")
processor = MCDAProcessor(data)
result = processor.decide("topsis")
```

## 📝 注意事项

1. **编码**：CSV 文件推荐使用 UTF-8 编码
2. **分隔符**：CSV 使用逗号（`,`）作为分隔符
3. **区间数**：支持两种格式，推荐使用方括号格式 `[80,90]`
4. **权重归一化**：权重会自动归一化，无需手动计算
5. **方向**：`higher` 表示越大越好，`lower` 表示越小越好

## ❓ 常见问题

### Q1: 如何表示区间数？

A: 支持两种格式：
- 逗号分隔：`80,90`
- 方括号：`[80,90]`

### Q2: 权重需要归一化吗？

A: 不需要，系统会自动归一化。

### Q3: 如何添加更多备选方案？

A: 在第一行添加更多方案名称，每行添加对应的得分即可。

### Q4: Excel 文件支持多个 Sheet 吗？

A: 支持，默认读取第一个 Sheet，可通过 `--sheet` 参数指定。

## 📞 技术支持

如有问题，请参考：
- 使用文档：[MCDA Core 使用指南](../../README_CN.md)
- API 文档：[API 参考](../../docs/api.md)
- 问题反馈：[GitHub Issues](https://github.com/your-repo/issues)
