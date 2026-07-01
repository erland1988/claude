---
name: wip-init
description: 初始化 .wip/ 项目结构，中文描述智能推荐英文项目名
---

# wip-init

初始化 `.wip/` 项目结构，支持中文描述智能推荐英文项目名。

## 执行流程

1. 询问项目描述（中文，如"订单系统重构"）
2. **智能命名**：分析描述关键词，推荐 2-3 个英文项目名选项
   - 命名规范：kebab-case（短横线连接）
   - 示例：
     | 中文描述 | 推荐选项 |
     |---------|---------|
     | 订单系统重构 | order-system-refactor / order-refactoring / order-v2 |
     | 用户权限改造 | user-auth-upgrade / permission-system / user-center-auth |
3. 用户选择或自定义项目名
4. 创建目录结构：
   ```
   .wip/{project-name}/
   ├── design.md              # 总体设计骨架
   ├── modules/               # 模块目录
   │   └── {module-name}/     # 自动命名单模块
   │       └── design.md      # 模块设计骨架
   └── ledger.md              # 进度账本
   ```
5. **自动更新 ledger.md**：记录项目创建
6. 将 `.wip/` 加入 `.gitignore`

> **重要**：wip-init 执行后进入**需求讨论阶段**，原则上只讨论需求、设计方案和执行计划，**不编写代码**。编码从 `wip-code` 开始。

## 依赖

- Python 3.7+
- 脚本: `scripts/project-init.py`
