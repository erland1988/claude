#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WIP Ledger 更新脚本
用于自动更新项目进度账本 (.wip/{project}/ledger.md)
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path


def get_timestamp():
    """获取当前时间戳"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def find_wip_root():
    """查找 .wip 目录"""
    current = Path.cwd()
    while current != current.parent:
        wip_path = current / ".wip"
        if wip_path.exists():
            return wip_path
        current = current.parent
    return None


def list_projects(wip_root):
    """列出所有项目"""
    projects = []
    if wip_root.exists():
        for item in wip_root.iterdir():
            if item.is_dir() and (item / "ledger.md").exists():
                projects.append(item.name)
    return projects


def read_ledger(project_path):
    """读取账本内容"""
    ledger_file = project_path / "ledger.md"
    if ledger_file.exists():
        return ledger_file.read_text(encoding='utf-8')
    return None


def write_ledger(project_path, content):
    """写入账本内容"""
    ledger_file = project_path / "ledger.md"
    ledger_file.write_text(content, encoding='utf-8')


def update_project_info(content, stage=None):
    """更新项目信息"""
    if stage:
        # 更新当前阶段
        content = re.sub(
            r'- 当前阶段: .*',
            f'- 当前阶段: {stage}',
            content
        )
    # 更新时间
    content = re.sub(
        r'- 最后更新: .*',
        f'- 最后更新: {get_timestamp()}',
        content
    )
    return content


def update_module_status(content, module, field, status):
    """
    更新模块状态
    field: 设计/计划/编码/审查/合并
    status: ⬜/✅/🔄
    """
    # 查找模块行并更新对应字段
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith(f'| {module} '):
            parts = line.split('|')
            if len(parts) >= 7:
                field_map = {
                    '设计': 2,
                    '计划': 3,
                    '编码': 4,
                    '审查': 5,
                    '合并': 6
                }
                if field in field_map:
                    parts[field_map[field]] = f' {status} '
                    lines[i] = '|'.join(parts)
    return '\n'.join(lines)


def add_log_entry(content, module, action, detail='', commit=''):
    """添加日志条目"""
    timestamp = datetime.now().strftime("%H:%M")
    log_line = f"| {timestamp} | {module} | {action} | {detail} | {commit} |"
    
    # 在详细日志部分添加
    if '## 详细日志' in content:
        lines = content.split('\n')
        insert_idx = -1
        for i, line in enumerate(lines):
            if line.startswith('## 详细日志'):
                insert_idx = i + 2  # 跳过表头
        if insert_idx > 0:
            lines.insert(insert_idx, log_line)
            content = '\n'.join(lines)
    return content


def init_ledger(project_name, module_name='core'):
    """初始化账本"""
    wip_root = find_wip_root()
    if not wip_root:
        print("错误: 未找到 .wip 目录", file=sys.stderr)
        sys.exit(1)
    
    project_path = wip_root / project_name
    project_path.mkdir(parents=True, exist_ok=True)
    
    ledger_content = f"""# 项目进度账本: {project_name}

## 项目信息
- 名称: {project_name}
- 创建时间: {get_timestamp()}
- 当前阶段: design
- 最后更新: {get_timestamp()}

## 模块进度
| 模块 | 设计 | 计划 | 编码 | 审查 | 合并 |
|------|------|------|------|------|------|
| {module_name} | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

## 详细日志
| 时间 | 模块 | 动作 | 详情 | 提交 |
|------|------|------|------|------|
| {datetime.now().strftime("%H:%M")} | - | project_init | 项目初始化 | - |

## 阻塞问题
<!-- 如有 BLOCKED 状态记录这里 -->
"""
    
    write_ledger(project_path, ledger_content)
    print(f"[OK] 账本已初始化: {project_path / 'ledger.md'}")


def update_ledger(project_name, action, **kwargs):
    """更新账本"""
    wip_root = find_wip_root()
    if not wip_root:
        print("错误: 未找到 .wip 目录", file=sys.stderr)
        sys.exit(1)
    
    project_path = wip_root / project_name
    ledger_file = project_path / "ledger.md"
    
    if not ledger_file.exists():
        print(f"错误: 项目 {project_name} 的账本不存在", file=sys.stderr)
        sys.exit(1)
    
    content = read_ledger(project_path)
    
    # 根据动作类型更新
    if action == 'design_complete':
        content = update_project_info(content, 'planning')
        module = kwargs.get('module', 'core')
        content = update_module_status(content, module, '设计', '✅')
        content = add_log_entry(content, module, 'design_complete', '设计完成')
    
    elif action == 'plan_complete':
        content = update_project_info(content, 'coding')
        module = kwargs.get('module', 'core')
        content = update_module_status(content, module, '计划', '✅')
        content = add_log_entry(content, module, 'plan_created', '执行计划生成')
    
    elif action == 'step_complete':
        module = kwargs.get('module', 'core')
        step = kwargs.get('step', '')
        commit = kwargs.get('commit', '')
        content = update_module_status(content, module, '编码', '🔄')
        content = add_log_entry(content, module, 'step_complete', f'Step {step} 完成', commit)
    
    elif action == 'review_complete':
        content = update_project_info(content, 'done')
        module = kwargs.get('module', 'core')
        content = update_module_status(content, module, '审查', '✅')
        content = add_log_entry(content, module, 'review_complete', '审查通过')
    
    elif action == 'add_module':
        module = kwargs.get('module', '')
        # 添加新模块行
        if f'| {module} ' not in content:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('| ') and '模块' not in line:
                    lines.insert(i, f'| {module} | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |')
                    break
            content = '\n'.join(lines)
            content = add_log_entry(content, module, 'module_added', '新增模块')
    
    content = update_project_info(content)  # 更新时间
    write_ledger(project_path, content)
    print(f"[OK] 账本已更新: {ledger_file}")


def main():
    if len(sys.argv) < 2:
        print("用法: ledger-update.py <action> [args...]")
        print("\nActions:")
        print("  init <project> [module]     - 初始化账本")
        print("  design <project> [module]   - 标记设计完成")
        print("  plan <project> [module]     - 标记计划完成")
        print("  step <project> <module> <step> [commit] - 标记步骤完成")
        print("  review <project> [module]   - 标记审查完成")
        print("  add-module <project> <module> - 添加模块")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'init':
        if len(sys.argv) < 3:
            print("错误: 需要项目名称", file=sys.stderr)
            sys.exit(1)
        init_ledger(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else 'core')
    
    elif action == 'design':
        update_ledger(sys.argv[2], 'design_complete', module=sys.argv[3] if len(sys.argv) > 3 else 'core')
    
    elif action == 'plan':
        update_ledger(sys.argv[2], 'plan_complete', module=sys.argv[3] if len(sys.argv) > 3 else 'core')
    
    elif action == 'step':
        if len(sys.argv) < 5:
            print("错误: 需要 project module step", file=sys.stderr)
            sys.exit(1)
        update_ledger(sys.argv[2], 'step_complete', 
                     module=sys.argv[3], step=sys.argv[4], commit=sys.argv[5] if len(sys.argv) > 5 else '')
    
    elif action == 'review':
        update_ledger(sys.argv[2], 'review_complete', module=sys.argv[3] if len(sys.argv) > 3 else 'core')
    
    elif action == 'add-module':
        if len(sys.argv) < 4:
            print("错误: 需要 project module", file=sys.stderr)
            sys.exit(1)
        update_ledger(sys.argv[2], 'add_module', module=sys.argv[3])
    
    else:
        print(f"错误: 未知动作 {action}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
