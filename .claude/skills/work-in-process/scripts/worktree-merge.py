#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WIP Worktree 合并脚本
将模块分支合并回基分支
"""

import os
import sys
import subprocess
from pathlib import Path


def run_git(args, cwd=None):
    """运行 git 命令"""
    result = subprocess.run(
        ['git'] + args,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout, result.stderr


def get_current_branch():
    """获取当前分支"""
    success, stdout, _ = run_git(['branch', '--show-current'])
    return stdout.strip() if success else None


def merge_worktree(project_name, module_name):
    """合并 worktree"""
    feature_branch = f"feature/{project_name}-{module_name}"
    
    # 获取当前分支（目标分支）
    target_branch = get_current_branch()
    if not target_branch:
        print("[ERROR] 无法获取当前分支", file=sys.stderr)
        sys.exit(1)
    
    print(f"准备合并: {feature_branch} -> {target_branch}")
    
    # 检查分支是否存在
    success, _, _ = run_git(['show-ref', '--verify', f'refs/heads/{feature_branch}'])
    if not success:
        print(f"[ERROR] 分支不存在: {feature_branch}", file=sys.stderr)
        sys.exit(1)
    
    # 检查是否有未提交的更改
    success, stdout, _ = run_git(['status', '--porcelain'])
    if stdout.strip():
        print("[WARN] 当前分支有未提交的更改")
        print("请先提交或暂存更改，然后再合并")
        sys.exit(1)
    
    # 拉取最新代码（如果有远程）
    run_git(['fetch', 'origin'])
    
    # 合并分支
    success, stdout, stderr = run_git(['merge', '--no-ff', feature_branch, '-m', 
                                      f"Merge {feature_branch} into {target_branch}"])
    if not success:
        print(f"[ERROR] 合并失败: {stderr}", file=sys.stderr)
        print("可能需要手动解决冲突")
        sys.exit(1)
    
    # 获取合并提交哈希
    success, commit_hash, _ = run_git(['rev-parse', '--short', 'HEAD'])
    commit_hash = commit_hash.strip() if success else 'unknown'
    
    print(f"\n[OK] 合并成功")
    print(f"  源分支: {feature_branch}")
    print(f"  目标分支: {target_branch}")
    print(f"  提交: {commit_hash}")
    
    return commit_hash


def main():
    if len(sys.argv) < 3:
        print("用法: worktree-merge.py <project> <module>")
        print("\n示例:")
        print('  worktree-merge.py order-system data-models')
        print('  worktree-merge.py order-system business-logic')
        print("\n注意: 在当前分支执行，合并 feature/{project}-{module} 到当前分支")
        sys.exit(1)
    
    project_name = sys.argv[1]
    module_name = sys.argv[2]
    
    commit_hash = merge_worktree(project_name, module_name)
    
    # 输出用于 ledger 更新
    print(f"\n[LEDGER] {commit_hash}")


if __name__ == '__main__':
    main()
