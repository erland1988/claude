#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WIP 项目初始化脚本
创建 .wip/{project}/ 目录结构和骨架文档
"""

import os
import sys
import re
from datetime import datetime
from pathlib import Path


def get_timestamp():
    """获取当前时间戳"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def to_kebab_case(name):
    """转换为 kebab-case"""
    # 替换空格和特殊字符为 -
    name = re.sub(r'[\s_]+', '-', name)
    # 移除多余字符
    name = re.sub(r'[^\w\-]', '', name)
    # 转换为小写
    return name.lower().strip('-')


def suggest_names(chinese_desc):
    """根据中文描述推荐英文项目名"""
    # 关键词映射表
    keyword_map = {
        '订单': ['order', 'orders'],
        '用户': ['user', 'users'],
        '支付': ['payment', 'pay'],
        '系统': ['system', 'sys'],
        '重构': ['refactor', 'rebuild', 'v2'],
        '改造': ['upgrade', 'migration', 'v2'],
        '优化': ['optimization', 'improvement'],
        '权限': ['auth', 'permission'],
        '数据': ['data', 'db'],
        '缓存': ['cache', 'redis'],
        '配置': ['config', 'configuration'],
        '日志': ['log', 'logging'],
        '监控': ['monitor', 'monitoring'],
        '工具': ['tool', 'utils'],
        '服务': ['service', 'svc'],
        '接口': ['api', 'interface'],
        '导入': ['import', 'loader'],
        '导出': ['export', 'exporter'],
        '同步': ['sync', 'synchronization'],
        '迁移': ['migration', 'migrate'],
        '验证': ['validator', 'validation'],
        '查询': ['query', 'search'],
        '报表': ['report', 'reporting'],
        '统计': ['stats', 'statistics'],
        '分析': ['analysis', 'analyzer'],
        '通知': ['notification', 'notice'],
        '消息': ['message', 'messaging'],
        '任务': ['task', 'job'],
        '调度': ['scheduler', 'schedule'],
        '工作流': ['workflow', 'flow'],
        '流程': ['process', 'flow'],
    }
    
    desc_lower = chinese_desc.lower()
    suggestions = []
    
    # 尝试匹配关键词
    matched_keywords = []
    for cn, en_list in keyword_map.items():
        if cn in chinese_desc:
            matched_keywords.append((cn, en_list))
    
    # 生成建议名称
    if matched_keywords:
        # 组合前两个关键词
        if len(matched_keywords) >= 2:
            base = f"{matched_keywords[0][1][0]}-{matched_keywords[1][1][0]}"
            suggestions.append(to_kebab_case(base))
            suggestions.append(to_kebab_case(f"{base}-v2"))
        
        # 第一个关键词 + 动作
        if len(matched_keywords) >= 1:
            base = matched_keywords[0][1][0]
            for action in ['refactor', 'upgrade', 'optimization', 'v2']:
                suggestions.append(to_kebab_case(f"{base}-{action}"))
    
    # 去重并限制数量
    seen = set()
    unique = []
    for s in suggestions:
        if s not in seen and len(s) > 3:
            seen.add(s)
            unique.append(s)
    
    return unique[:3]


def get_project_root():
    """获取项目根目录（包含 .wip 的目录）"""
    current = Path.cwd()
    # 如果当前在 .claude/skills/work-in-process/ 下，向上找到项目根
    if '.claude' in str(current):
        while current.name != '.claude' and current != current.parent:
            current = current.parent
        if current.name == '.claude':
            return current.parent
    # 否则从当前目录向上找 .wip
    check = current
    while check != check.parent:
        if (check / '.wip').exists():
            return check
        check = check.parent
    # 默认返回当前目录
    return current


def create_project(project_name, module_name='core'):
    """创建项目结构"""
    project_root = get_project_root()
    wip_dir = project_root / '.wip'
    wip_dir.mkdir(exist_ok=True)

    project_path = wip_dir / project_name
    modules_path = project_path / 'modules' / module_name
    
    # 创建目录
    modules_path.mkdir(parents=True, exist_ok=True)
    
    # 创建 design.md（总体设计骨架）
    design_content = f"""# {project_name} 总体设计

## 参考资料

## 需求背景
- 触发条件：
- 范围边界：
- 前置校验：
- 状态约束：
- 幂等语义：

## 设计方案

### 总体思路

### 架构概要

### 关键决策

## 模块划分

| 模块 | 说明 | 状态 |
|------|------|------|
| {module_name} | 待定义 | ⬜ |

## 变更文件汇总（预估）

## 依赖关系图
"""
    
    (project_path / 'design.md').write_text(design_content, encoding='utf-8')
    
    # 创建模块 design.md
    module_design_content = f"""# {module_name} 设计

## 模块边界

### 职责

### 不做的事

### 接口契约

## 数据模型

## 状态机（如有）

## 实现思路

## 预估变更
| 文件 | 操作 | 说明 |
|------|------|------|

## 依赖
- 前置模块: 无
- 后置模块: 无
"""
    
    (modules_path / 'design.md').write_text(module_design_content, encoding='utf-8')
    
    # 创建 ledger.md
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
    
    (project_path / 'ledger.md').write_text(ledger_content, encoding='utf-8')
    
    return project_path


def main():
    if len(sys.argv) < 2:
        print("用法: project-init.py <中文描述>")
        print("\n示例:")
        print('  project-init.py "订单系统重构"')
        print('  project-init.py "用户权限改造"')
        sys.exit(1)
    
    chinese_desc = sys.argv[1]
    
    # 推荐名称
    suggestions = suggest_names(chinese_desc)
    
    print(f"项目描述: {chinese_desc}")
    print("\n推荐项目名:")
    for i, name in enumerate(suggestions, 1):
        print(f"  {i}. {name}")
    
    # 让用户选择或输入
    print("\n请选择 (输入序号或直接输入名称，默认 1):")
    try:
        choice = input("> ").strip()
    except EOFError:
        choice = "1"
    
    if not choice:
        choice = "1"
    
    if choice.isdigit() and 1 <= int(choice) <= len(suggestions):
        project_name = suggestions[int(choice) - 1]
    else:
        project_name = to_kebab_case(choice)
    
    # 创建项目
    project_path = create_project(project_name)
    
    print(f"\n[OK] 项目已创建: {project_path}")
    print(f"  - 总体设计: {project_path / 'design.md'}")
    print(f"  - 模块设计: {project_path / 'modules' / 'core' / 'design.md'}")
    print(f"  - 进度账本: {project_path / 'ledger.md'}")

    # 添加到 .gitignore（项目根目录）
    gitignore = project_root / '.gitignore'
    wip_entry = '.wip/'
    if gitignore.exists():
        content = gitignore.read_text(encoding='utf-8')
        if wip_entry not in content:
            with open(gitignore, 'a', encoding='utf-8') as f:
                f.write(f"\n{wip_entry}\n")
            print(f"\n[OK] 已添加到 .gitignore: {wip_entry}")
    else:
        gitignore.write_text(f"{wip_entry}\n", encoding='utf-8')
        print(f"\n[OK] 创建 .gitignore 并添加: {wip_entry}")


if __name__ == '__main__':
    main()
