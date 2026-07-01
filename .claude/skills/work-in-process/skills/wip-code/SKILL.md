---
name: wip-code
description: 按 plan.md 执行编码，自动选择执行模式（当前会话/子代理驱动）
---

# wip-code

按模块执行计划（plan.md）逐步骤编写代码，**自动选择执行模式**。

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
    │       └── 输出：STATUS + COMMITS + TESTS
    ├── 生成审查包
    ├── 派审查子代理 (reviewer)
    │       └── 输出：SPEC_COMPLIANCE + FINDINGS
    ├── 判断结果
    │   ├── 通过 → 下一步
    │   └── 需修复 → 派修复子代理 (fixer)
    └── 循环直到通过
```

### 子代理提示词位置

- `skills/wip-code/subagents/implementer.md`
- `skills/wip-code/subagents/reviewer.md`
- `skills/wip-code/subagents/fixer.md`

## 通用执行要求

1. 执行前用 `git status` 确认工作区干净
2. 按 Step 模板执行：文件 / 位置 / 操作 / 验证
3. 若发现 plan.md 与实际代码有出入，先回写更新
4. 每步验证通过后再进行下一步
5. **自动更新 ledger.md**
