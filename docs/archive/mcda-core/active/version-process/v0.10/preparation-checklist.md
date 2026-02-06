# v0.10 准备工作清单

**版本**: v0.10
**功能**: Web UI + API + 一票否决机制
**开始日期**: 待定
**状态**: 📋 待开始

---

## ✅ 准备工作检查清单

### 1. 文档准备 📚

#### 1.1 架构设计文档
- [x] ADR-014: 一票否决机制架构设计
  - [x] 业务需求分析
  - [x] 数据模型设计
  - [x] 服务层设计
  - [x] 技术方案选型
- [x] v0.10 执行计划
  - [x] 6 个 Phase 详细规划
  - [x] 工期分配
  - [x] 验收标准
- [ ] 版本规划历史（已创建）
  - [ ] ADR-009 ~ 013 归档完成

#### 1.2 技术文档
- [ ] 一票否决机制 TDD 进度文件
  - [ ] `docs/active/mcda-core/v0.10/tdd-veto-constraints.md`
  - [ ] `docs/active/mcda-core/v0.10/tdd-web-ui.md`
  - [ ] `docs/active/mcda-core/v0.10/tdd-api.md`
- [ ] 用户配置指南
  - [ ] `docs/active/mcda-core/v0.10/veto-configuration-guide.md`
  - [ ] `docs/active/mcda-core/v0.10/web-ui-user-guide.md`
  - [ ] `docs/active/mcda-core/v0.10/api-user-guide.md`

---

### 2. 开发环境准备 💻

#### 2.1 Python 环境（后端）
- [x] Python 3.12 已安装
- [x] 虚拟环境 `.venv_linux` 已配置
- [ ] FastAPI 依赖安装
  ```bash
  pip install fastapi uvicorn pydantic
  ```
- [ ] Web 框架依赖安装
  ```bash
  pip install jinja2 python-multipart
  ```

#### 2.2 Node.js 环境（前端）
- [ ] Node.js 18+ 安装检查
  ```bash
  node --version  # 应该 >= 18.0.0
  ```
- [ ] npm 安装检查
  ```bash
  npm --version
  ```
- [ ] 前端项目初始化
  ```bash
  cd skills/mcda-core/web
  npm create vite@latest . --template react-ts
  npm install
  ```

#### 2.3 前端依赖
- [ ] React 18
- [ ] TypeScript 5
- [ ] Tailwind CSS 3
- [ ] React Router DOM
- [ ] Axios（API 调用）
- [ ] Recharts（图表库）

#### 2.4 开发工具
- [ ] VS Code 配置
  - [ ] Python 插件
  - [ ] React/TypeScript 插件
  - [ ] Tailwind CSS IntelliSense
- [ ] 浏览器 DevTools
- [ ] Postman（API 测试）

---

### 3. 一票否决机制准备 🔐

#### 3.1 代码骨架创建
- [ ] `skills/mcda-core/lib/constraints/` 目录
  - [ ] `__init__.py`
  - [ ] `models.py` - 数据模型
  - [ ] `evaluator.py` - 评估器
  - [ ] `filters.py` - 过滤器
- [ ] `skills/mcda-core/lib/services/constraint_service.py`
- [ ] 扩展 `skills/mcda-core/lib/models.py`（Criterion 添加 veto 字段）

#### 3.2 测试文件准备
- [ ] `tests/mcda-core/unit/test_constraints/` 目录
  - [ ] `__init__.py`
  - [ ] `test_models.py`
  - [ ] `test_evaluator.py`
  - [ ] `test_evaluator_hard.py`
  - [ ] `test_evaluator_soft.py`
  - [ ] `test_evaluator_tiered.py`
  - [ ] `test_evaluator_composite.py`
- [ ] `tests/mcda-core/unit/test_services/test_constraint_service.py`
- [ ] `tests/mcda-core/integration/test_constraints_integration.py`

#### 3.3 测试数据准备
- [ ] `tests/mcda-core/fixtures/`
  - [ ] `vendor_qualification.yaml` - 供应商准入场景
  - [ ] `project_risk_assessment.yaml` - 项目风险评估场景
  - [ ] `contract_risk_assessment.yaml` - 合同风险评估场景

#### 3.4 TDD 进度文件
- [ ] `docs/active/mcda-core/v0.10/tdd-veto-constraints.md`
  - [ ] RED Phase 测试列表
  - [ ] GREEN Phase 实现清单
  - [ ] REFACTOR Phase 优化项

---

### 4. Web UI 准备 🌐

#### 4.1 项目结构创建
- [ ] `skills/mcda-core/web/` 目录
  - [ ] `package.json`
  - [ ] `vite.config.ts`
  - [ ] `tsconfig.json`
  - [ ] `tailwind.config.js`
  - [ ] `index.html`
  - [ ] `src/` 目录结构
    - [ ] `App.tsx`
    - [ ] `main.tsx`
    - [ ] `components/`
    - [ ] `pages/`
    - [ ] `api/`
    - [ ] `types/`

#### 4.2 基础配置文件
- [ ] `vite.config.ts` - Vite 配置
- [ ] `tsconfig.json` - TypeScript 配置
- [ ] `tailwind.config.js` - Tailwind CSS 配置
- [ ] `postcss.config.js` - PostCSS 配置
- [ ] `.eslintrc.cjs` - ESLint 配置

#### 4.3 测试文件准备
- [ ] `tests/web/unit/components/` 目录
- [ ] `tests/web/integration/` 目录
- [ ] `tests/web/e2e/` 目录

#### 4.4 TDD 进度文件
- [ ] `docs/active/mcda-core/v0.10/tdd-web-ui.md`

---

### 5. API 接口准备 🔌

#### 5.1 项目结构创建
- [ ] `skills/mcda-core/api/` 目录
  - [ ] `__init__.py`
  - [ ] `main.py` - FastAPI 应用入口
  - [ ] `routers/` - 路由目录
    - [ ] `__init__.py`
    - [ ] `decisions.py`
    - [ ] `algorithms.py`
    - [ ] `constraints.py` - **新增**
  - [ ] `models/` - 数据模型
    - [ ] `__init__.py`
    - [ ] `schemas.py`
  - [ ] `services/` - 服务层
    - [ ] `__init__.py`
    - [ ] `decision_service.py`

#### 5.2 测试文件准备
- [ ] `tests/api/unit/test_routers/` 目录
- [ ] `tests/api/integration/test_services/` 目录
- [ ] `tests/api/e2e/` 目录

#### 5.3 TDD 进度文件
- [ ] `docs/active/mcda-core/v0.10/tdd-api.md`

---

### 6. 数据准备 📊

#### 6.1 用户模板
- [ ] `docs/active/mcda-core/v0.10/templates/` 目录
  - [ ] `vendor_qualification_template.yaml` - 供应商准入模板
  - [ ] `project_risk_template.yaml` - 项目风险评估模板
  - [ ] `contract_risk_template.yaml` - 合同风险评估模板

#### 6.2 配置示例
- [ ] 一票否决配置示例
  - [ ] 硬否决配置
  - [ ] 软否决配置
  - [ ] 分级否决配置
  - [ ] 组合否决配置

---

### 7. 依赖安装 📦

#### 7.1 Python 后端依赖
- [ ] FastAPI 依赖
  ```bash
  pip install fastapi==0.109.0
  pip install uvicorn[standard]==0.27.0
  pip install pydantic==2.5.3
  ```
- [ ] Web 框架依赖
  ```bash
  pip install jinja2==3.1.2
  pip install python-multipart==0.0.6
  pip install python-dotenv==1.0.0
  ```
- [ ] CORS 支持
  ```bash
  pip install fastapi-cors==0.0.6
  ```

#### 7.2 Node.js 前端依赖
- [ ] 核心依赖
  ```bash
  cd skills/mcda-core/web
  npm install react@18 react-dom@18
  npm install react-router-dom@6
  npm install typescript@5 @types/react @types/react-dom
  ```
- [ ] UI 库
  ```bash
  npm install tailwindcss@3 postcss autoprefixer
  npm install -D @tailwindcss/forms
  npm install recharts
  npm install axios
  npm install lucide-react
  ```

#### 7.3 开发工具依赖
- [ ] 测试工具
  ```bash
  npm install -D vitest @testing-library/react @testing-library/jest-dom
  npm install -D @testing-library/user-event
  npm install -D jsdom
  ```
- [ ] 代码质量工具
  ```bash
  npm install -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
  npm install -D prettier eslint-config-prettier
  ```

---

### 8. 文档模板准备 📝

#### 8.1 TDD 进度文件模板
- [ ] `tdd-veto-constraints.md` - 一票否决 TDD 进度
- [ ] `tdd-web-ui.md` - Web UI TDD 进度
- [ ] `tdd-api.md` - API TDD 进度

#### 8.2 用户文档模板
- [ ] 一票否决配置指南
- [ ] Web UI 使用指南
- [ ] API 使用指南

#### 8.3 完成报告模板
- [ ] `v0.10-completion-report.md`
- [ ] `v0.10-FINAL-SUMMARY.md`

---

## 🎯 准备工作验收标准

### 必须完成（P0）
- [ ] ADR-014 文档已完成 ✅
- [ ] v0.10 执行计划已创建 ✅
- [ ] Python 环境已配置 ✅
- [ ] Node.js 环境已安装
- [ ] 一票否决代码骨架已创建
- [ ] 测试文件准备完成
- [ ] 测试数据准备完成

### 建议完成（P1）
- [ ] 所有依赖已安装
- [ ] Web UI 项目已初始化
- [ ] API 项目结构已创建
- [ ] TDD 进度文件已创建
- [ ] 用户模板已准备

### 可选完成（P2）
- [ ] Docker 环境已配置
- [ ] Postman Collection 已创建
- [ ] E2E 测试环境已搭建

---

## 📊 准备工作统计

### 当前完成度

| 类别 | 项目数 | 已完成 | 待完成 | 完成率 |
|------|--------|--------|--------|--------|
| 文档准备 | 10 | 3 | 7 | 30% |
| 开发环境 | 8 | 1 | 7 | 12.5% |
| 一票否决 | 10 | 0 | 10 | 0% |
| Web UI | 8 | 0 | 8 | 0% |
| API 接口 | 6 | 0 | 6 | 0% |
| 数据准备 | 6 | 0 | 6 | 0% |
| 依赖安装 | 10 | 0 | 10 | 0% |
| 文档模板 | 6 | 0 | 6 | 0% |
| **总计** | **64** | **4** | **60** | **6.25%** |

---

## ⏭️ 下一步行动

### 立即执行（优先级排序）
1. ✅ **创建 v0.10 执行计划** - 已完成
2. **安装依赖**
   - [ ] Python 后端依赖（FastAPI）
   - [ ] Node.js 前端依赖（React + Tailwind）
3. **创建项目骨架**
   - [ ] 一票否决代码骨架
   - [ ] Web UI 项目初始化
   - [ ] API 项目结构
4. **准备测试数据**
   - [ ] YAML 配置文件
   - [ ] 测试 fixtures

---

**准备清单创建日期**: 2026-02-05
**准备清单创建人**: Claude Sonnet 4.5
**状态**: 📋 待开始执行

**预计准备完成时间**: 0.5 人日
