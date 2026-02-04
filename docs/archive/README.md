# 归档目录

**用途**: 保存已完成的版本文档和历史记录

## 📋 目录结构

```
archive/
└── {feature}/              # 功能模块
    ├── v0.1/               # 版本归档
    │   ├── active/         # 旧的工作进度文件
    │   ├── plans/          # 旧的执行计划
    │   └── reports/        # 旧的测试报告
    ├── v0.2/
    └── deprecated/         # 废弃的文档
        └── old-design.md
```

## 📦 归档内容

- ✅ 旧版本的 `active/` 工作进度文件
- ✅ 旧版本的 `plans/` 执行计划
- ✅ 旧版本的 `reports/` 测试报告
- ✅ 过时的参考文档和设计文档

## 🔄 归档时机

- 版本发布并创建 checkpoint 后
- 文档内容被新版本替代后
- 临时文档不再需要引用后

## 🔗 相关文档

- [文档架构原则](../documentation-architecture-v2.md)
- [Checkpoint 目录](../checkpoints/)
- [当前工作目录](../active/)
