#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WIP Worktree 创建脚本"""

import os
import sys
import subprocess
from pathlib import Path


def run_git(args, cwd=None):
    """运行 git 命令"""
    result = subprocess.run(['git'] + args, cwd=cwd, capture_output=True, text=True)
    return result.returncode == 0, result.stdout, result.stderr


def get_project_root():
    """获取项目根目录（包含 .wip 的目录）"""
    current = Path.cwd()
    if '.claude' in str(current):
        while current.name != '.claude' and current != current.parent:
            current = current.parent
        if current.name == '.claude':
            return current.parent
    check = current
    while check != check.parent:
        if (check / '.wip').exists():
            return check
        check = check.parent
    return current


def get_current_branch():
    """获取当前分支"""
    success, stdout, _ = run_git(['branch', '--show-current'])
    return stdout.strip() if success else None


def create_worktree(project_name, module_name):
    """创建 worktree"""
    project_root = get_project_root()
    wip_root = project_root / '.wip'

    base_branch = get_current_branch()
    if not base_branch:
        print("[ERROR] 无法获取当前分支", file=sys.stderr)
        sys.exit(1)

    feature_branch = f"feature/{project_name}-{module_name}"
    worktree_path = wip_root / 'worktrees' / project_name / module_name

    # 创建分支
    success, _, _ = run_git(['show-ref', '--verify', f'refs/heads/{feature_branch}'])
    if success:
        print(f"[WARN] 分支 {feature_branch} 已存在")
    else:
        success, _, stderr = run_git(['checkout', '-b', feature_branch])
        if not success:
            print(f"[ERROR] 创建分支失败: {stderr}", file=sys.stderr)
            sys.exit(1)
        print(f"[OK] 创建分支: {feature_branch} (基于 {base_branch})")

    # 创建 worktree
    worktree_path.parent.mkdir(parents=True, exist_ok=True)

    if worktree_path.exists():
        print(f"[WARN] worktree 目录已存在: {worktree_path}")
    else:
        success, _, stderr = run_git(['worktree', 'add', str(worktree_path), feature_branch])
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


def main():
    if len(sys.argv) < 3:
        print("用法: worktree-create.py <project> <module>")
        sys.exit(1)

    create_worktree(sys.argv[1], sys.argv[2])


if __name__ == '__main__':
    main()
