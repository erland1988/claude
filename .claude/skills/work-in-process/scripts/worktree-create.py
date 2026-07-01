#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WIP Worktree 创建脚本
为指定模块创建独立的工作目录和分支
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


def get_wip_root():
    """获取 .wip 目录路径"""
    current = Path.cwd()
    while current != current.parent:
        wip = current / '.wip'
        if wip.exists():
            return current, wip
        current = current.parent
    return None, None


def create_worktree(project_name, module_name):
    """创建 worktree"""
    repo_root, wip_root = get_wip_root()
    if not repo_root:
        print("[ERROR] 未找到 .wip 目录", file=sys.stderr)
        sys.exit(1)
    
    # 获取当前分支（基分支）
    base_branch = get_current_branch()
    if not base_branch:
        print("[ERROR] 无法获取当前分支", file=sys.stderr)
        sys.exit(1)
    
    # 构建 feature 分支名
    feature_branch = f"feature/{project_name}-{module_name}"
    
    # worktree 路径
    worktree_path = wip_root / 'worktrees' / project_name / module_name
    
    # 检查分支是否已存在
    success, _, _ = run_git(['show-ref', '--verify', f'refs/heads/{feature_branch}'])
    if success:
        print(f"[WARN] 分支 {feature_branch} 已存在")
    else:
        # 创建新分支（基于当前分支）
        success, _, stderr = run_git(['checkout', '-b', feature_branch])
        if not success:
            print(f"[ERROR] 创建分支失败: {stderr}", file=sys.stderr)
            sys.exit(1)
        print(f"[OK] 创建分支: {feature_branch} (基于 {base_branch})")
    
    # 创建 worktree 目录
    worktree_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 添加 worktree
    if worktree_path.exists():
        print(f"[WARN] worktree 目录已存在: {worktree_path}")
    else:
        success, _, stderr = run_git([
            'worktree', 'add', 
            str(worktree_path),
            feature_branch
        ])
        if not success:
            print(f"[ERROR] 创建 worktree 失败: {stderr}", file=sys.stderr)
            sys.exit(1)
        print(f"[OK] 创建 worktree: {worktree_path}")
    
    # 切回基分支
    run_git(['checkout', base_branch])
    
    print(f"\n[OK] worktree 创建成功")
    print(f"  基分支: {base_branch}")
    print(f"  功能分支: {feature_branch}")
    print(f"  工作目录: {worktree_path}")
    print(f"\n使用方式:")
    print(f"  cd {worktree_path}")
    print(f"  # 在此目录执行编码...")


def main():
    if len(sys.argv) < 3:
        print("用法: worktree-create.py <project> <module>")
        print("\n示例:")
        print('  worktree-create.py order-system data-models')
        print('  worktree-create.py order-system business-logic')
        sys.exit(1)
    
    project_name = sys.argv[1]
    module_name = sys.argv[2]
    
    create_worktree(project_name, module_name)


if __name__ == '__main__':
    main()
