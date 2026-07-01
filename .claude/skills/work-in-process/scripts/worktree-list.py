#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WIP Worktree 列表脚本
列出所有 worktree 及其状态
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


def list_worktrees():
    """列出所有 worktree"""
    success, stdout, stderr = run_git(['worktree', 'list', '--porcelain'])
    if not success:
        print(f"[ERROR] 获取 worktree 列表失败: {stderr}", file=sys.stderr)
        return []
    
    worktrees = []
    current_worktree = {}
    
    for line in stdout.strip().split('\n'):
        if line.startswith('worktree '):
            if current_worktree:
                worktrees.append(current_worktree)
            current_worktree = {'path': line[9:]}
        elif line.startswith('HEAD '):
            current_worktree['head'] = line[5:]
        elif line.startswith('branch '):
            current_worktree['branch'] = line[7:].replace('refs/heads/', '')
        elif line.startswith('detached'):
            current_worktree['detached'] = True
    
    if current_worktree:
        worktrees.append(current_worktree)
    
    return worktrees


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


def get_wip_worktrees(wip_root=None):
    """获取 .wip 下的 worktree"""
    if wip_root is None:
        project_root = get_project_root()
        wip_root = project_root / '.wip'
    worktrees_dir = wip_root / 'worktrees'
    if not worktrees_dir.exists():
        return []
    
    wip_worktrees = []
    for project_dir in worktrees_dir.iterdir():
        if project_dir.is_dir():
            for module_dir in project_dir.iterdir():
                if module_dir.is_dir():
                    wip_worktrees.append({
                        'project': project_dir.name,
                        'module': module_dir.name,
                        'path': module_dir
                    })
    return wip_worktrees


def main():
    # 获取所有 worktree
    all_worktrees = list_worktrees()
    
    if not all_worktrees:
        print("没有 worktree")
        sys.exit(0)
    
    print(f"共 {len(all_worktrees)} 个 worktree:\n")
    
    # 找到主工作区
    main_worktree = None
    feature_worktrees = []
    
    for wt in all_worktrees:
        if '.wip/worktrees' not in wt['path']:
            main_worktree = wt
        else:
            feature_worktrees.append(wt)
    
    # 显示主工作区
    if main_worktree:
        print(f"[主工作区]")
        print(f"  路径: {main_worktree['path']}")
        print(f"  分支: {main_worktree.get('branch', 'N/A')}")
        print()
    
    # 按项目分组显示 feature worktree
    if feature_worktrees:
        print("[模块工作区]")
        
        # 按项目分组
        by_project = {}
        for wt in feature_worktrees:
            parts = wt['path'].split('.wip/worktrees/')
            if len(parts) > 1:
                project_module = parts[1].replace('\\', '/')
                project = project_module.split('/')[0] if '/' in project_module else 'unknown'
                if project not in by_project:
                    by_project[project] = []
                by_project[project].append(wt)
        
        for project, worktrees in sorted(by_project.items()):
            print(f"\n  项目: {project}")
            for wt in worktrees:
                branch = wt.get('branch', 'N/A')
                module = branch.split('-')[-1] if '-' in branch else 'unknown'
                status = "detached" if wt.get('detached') else "attached"
                print(f"    - {module}")
                print(f"      分支: {branch}")
                print(f"      路径: {wt['path']}")


def main_simple():
    """简化版本，只列出 .wip/worktrees 下的目录"""
    project_root = get_project_root()
    wip_root = project_root / '.wip'

    if not wip_root.exists():
        print("[ERROR] 未找到 .wip 目录", file=sys.stderr)
        sys.exit(1)

    worktrees_dir = wip_root / 'worktrees'
    if not worktrees_dir.exists():
        print("没有 worktree")
        sys.exit(0)
    
    print("Worktree 列表:\n")
    
    for project_dir in sorted(worktrees_dir.iterdir()):
        if project_dir.is_dir():
            print(f"项目: {project_dir.name}")
            for module_dir in sorted(project_dir.iterdir()):
                if module_dir.is_dir():
                    print(f"  - {module_dir.name}")
                    print(f"    路径: {module_dir}")


if __name__ == '__main__':
    # 尝试完整版本，失败则使用简化版
    try:
        main()
    except Exception as e:
        main_simple()
