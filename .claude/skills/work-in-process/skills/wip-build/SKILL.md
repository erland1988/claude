---
name: wip-build
description: 生成设计文档（总体+模块），自动判断模块数量并命名
---

# wip-build

生成设计文档（总体设计 + 模块设计），**自动判断模块数量**并根据职责**自动命名**。

## 执行流程

1. 读取当前项目代码结构，理解技术栈、命名风格
2. 与用户对话澄清需求（背景、范围、约束）
3. **自动判断模块数量**：
   - **简单需求**：单模块，自动命名（如 `core`, `validator`）
   - **复杂需求**：自动拆分多个模块
4. **智能模块命名**（根据职责）：
   | 模块职责 | 自动命名示例 |
   |---------|-------------|
   | 数据模型定义 | `data-models` |
   | 数据库迁移 | `db-migrations` |
   | 业务逻辑实现 | `business-logic` |
   | API 接口层 | `api-endpoints` |
   | 权限校验 | `auth-validation` |
5. 生成分层设计文档：
   - **总体设计** → `.wip/{name}/design.md`
   - **模块设计** → `.wip/{name}/modules/{module}/design.md`
6. **自动更新 ledger.md**
