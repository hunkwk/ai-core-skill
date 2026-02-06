# v0.10 执行计划 - Web UI + API + 一票否决机制

**版本**: v0.10
**功能**: Web UI + API 集成 + 一票否决机制
**开发方法**: TDD（测试驱动开发）
**预计工期**: 20 人日 (4 周)
**开始日期**: 待定
**状态**: 📋 计划中

---

## 📊 版本总览

### 目标

1. **一票否决机制**（P0）- 企业级决策场景支持
2. **Web UI**（P0）- 友好的 Web 界面
3. **API 接口**（P0）- RESTful API
4. **数据导入导出**（P1）- 复用 v0.9 功能
5. **报告生成**（P1）- HTML/PDF 报告
6. **部署文档**（P2）- Docker 部署

### 工期分配

| Phase | 功能 | 工期 | 优先级 |
|-------|------|------|--------|
| 1 | 一票否决机制 | 6人日 | P0 |
| 2 | Web UI | 6人日 | P0 |
| 3 | API 接口 | 4人日 | P0 |
| 4 | 数据导入导出 | 2人日 | P1 |
| 5 | 报告生成 | 1人日 | P1 |
| 6 | 部署文档 | 1人日 | P2 |
| **总计** | - | **20人日** | - |

---

## Phase 1: 一票否决机制（6 人日）

**优先级**: P0（最高）
**状态**: 📋 待开始

### 1.1 数据模型设计（1 人日）

#### 目标

设计并实现否决相关的数据模型。

#### 交付物

- [ ] `skills/mcda-core/lib/constraints/models.py`
  - [ ] `VetoCondition` - 否决条件
  - [ ] `VetoConfig` - 否决配置
  - [ ] `VetoResult` - 否决评估结果
  - [ ] `VetoTier` - 分级否决档位
  - [ ] `ConstraintMetadata` - 约束元数据

#### TDD 测试清单

`tests/mcda-core/unit/test_constraints/test_models.py`:
- [ ] `test_veto_condition_equals_operator()`
- [ ] `test_veto_condition_greater_than_operator()`
- [ ] `test_veto_condition_in_operator()`
- [ ] `test_veto_condition_invalid_operator_raises_error()`
- [ ] `test_veto_config_hard_type()`
- [ ] `test_veto_config_soft_type()`
- [ ] `test_veto_config_tiered_type()`
- [ ] `test_veto_config_composite_type()`
- [ ] `test_veto_config_validation()`
- [ ] `test_veto_result_creation()`
- [ ] `test_veto_tier_creation()`

#### 验收标准

- [ ] 所有测试通过（100%）
- [ ] 测试覆盖率 ≥ 90%
- [ ] 代码符合 PEP 8 规范
- [ ] 类型注解 100% 覆盖

---

### 1.2 VetoEvaluator 实现（2 人日）

#### 目标

实现否决评估器核心逻辑。

#### 交付物

- [ ] `skills/mcda-core/lib/constraints/evaluator.py`
  - [ ] `VetoEvaluator` 类
  - [ ] `evaluate()` - 主评估方法
  - [ ] `_evaluate_hard()` - 硬否决评估
  - [ ] `_evaluate_soft()` - 软否决评估
  - [ ] `_evaluate_tiered()` - 分级否决评估
  - [ ] `_evaluate_composite()` - 组合否决评估

#### TDD 测试清单

`tests/mcda-core/unit/test_constraints/test_evaluator.py`:
- [ ] `test_hard_veto_accept()`
- [ ] `test_hard_veto_reject()`
- [ ] `test_hard_veto_with_lower_better()`
- [ ] `test_soft_veto_no_penalty()`
- [ ] `test_soft_veto_with_penalty()`
- [ ] `test_soft_veto_accumulates_penalties()`
- [ ] `test_tiered_veto_low_risk_accept()`
- [ ] `test_tiered_veto_medium_risk_warning()`
- [ ] `test_tiered_veto_high_risk_reject()`
- [ ] `test_tiered_veto_boundary_cases()`
- [ ] `test_composite_veto_or_logic_one_match()`
- [ ] `test_composite_veto_or_logic_multiple_matches()`
- [ ] `test_composite_veto_and_logic_all_match()`
- [ ] `test_composite_veto_and_logic_partial_match()`
- [ ] `test_evaluator_integration()`

#### 验收标准

- [ ] 所有测试通过（100%）
- [ ] 测试覆盖率 ≥ 90%
- [ ] 支持四种否决类型
- [ ] 支持正向和反向指标

---

### 1.3 ConstraintService 实现（1.5 人日）

#### 目标

实现约束服务，集成到现有架构。

#### 交付物

- [ ] `skills/mcda-core/lib/services/constraint_service.py`
  - [ ] `ConstraintService` 类
  - [ ] `filter_problem()` - 过滤被否决的方案
  - [ ] `apply_penalties()` - 应用软否决惩罚
  - [ ] `get_constraint_metadata()` - 获取约束元数据

#### TDD 测试清单

`tests/mcda-core/unit/test_services/test_constraint_service.py`:
- [ ] `test_filter_problem_no_veto_rules()`
- [ ] `test_filter_problem_with_hard_veto()`
- [ ] `test_filter_problem_all_rejected()`
- [ ] `test_filter_problem_partial_rejected()`
- [ ] `test_apply_penalties_to_scores()`
- [ ] `test_apply_penalties_with_soft_veto()`
- [ ] `test_get_constraint_metadata()`
- [ ] `test_service_integration_with_algorithm()`

#### 集成测试

`tests/mcda-core/integration/test_constraints_integration.py`:
- [ ] `test_vendor_qualification_scenario()` - 供应商准入场景
- [ ] `test_project_risk_assessment_scenario()` - 项目风险评估场景
- [ ] `test_contract_risk_scenario()` - 合同风险场景

#### 验收标准

- [ ] 所有单元测试通过（100%）
- [ ] 所有集成测试通过（100%）
- [ ] 测试覆盖率 ≥ 85%
- [ ] 与现有算法无缝集成

---

### 1.4 CLI 集成（1 人日）

#### 目标

扩展 CLI，支持否决规则配置。

#### 交付物

- [ ] `skills/mcda-core/lib/cli.py` 更新
  - [ ] 支持否决规则解析
  - [ ] 显示否决结果
  - [ ] 错误提示优化

#### TDD 测试清单

`tests/mcda-core/integration/test_cli/test_cli_veto.py`:
- [ ] `test_cli_with_hard_veto()`
- [ ] `test_cli_with_soft_veto()`
- [ ] `test_cli_with_tiered_veto()`
- [ ] `test_cli_veto_result_display()`
- [ ] `test_cli_all_alternatives_vetoed()`

#### YAML 配置示例

`tests/mcda-core/fixtures/veto_config.yaml`:
- [ ] 供应商准入配置（硬否决 + 软否决）
- [ ] 项目风险评估配置（分级否决）
- [ ] 合同风险评估配置（组合否决）

#### 验收标准

- [ ] CLI 命令支持否决规则
- [ ] 错误提示清晰友好
- [ ] 结果展示完整

---

### 1.5 测试和文档（0.5 人日）

#### 目标

完善测试覆盖和文档。

#### 交付物

- [ ] 测试覆盖率报告
- [ ] 用户配置指南
- [ ] API 文档

#### 文档清单

- [ ] `docs/active/mcda-core/v0.10/tdd-veto-constraints.md` - TDD 进度
- [ ] `docs/active/mcda-core/v0.10/veto-configuration-guide.md` - 配置指南
- [ ] `docs/active/mcda-core/v0.10/veto-use-cases.md` - 使用案例

#### 验收标准

- [ ] 测试覆盖率 ≥ 90%
- [ ] 文档完整清晰
- [ ] 配置示例可运行

---

## Phase 2: Web UI（6 人日）

**优先级**: P0（最高）
**状态**: 📋 待开始

### 2.1 技术栈选型（0.5 人日）

#### 技术选型

- **前端**: React 18 + TypeScript
- **样式**: Tailwind CSS 3.x
- **状态管理**: React Context + Hooks
- **构建工具**: Vite
- **后端**: FastAPI（Python 3.12）
- **部署**: Docker + Docker Compose

#### 验收标准

- [ ] 技术栈确定
- [ ] 开发环境搭建完成
- [ ] Hello World 运行成功

---

### 2.2 项目初始化（0.5 人日）

#### 交付物

```
skills/mcda-core/web/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
├── index.html
└── src/
    ├── App.tsx
    ├── main.tsx
    ├── components/
    ├── pages/
    └── api/
```

#### TDD 测试清单

- [ ] `test_development_environment()`
- [ ] `test_build_process()`
- [ ] `test_hot_reload()`

---

### 2.3 核心组件开发（3 人日）

#### 页面组件

- [ ] `pages/DecisionCreatePage.tsx` - 决策问题创建页面
- [ ] `pages/AlgorithmSelectPage.tsx` - 算法选择页面
- [ ] `pages/ResultDisplayPage.tsx` - 结果展示页面
- [ ] `pages/SensitivityAnalysisPage.tsx` - 敏感性分析页面

#### UI 组件

- [ ] `components/DecisionForm.tsx` - 决策问题表单
- [ ] `components/CriteriaEditor.tsx` - 准则编辑器
- [ ] `components/ScoreMatrix.tsx` - 评分矩阵
- [ ] `components/RankingChart.tsx` - 排名图表
- [ ] `components/VetoRulesEditor.tsx` - **否决规则编辑器（新增）**
- [ ] `components/ResultTable.tsx` - 结果表格
- [ ] `components/SensitivityChart.tsx` - 敏感性图表

#### TDD 测试清单

`tests/web/unit/components/`:
- [ ] `test_DecisionForm_component()`
- [ ] `test_CriteriaEditor_component()`
- [ ] `test_ScoreMatrix_component()`
- [ ] `test_VetoRulesEditor_component()` - **新增**
- [ ] `test_ResultTable_component()`
- [ ] `test_RankingChart_component()`

#### 验收标准

- [ ] 所有组件测试通过
- [ ] 组件可复用性良好
- [ ] UI 响应式设计

---

### 2.4 否决规则配置界面（1 人日）

#### 目标

实现否决规则的可视化配置界面。

#### 交付物

- [ ] `components/VetoRulesEditor.tsx` - 否决规则编辑器
- [ ] `components/HardVetoConfig.tsx` - 硬否决配置
- [ ] `components/SoftVetoConfig.tsx` - 软否决配置
- [ ] `components/TieredVetoConfig.tsx` - 分级否决配置
- [ ] `components/CompositeVetoConfig.tsx` - 组合否决配置

#### 功能特性

- [ ] 拖拽式规则配置
- [ ] 实时预览
- [ ] 规则验证
- [ ] 导入/导出配置

#### TDD 测试清单

- [ ] `test_veto_rules_editor_render()`
- [ ] `test_veto_rules_editor_add_rule()`
- [ ] `test_veto_rules_editor_delete_rule()`
- [ ] `test_veto_rules_editor_validation()`
- [ ] `test_hard_veto_config()`
- [ ] `test_soft_veto_config()`
- [ ] `test_tiered_veto_config()`
- [ ] `test_composite_veto_config()`

#### 验收标准

- [ ] 支持四种否决类型配置
- [ ] 实时验证规则正确性
- [ ] 导出 YAML 配置文件

---

### 2.5 样式和响应式设计（1 人日）

#### 目标

使用 Tailwind CSS 实现美观的 UI。

#### 交付物

- [ ] 全局样式配置
- [ ] 响应式布局
- [ ] 暗色模式支持（可选）
- [ ] 打印样式

#### 验收标准

- [ ] UI 美观专业
- [ ] 移动端适配
- [ ] 浏览器兼容性

---

## Phase 3: API 接口（4 人日）

**优先级**: P0（最高）
**状态**: 📋 待开始

### 3.1 FastAPI 后端搭建（1 人日）

#### 交付物

```
skills/mcda-core/api/
├── __init__.py
├── main.py
├── routers/
│   ├── __init__.py
│   ├── decisions.py
│   ├── algorithms.py
│   └── constraints.py - **新增**
├── models/
│   ├── __init__.py
│   └── schemas.py
└── services/
    ├── __init__.py
    └── decision_service.py
```

#### API 端点

**决策端点**:
- [ ] `POST /api/decisions` - 创建决策问题
- [ ] `GET /api/decisions/{id}` - 获取决策结果
- [ ] `DELETE /api/decisions/{id}` - 删除决策问题

**算法端点**:
- [ ] `GET /api/algorithms` - 获取算法列表
- [ ] `POST /api/algorithms/{name}/calculate` - 执行算法
- [ ] `GET /api/algorithms/{name}/schema` - 获取算法配置模式

**约束端点（新增）**:
- [ ] `POST /api/constraints/validate` - 验证否决规则
- [ ] `GET /api/constraints/types` - 获取否决类型
- [ ] `GET /api/constraints/schema` - 获取约束配置模式

#### TDD 测试清单

`tests/api/unit/test_routers/`:
- [ ] `test_create_decision()`
- [ ] `test_get_decision_result()`
- [ ] `test_calculate_with_algorithm()`
- [ ] `test_validate_constraints()` - **新增**
- [ ] `test_get_constraint_types()` - **新增**

#### 验收标准

- [ ] API 端点功能完整
- [ ] RESTful 设计规范
- [ ] API 文档自动生成（Swagger/OpenAPI）

---

### 3.2 数据模型和验证（1 人日）

#### 交付物

- [ ] `models/schemas.py` - Pydantic 数据模型
  - [ ] `DecisionProblemCreate` - 创建决策问题
  - [ ] `DecisionProblemResponse` - 决策问题响应
  - [ ] `VetoRuleCreate` - **否决规则创建**
  - [ ] `VetoRuleResponse` - **否决规则响应**
  - [ ] `CalculationRequest` - 计算请求
  - [ ] `CalculationResponse` - 计算响应

#### TDD 测试清单

- [ ] `test_decision_problem_validation()`
- [ ] `test_veto_rule_validation()` - **新增**
- [ ] `test_calculation_request_validation()`
- [ ] `test_response_serialization()`

#### 验收标准

- [ ] 数据验证完整
- [ ] 错误提示清晰
- [ ] 支持否决规则序列化

---

### 3.3 服务层实现（1.5 人日）

#### 交付物

- [ ] `services/decision_service.py`
  - [ ] `create_decision()` - 创建决策问题
  - [ ] `calculate()` - 执行算法计算
  - [ ] `get_result()` - 获取结果
  - [ ] `apply_constraints()` - **应用约束规则**
  - [ ] `validate_constraints()` - **验证约束规则**

#### TDD 测试清单

`tests/api/integration/test_services/`:
- [ ] `test_create_and_calculate()`
- [ ] `test_apply_hard_veto()`
- [ ] `test_apply_soft_veto()`
- [ ] `test_apply_tiered_veto()`
- [ ] `test_apply_composite_veto()`
- [ ] `test_constraint_validation()`

#### 验收标准

- [ ] 服务层逻辑正确
- [ ] 与否决服务集成
- [ ] 错误处理完善

---

### 3.4 API 文档和测试（0.5 人日）

#### 交付物

- [ ] Swagger/OpenAPI 文档
- [ ] API 使用示例
- [ ] Postman Collection

#### 验收标准

- [ ] API 文档完整
- [ ] 示例代码可运行
- [ ] 接口测试通过

---

## Phase 4: 数据导入导出（2 人日）

**优先级**: P1
**状态**: 📋 待开始

### 4.1 导出功能增强（1.5 人日）

#### 目标

扩展数据导出功能。

#### 交付物

- [ ] 支持导出为 Excel（带格式）
- [ ] 支持导出为 JSON
- [ ] 支持导出为 CSV
- [ ] **支持导出否决结果**（新增）

#### TDD 测试清单

- [ ] `test_export_to_excel()`
- [ ] `test_export_to_json()`
- [ ] `test_export_to_csv()`
- [ ] `test_export_with_veto_results()` - **新增**

#### 验收标准

- [ ] 导出功能完整
- [ ] 文件格式正确
- [ ] 包含否决结果信息

---

### 4.2 格式验证（0.5 人日）

#### 目标

增强数据格式验证。

#### 交付物

- [ ] CSV 格式验证增强
- [ ] Excel 格式验证增强
- [ ] **否决规则配置验证**（新增）

#### TDD 测试清单

- [ ] `test_csv_validation()`
- [ ] `test_excel_validation()`
- [ ] `test_veto_config_validation()` - **新增**

#### 验收标准

- [ ] 验证逻辑完整
- [ ] 错误提示友好
- [ ] 支持否决规则验证

---

## Phase 5: 报告生成（1 人日）

**优先级**: P1
**状态**: 📋 待开始

### 5.1 HTML 报告生成（0.5 人日）

#### 目标

生成 HTML 格式的决策报告。

#### 交付物

- [ ] `lib/reporter/html_reporter.py`
- [ ] HTML 报告模板
- [ ] **否决结果展示**（新增）

#### TDD 测试清单

- [ ] `test_generate_html_report()`
- [ ] `test_html_report_includes_veto_results()` - **新增**

#### 验收标准

- [ ] HTML 报告美观
- [ ] 包含否决结果

---

### 5.2 PDF 报告生成（0.5 人日）

#### 目标

生成 PDF 格式的决策报告（可选）。

#### 交付物

- [ ] `lib/reporter/pdf_reporter.py`
- [ ] PDF 报告模板
- [ ] **否决结果展示**（新增）

#### TDD 测试清单

- [ ] `test_generate_pdf_report()`
- [ ] `test_pdf_report_includes_veto_results()` - **新增**

#### 验收标准

- [ ] PDF 报告美观
- [ ] 包含否决结果

---

## Phase 6: 部署文档（1 人日）

**优先级**: P2
**状态**: 📋 待开始

### 6.1 Docker 配置（0.5 人日）

#### 交付物

- [ ] `Dockerfile` - Web UI + API
- [ ] `docker-compose.yml` - 完整服务栈
- [ ] `.dockerignore`
- [ ] 部署脚本

#### TDD 测试清单

- [ ] `test_docker_build()`
- [ ] `test_docker_compose_up()`
- [ ] `test_api_accessible_from_container()`

#### 验收标准

- [ ] Docker 镜像构建成功
- [ ] docker-compose 一键启动
- [ ] 服务可访问

---

### 6.2 部署指南（0.5 人日）

#### 交付物

- [ ] 本地开发环境搭建指南
- [ ] 生产环境部署指南
- [ ] **否决规则配置指南**（新增）
- [ ] 故障排查手册

#### 验收标准

- [ ] 文档清晰完整
- [ ] 步骤可复现
- [ ] 包含否决配置示例

---

## 🎯 总体验收标准

### 功能验收

- [ ] 一票否决机制功能完整（4 种类型）
- [ ] Web UI 可用性测试通过
- [ ] API 接口测试覆盖率 ≥ 85%
- [ ] 数据导入导出功能完整
- [ ] 报告生成功能完整（HTML/PDF）
- [ ] Docker 部署成功

### 质量验收

- [ ] 代码符合 PEP 8 规范
- [ ] 类型注解 100% 覆盖
- [ ] 测试覆盖率 ≥ 85%
- [ ] 所有测试通过

### 文档验收

- [ ] API 文档完整（Swagger）
- [ ] 用户配置指南完整
- [ ] 部署文档清晰
- [ ] **否决规则配置示例完整**（新增）

---

## 📊 工期统计

| Phase | 功能 | 工期 | 测试数 | 状态 |
|-------|------|------|--------|------|
| 1 | 一票否决机制 | 6人日 | 40+ | 📋 待开始 |
| 2 | Web UI | 6人日 | 20+ | 📋 待开始 |
| 3 | API 接口 | 4人日 | 15+ | 📋 待开始 |
| 4 | 数据导入导出 | 2人日 | 6+ | 📋 待开始 |
| 5 | 报告生成 | 1人日 | 4+ | 📋 待开始 |
| 6 | 部署文档 | 1人日 | 3+ | 📋 待开始 |
| **总计** | - | **20人日** | **88+** | - |

---

## 📝 依赖关系

```
Phase 1 (一票否决) ─────────────────────────┐
                                              │
Phase 3 (API) ───────────────────────────────┼──→ Phase 4 (数据导入导出)
                                              │
Phase 2 (Web UI) ─────────────────────────────┘
                                              │
Phase 5 (报告生成) ◄──────────────────────────┘
                                              │
Phase 6 (部署文档) ◄──────────────────────────┘
```

**关键路径**:
1. Phase 1 (一票否决) **必须优先完成**
2. Phase 2 和 3 可并行开发
3. Phase 4-6 依赖前面的阶段

---

## 🎓 成功标准

### 最小可行版本（MVP）

- [ ] Phase 1 完成：一票否决机制（hard + soft）
- [ ] Phase 2 完成：基础 Web UI
- [ ] Phase 3 完成：核心 API 端点
- [ ] 测试覆盖率 ≥ 80%

### 完整版本

- [ ] 所有 6 个 Phase 完成
- [ ] 测试覆盖率 ≥ 85%
- [ ] 文档完整
- [ ] Docker 部署成功

---

## 📚 参考文档

### 架构设计
- [ADR-014: 一票否决机制架构设计](../../decisions/mcda-core/014-veto-mechanism.md)
- [ADR-001: MCDA Core 分层架构设计](../../decisions/mcda-core/001-mcda-layered-architecture.md)

### 版本规划
- [完整版本路线图](../../plans/mcda-core/roadmap-complete.md)
- [版本规划历史](../../active/mcda-core/version-planning-history.md)

### 技术文档
- [React 官方文档](https://react.dev/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Tailwind CSS 官方文档](https://tailwindcss.com/)

---

**计划创建日期**: 2026-02-05
**计划创建人**: Claude Sonnet 4.5
**状态**: 📋 待用户确认
