# 文档架构原则 v2.0

**更新时间**: 2026-02-01
**版本**: v2.0
**状态**: ✅ 生效

---

## 🎯 核心设计理念

**按文档特性选择分层策略**：
- **永久性文档** → `{type}/{feature}/` (不包含版本)
- **临时性文档** → `{type}/{feature}/v{version}/` (包含版本)

---

## 📊 两大目录类型

### 类型 A: Feature 子目录（不包含版本号）

**适用场景**: 永久性、跨版本、积累型文档

```
requirements/{feature}/
├── requirements.md
└── README.md

decisions/{feature}/
├── 001-design-decision.md
├── 002-api-design.md
└── README.md

checkpoints/{feature}/
├── checkpoint-complete.md    # 单一真相来源
├── checkpoint-v0.3.md        # 版本里程碑
└── checkpoint-v0.3-phase2.md # 阶段里程碑

archive/{feature}/
├── v0.1/
│   ├── active/
│   ├── plans/
│   └── reports/
└── v0.2/
    └── ...
```

**特点**:
- ✅ 跨版本共享（requirements、decisions）
- ✅ 随时间积累（checkpoints）
- ✅ 不需要版本隔离

---

### 类型 B: Feature + Version 子目录（包含版本号）

**适用场景**: 临时性、版本隔离、迭代型文档

```
plans/{feature}/
├── v0.1/
├── v0.2/
├── v0.3/
└── v0.4/
    └── execution-plan.md

active/{feature}/
├── v0.1/
├── v0.2/
└── v0.3/
    ├── tdd-todim.md
    ├── fix-bug-name.md
    └── refactor-target.md

reports/{feature}/
├── v0.1/
├── v0.2/
└── v0.3/
    └── test-report-v0.3.md
```

**特点**:
- ✅ 版本隔离清晰
- ✅ 完成后归档到 `archive/`
- ✅ 便于回溯历史版本

---

## 📋 文档生命周期

```
plans (draft)
    ↓
active (in_progress)
    ↓
reports (completed)
    ↓
archive (historical)

                ↓
         checkpoints (milestones)
```

---

## 📁 完整目录示例（mcda-core）

```
docs/
├── requirements/
│   └── mcda-core/
│       ├── requirements.md
│       └── README.md
│
├── decisions/
│   └── mcda-core/
│       ├── 001-algorithms-architecture.md
│       ├── 002-normalization-methods.md
│       ├── 003-weighting-roadmap.md
│       └── README.md
│
├── plans/
│   └── mcda-core/
│       ├── v0.1/
│       ├── v0.2/
│       ├── v0.3/
│       └── v0.4/
│           └── advanced-features-execution-plan.md
│
├── active/
│   └── mcda-core/
│       └── v0.4/
│           ├── tdd-todim.md
│           └── fix-electre-kernel.md
│
├── reports/
│   └── mcda-core/
│       ├── v0.1/
│       ├── v0.2/
│       └── v0.3/
│           └── test-report-v0.3.md
│
├── checkpoints/
│   └── mcda-core/
│       ├── checkpoint-complete.md
│       ├── checkpoint-v0.3-phase2.md
│       └── checkpoint-v0.3-complete.md
│
└── archive/
    └── mcda-core/
        ├── v0.1/
        │   ├── active/
        │   ├── plans/
        │   └── reports/
        └── v0.2/
            ├── active/
            ├── plans/
            └── reports/
```

---

## 🔄 版本开发流程

**1. 创建版本规划**:
```bash
# 创建计划文档
docs/plans/{feature}/v{version}/execution-plan.md
```

**2. 创建工作目录**:
```bash
# 创建空目录供 AI 使用
docs/active/{feature}/v{version}/
```

**3. 开发阶段**:
- AI 在 `active/` 下创建进度文件（tdd-*.md、fix-*.md 等）
- 实时追踪开发进度

**4. 完成版本**:
```bash
# 创建测试报告
docs/reports/{feature}/v{version}/test-report.md

# 更新里程碑
docs/checkpoints/{feature}/checkpoint-complete.md
docs/checkpoints/{feature}/checkpoint-v{version}.md
```

**5. 归档**:
```bash
# 移动到归档目录
mv docs/active/{feature}/v{version}/ docs/archive/{feature}/v{version}/active/
mv docs/plans/{feature}/v{version}/ docs/archive/{feature}/v{version}/plans/
```

---

## 📊 快速参考

| 文档类型 | 目录位置 | 是否包含版本 | 归档时机 |
|---------|---------|-------------|---------|
| 需求文档 | `requirements/{feature}/` | ❌ | 不归档（持续更新） |
| 架构决策 | `decisions/{feature}/` | ❌ | 不归档（状态标记为 DEPRECATED） |
| 执行计划 | `plans/{feature}/v{version}/` | ✅ | 版本完成后 |
| 进度追踪 | `active/{feature}/v{version}/` | ✅ | 版本完成后 |
| 测试报告 | `reports/{feature}/v{version}/` | ✅ | 版本完成后 |
| 里程碑 | `checkpoints/{feature}/` | ❌ | 不归档（持续积累） |
| 旧文档 | `archive/{feature}/v{version}/` | ✅ | 永久归档 |

---

## 🎯 关键原则

1. **类型 A（永久）vs 类型 B（临时）**: 根据文档特性选择
2. **版本隔离**: `plans/active/reports` 必须包含版本号
3. **单一真相来源**: `checkpoint-complete.md` 是功能级别的完整里程碑
4. **归档原则**: 版本完成后，临时文档归档到 `archive/`
5. **不重复**: 避免在多个地方维护相同内容

---

**创建者**: hunkwk + AI collaboration
**审核**: ✅ 已批准
**生效时间**: 2026-02-01
