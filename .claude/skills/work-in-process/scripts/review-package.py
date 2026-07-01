#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WIP Review Package 生成脚本
生成审查包（diff 文件），供 reviewer 子代理使用
"""

import os
import sys
import subprocess
import tempfile
from datetime import datetime
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


def get_wip_root():
    """获取 .wip 目录路径"""
    current = Path.cwd()
    while current != current.parent:
        wip = current / '.wip'
        if wip.exists():
            return current, wip
        current = current.parent
    return None, None


def generate_review_package(project_name, module_name, base_commit='HEAD~1'):
    """
    生成审查包
    base_commit: 比较的基础提交（默认 HEAD~1，即上一个提交）
    """
    repo_root, wip_root = get_wip_root()
    if not repo_root:
        print("[ERROR] 未找到 .wip 目录", file=sys.stderr)
        sys.exit(1)
    
    worktree_path = wip_root / 'worktrees' / project_name / module_name
    
    if not worktree_path.exists():
        print(f"[ERROR] worktree 不存在: {worktree_path}", file=sys.stderr)
        sys.exit(1)
    
    # 获取提交范围
    success, head_commit, _ = run_git(['rev-parse', '--short', 'HEAD'], cwd=worktree_path)
    if not success:
        print("[ERROR] 无法获取 HEAD 提交", file=sys.stderr)
        sys.exit(1)
    head_commit = head_commit.strip()
    
    # 获取提交日志
    success, commit_log, _ = run_git(
        ['log', '--oneline', f'{base_commit}..HEAD'],
        cwd=worktree_path
    )
    if not success:
        commit_log = "(无法获取)"
    
    # 获取 diff stat
    success, diff_stat, _ = run_git(
        ['diff', '--stat', f'{base_commit}..HEAD'],
        cwd=worktree_path
    )
    if not success:
        diff_stat = "(无法获取)"
    
    # 获取完整 diff
    success, diff_content, _ = run_git(
        ['diff', '-U10', f'{base_commit}..HEAD'],
        cwd=worktree_path
    )
    if not success:
        print(f"[ERROR] 无法生成 diff: {diff_content}", file=sys.stderr)
        sys.exit(1)
    
    # 生成审查包文件
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_filename = f"review-package-{project_name}-{module_name}-{timestamp}.md"
    package_path = wip_root / 'review-packages' / project_name / module_name
    package_path.mkdir(parents=True, exist_ok=True)
    package_file = package_path / package_filename
    
    package_content = f"""# Review Package

## Metadata
- **Project**: {project_name}
- **Module**: {module_name}
- **Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **Base Commit**: {base_commit}
- **Head Commit**: {head_commit}
- **Range**: {base_commit}..{head_commit}

## Commit Log
```
{commit_log}
```

## Changed Files (Stat)
```
{diff_stat}
```

## Full Diff
```diff
{diff_content}
```

## For Reviewer
Please review this package against the task brief.
Check:
1. All requirements are implemented
2. Code quality is acceptable
3. Tests exist and pass
4. No obvious defects
"""
    
    package_file.write_text(package_content, encoding='utf-8')
    
    print(f"[OK] 审查包已生成: {package_file}")
    print(f"  提交范围: {base_commit}..{head_commit}")
    print(f"  变更文件数: {len([l for l in diff_stat.split(chr(10)) if '|' in l])}")
    
    return package_file


def main():
    if len(sys.argv) < 3:
        print("用法: review-package.py <project> <module> [base-commit]")
        print("\n示例:")
        print('  review-package.py order-system data-models')
        print('  review-package.py order-system data-models HEAD~2')
        print('  review-package.py order-system data-models abc1234')
        sys.exit(1)
    
    project_name = sys.argv[1]
    module_name = sys.argv[2]
    base_commit = sys.argv[3] if len(sys.argv) > 3 else 'HEAD~1'
    
    package_file = generate_review_package(project_name, module_name, base_commit)
    
    # 输出路径供其他脚本使用
    print(f"\n[PATH] {package_file}")


if __name__ == '__main__':
    main()
