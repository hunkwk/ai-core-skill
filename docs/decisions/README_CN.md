# 架构决策记录

本目录包含重要技术决策的架构决策记录（ADR）。

## 什么是 ADR？

ADR 记录：
- **上下文**: 什么问题？
- **决策**: 做了什么决定？
- **后果**: 意味着什么？

## 文件命名

```
{编号}-{简短标题}.md

示例:
  001-use-redis-vectors.md
  002-flat-skill-structure.md
  003-git-flow-simplified.md
```

## 模板

```markdown
# ADR-XXX: [决策标题]

## 状态
Proposed（提议）| Accepted（已接受）| Deprecated（已废弃）| Superseded（被替代）

## 上下文
[描述问题或当前状态]

## 决策
[描述做出的决定]

## 后果
- **正面**: [好处]
- **负面**: [代价]

## 相关
- 链接: [相关 issue/commit]
- 作者: hunkwk
- 日期: YYYY-MM-DD
```

## 使用方法

当做出重要技术决策时：
1. 复制 `template.md`
2. 填写 ADR 内容
3. 按顺序编号（001, 002, 003...）
4. 提交决策

---

**参见**: [ADR 模板](template.md)
