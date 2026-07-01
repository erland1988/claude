#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WIP Worktree 清理脚本
移除已合并的 worktree
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def get_project_root():
    """获取项目根目录"""
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


def run_git(args, cwd=None):
    """运行 git 命令"""
    result = subprocess.run(
        ['git'] + args,
        cwd=cwd,
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout, result.stderr


def clean_worktree(project_name, module_name, force=False):
    """清理 worktree"""
    project_root = get_project_root()
    wip_root = project_root / '.wip'
    if not wip_root.exists():
        print("[ERROR] 未找到 .wip 目录", file=sys.stderr)
        sys.exit(1)
    
    feature_branch = f"feature/{project_name}-{module_name}"
    worktree_path = wip_root / 'worktrees' / project_name / module_name
    
    # 检查 worktree 是否存在
    if not worktree_path.exists():
        print(f"[WARN] worktree 不存在: {worktree_path}")
        return
    
    # 检查分支是否已合并
    if not force:
        success, _, _ = run_git(['branch', '--merged'])
        # 简化检查：询问用户确认
        print(f"即将移除 worktree: {worktree_path}")
        print(f"关联分支: {feature_branch}")
        response = input("确认移除? (y/N): ").strip().lower()
        if response != 'y':
            print("已取消")
            return
    
    # 移除 worktree（git worktree remove）
    success, _, stderr = run_git(['worktree', 'remove', str(worktree_path)])
    if not success:
        # 如果 git remove 失败，强制删除目录
        print(f"[WARN] git worktree remove 失败，尝试强制删除: {stderr}")
        try:
            shutil.rmtree(worktree_path)
            print(f"[OK] 已删除目录: {worktree_path}")
        except Exception as e:
            print(f"[ERROR] 删除失败: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"[OK] 已移除 worktree: {worktree_path}")
    
    # 询问是否删除分支
    success, _, _ = run_git(['show-ref', '--verify', f'refs/heads/{feature_branch}'])
    if success:
        response = input(f"是否删除分支 {feature_branch}? (y/N): ").strip().lower()
        if response == 'y':
            success, _, stderr = run_git(['branch', '-d', feature_branch])
            if success:
                print(f"[OK] 已删除分支: {feature_branch}")
            else:
                print(f"[WARN] 删除分支失败: {stderr}")
                print("可能分支未完全合并，如需强制删除请使用: git branch -D " + feature_branch)


def main():
    if len(sys.argv) < 3:
        print("用法: worktree-clean.py <project> <module> [--force]")
        print("\n示例:")
        print('  worktree-clean.py order-system data-models')
        print('  worktree-clean.py order-system data-models --force')
        sys.exit(1)
    
    project_name = sys.argv[1]
    module_name = sys.argv[2]
    force = '--force' in sys.argv or '-f' in sys.argv
    
    clean_worktree(project_name, module_name, force)


if __name__ == '__main__':
    main()
