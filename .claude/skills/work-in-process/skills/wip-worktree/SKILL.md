---
name: wip-worktree
description: Git Worktree 管理（创建/列出/合并/清理）
---

# wip-worktree

Git Worktree 管理，实现独立分支并行开发。

## 子命令

### `wip-worktree create [project] [module]`

为指定模块创建 Git Worktree。

**执行流程**：
1. 读取当前分支（作为基分支）
2. 创建 feature 分支：`feature/{project}-{module}`
3. 创建 worktree 目录：`.wip/worktrees/{project}/{module}/`
4. 切回基分支

### `wip-worktree list`

列出所有 worktree 及其状态。

### `wip-worktree merge [project] [module]`

将模块分支合并回基分支。

### `wip-worktree clean [project] [module]`

清理已合并的 worktree。

## 脚本位置

- `skills/wip-worktree/scripts/create.py`
- `skills/wip-worktree/scripts/list.py`
- `skills/wip-worktree/scripts/merge.py`
- `skills/wip-worktree/scripts/clean.py`
