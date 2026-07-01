---
name: wip-code
description: 按 plan.md 执行编码，自动选择执行模式（当前会话/子代理驱动）
---

# wip-code

按模块执行计划（plan.md）逐步骤编写代码，**自动选择执行模式**。

## 核心机制

**wip-code 自动管理 Git Worktree**：
1. 开始编码前，自动基于当前分支创建 `feature/{project}-{module}` 分支
2. 在 `.wip/worktrees/{project}/{module}/` 独立工作区中编码，不影响主分支
3. 全部步骤完成后，自动合并 feature 分支回基分支
4. 合并后自动清理 worktree 目录和 feature 分支

> Worktree 操作（创建/列出/合并/清理）由 AI 直接执行 `git worktree` 和 `git branch` 命令，无需外部脚本。

## 执行模式（自动判断）

| 信号 | 当前会话执行 | 子代理驱动 |
|------|-------------|-----------|
| Task/Step 数量 | ≤3 个 | >3 个 |
| 复杂度 | 单文件修改 | 多文件协调 |
| 风险等级 | 低风险 | 高风险（核心逻辑） |
| 测试要求 | 简单单元测试 | 复杂集成测试 |

## 模式 A：当前会话执行

- 在当前 Claude 会话中逐步执行
- 适合：简单任务、快速修复
- 流程：读取 plan.md → 按 Step 执行 → 验证 → 提交

## 模式 B：子代理驱动 ★

- 每个 Step 派独立子代理执行
- 实现子代理 → 审查子代理 → 修复子代理
- 质量更高，适合复杂任务

### 子代理驱动流程

```
读取 plan.md
    │
    ├── Step N: 派实现子代理 (implementer)
    │       └── 输出：状态 + 提交 + 测试
    ├── 生成审查包
    ├── 派审查子代理 (reviewer)
    │       └── 输出：规格符合性 + 发现清单
    ├── 判断结果
    │   ├── 通过 → 下一步
    │   └── 需修复 → 派修复子代理 (fixer)
    └── 循环直到通过
```

### 子代理提示词位置

- `skills/wip-code/subagents/implementer.md`（实现子代理）
- `skills/wip-code/subagents/reviewer.md`（审查子代理）
- `skills/wip-code/subagents/fixer.md`（修复子代理）

## 通用执行要求

1. **自动创建 worktree**：基于当前分支创建 feature 分支和独立工作区
2. 执行前用 `git status` 确认工作区干净
3. 按 Step 模板顺序逐一执行，根据复杂度自动选择当前会话或子代理驱动模式
4. 每步执行：编码 → 验证（编译/单测）→ 提交，通过后再进行下一步
5. 若某步骤失败，暂停并报告问题，等待人工介入
6. 若发现 plan.md 与实际代码有出入，先回写更新 plan.md 再继续，保持文档与代码同步
7. 全部步骤完成后做格式扫尾：确保新增代码与项目既有风格统一
8. **自动合并**：所有 Step 通过后，将 feature 分支合并回基分支，清理 worktree
9. **自动更新 ledger.md**：记录每步完成状态和合并信息
