---
name: wip-init
description: 初始化 .wip/ 项目结构，中文描述智能推荐英文项目名
---

# wip-init

初始化 `.wip/` 项目结构，支持中文描述智能推荐英文项目名。**所有操作由 AI 直接执行，无需调用外部脚本。**

## 完整执行流程

### 步骤 1：获取项目描述

用户可能已提供描述，如果没有，主动询问：

> 请描述你要开发的项目或需求（中文），例如："订单系统重构""用户权限改造""支付模块优化"

### 步骤 2：智能命名

根据用户的中文描述，AI 分析关键词并推荐 2-3 个英文项目名。

**命名规范**：kebab-case（全小写短横线），如 `order-system-refactor`

向用户展示推荐选项，等待用户确认（输入序号或自定义名称）。

向用户展示推荐选项，询问：

```
推荐以下项目名，请选择或自定义：

1. {option1}
2. {option2}
3. {option3}

输入序号（默认 1），或直接输入自定义名称（kebab-case）：
```

用户选择后确定 `project_name`：
- 如果输入纯数字 → 取对应序号的推荐名
- 如果输入字符串 → 转为 kebab-case 后使用（替换 `_` 和空格为 `-`，移除特殊字符，全小写）

### 步骤 3：创建目录结构

在当前工作区的项目根目录下执行：

```bash
mkdir -p ".wip/{project_name}/modules/core"
```

如果 `.wip/` 目录已存在，无需重复创建根目录。

### 步骤 4：生成 design.md（总体设计骨架）

写入 `.wip/{project_name}/design.md`：

```markdown
# {project_name} 总体设计

## 参考资料

## 需求背景
- 触发条件：
- 范围边界：
- 前置校验：
- 状态约束：
- 幂等语义：

## 设计方案

### 总体思路

### 架构概要

### 关键决策

## 模块划分

| 模块 | 说明 | 状态 |
|------|------|------|
| core | 待定义 | ⬜ |

## 变更文件汇总（预估）

## 依赖关系图
```

### 步骤 5：生成 modules/core/design.md（模块设计骨架）

写入 `.wip/{project_name}/modules/core/design.md`：

```markdown
# core 设计

## 模块边界

### 职责

### 不做的事

### 接口契约

## 数据模型

## 状态机（如有）

## 实现思路

## 预估变更
| 文件 | 操作 | 说明 |
|------|------|------|

## 依赖
- 前置模块: 无
- 后置模块: 无
```

### 步骤 6：生成 ledger.md（进度账本）

写入 `.wip/{project_name}/ledger.md`：

```markdown
# 项目进度账本: {project_name}

## 项目信息
- 名称: {project_name}
- 创建时间: {YYYY-MM-DD HH:mm:ss}
- 当前阶段: design
- 最后更新: {YYYY-MM-DD HH:mm:ss}

## 模块进度
| 模块 | 设计 | 计划 | worktree | 编码 | 审查 | 合并 |
|------|------|------|----------|------|------|------|
| core | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

## 详细日志
| 时间 | 模块 | 动作 | 详情 | 提交 |
|------|------|------|------|------|
| {HH:mm} | - | project_init | 项目初始化 | - |

## 阻塞问题
<!-- 如有 BLOCKED 状态记录这里 -->
```

> `{YYYY-MM-DD HH:mm:ss}` 和 `{HH:mm}` 替换为执行时的实际时间。

### 步骤 7：检查飞书配置

检查 `.wip/config.json` 是否存在：

```bash
test -f .wip/config.json && echo "EXISTS" || echo "NOT_FOUND"
```

如果不存在 → 创建：

```json
{
  "appId": "",
  "appSecret": "",
  "folderName": "work-in-process"
}
```

> 用户后续填入飞书应用的 `appId` 和 `appSecret` 后，`wip-feishu-upload` 等命令即可使用。

### 步骤 9：更新 .gitignore

检查项目根目录的 `.gitignore`：
- 如果文件不存在 → 创建并写入 `.wip/`
- 如果文件存在但无 `.wip/` 条目 → 追加 `.wip/`
- 如果已有 `.wip/` 条目 → 跳过

### 步骤 10：输出确认

### 步骤 9：输出确认

目录结构创建完成后，向用户汇报：

```
✅ 项目 {project_name} 已初始化

📁 .wip/{project_name}/
   ├── design.md          ← 总体设计（待 wip-build 填充）
   ├── modules/
   │   └── core/
   │       └── design.md  ← 模块设计（待 wip-build 填充）
   └── ledger.md          ← 进度账本

📋 下一步：
   - 讨论需求细节
   - 执行 wip-build 生成分模块设计

> ⚠️ 当前为需求讨论阶段，原则上不编写代码。编码从 wip-code 开始。
```

## 异常处理

| 情况 | 处理方式 |
|------|---------|
| `.wip/{project_name}` 已存在 | 提示用户项目已存在，询问是否覆盖或换名 |
| 用户输入无效序号 | 提示重新选择，默认使用选项 1 |
| 项目名包含非法字符 | 自动清理：替换 `_` 和空格为 `-`，移除 `[^\w\-]`，转小写 |

## 与 wip-build 的衔接

wip-init 只创建单模块骨架（`modules/core/`），后续：
- `wip-build` 根据需求分析，将 `core` 拆分为多个模块
- `wip-build` 填充各模块的设计文档
