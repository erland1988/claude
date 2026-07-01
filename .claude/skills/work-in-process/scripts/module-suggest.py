#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WIP 模块命名建议脚本
根据模块职责自动推荐英文模块名
"""

import sys
import re


def to_kebab_case(name):
    """转换为 kebab-case"""
    name = re.sub(r'[\s_]+', '-', name)
    name = re.sub(r'[^\w\-]', '', name)
    return name.lower().strip('-')


# 职责到模块名的映射表
RESPONSIBILITY_MAP = {
    # 数据相关
    '数据模型': ['data-models', 'entity-definitions', 'schema-definition'],
    '数据库': ['db-migrations', 'schema-changes', 'database'],
    '实体定义': ['entities', 'entity-definitions', 'domain-models'],
    '数据迁移': ['db-migrations', 'data-migration', 'schema-migration'],
    
    # 业务逻辑
    '业务逻辑': ['business-logic', 'core-service', 'domain-service'],
    '核心业务': ['core-service', 'business-logic', 'core-domain'],
    '领域服务': ['domain-service', 'domain-logic', 'business-service'],
    '服务层': ['service-layer', 'services', 'business-services'],
    
    # 接口层
    'API': ['api-endpoints', 'api', 'controllers'],
    '接口': ['api-endpoints', 'controllers', 'interfaces'],
    '控制器': ['controllers', 'api-controllers', 'handlers'],
    '路由': ['routes', 'router', 'endpoints'],
    '视图': ['views', 'view-layer', 'presentation'],
    
    # 权限安全
    '权限': ['auth-validation', 'permission-check', 'authorization'],
    '认证': ['authentication', 'auth', 'login'],
    '授权': ['authorization', 'permission', 'access-control'],
    '安全': ['security', 'security-layer', 'protection'],
    
    # 缓存性能
    '缓存': ['cache-optimization', 'cache-layer', 'redis-layer'],
    '性能优化': ['performance', 'optimization', 'perf-tuning'],
    'Redis': ['redis-layer', 'redis-cache', 'cache-redis'],
    
    # 配置工具
    '配置': ['config', 'configuration', 'settings'],
    '配置管理': ['config-management', 'configuration', 'settings'],
    '工具': ['utils', 'utilities', 'helpers'],
    '公共工具': ['utils', 'common-utils', 'shared-utils'],
    
    # 输入输出
    '导入': ['import', 'data-import', 'importer'],
    '导出': ['export', 'data-export', 'exporter'],
    '上传': ['upload', 'file-upload', 'uploader'],
    '下载': ['download', 'file-download', 'downloader'],
    
    # 处理逻辑
    '解析': ['parser', 'parsing', 'analyzer'],
    '验证': ['validator', 'validation', 'sanitizer'],
    '转换': ['transform', 'converter', 'transformer'],
    '计算': ['calculator', 'calculation', 'compute'],
    
    # 存储
    '存储': ['storage', 'persistence', 'repository'],
    '文件': ['file-storage', 'file-service', 'files'],
    '对象存储': ['object-storage', 'oss', 's3-storage'],
    
    # 消息通知
    '消息': ['messaging', 'message-queue', 'messages'],
    '通知': ['notification', 'notifier', 'alerts'],
    '邮件': ['email', 'mail-service', 'email-sender'],
    '短信': ['sms', 'sms-service', 'text-messages'],
    
    # 任务调度
    '任务': ['tasks', 'task-service', 'jobs'],
    '定时任务': ['scheduler', 'cron-jobs', 'scheduled-tasks'],
    '调度': ['scheduler', 'dispatcher', 'orchestrator'],
    '工作流': ['workflow', 'workflow-engine', 'flow'],
    
    # 日志监控
    '日志': ['logging', 'logger', 'log-service'],
    '监控': ['monitoring', 'monitor', 'observability'],
    '追踪': ['tracing', 'trace', 'distributed-tracing'],
    '指标': ['metrics', 'telemetry', 'instrumentation'],
    
    # 测试
    '测试': ['tests', 'testing', 'test-suite'],
    '单元测试': ['unit-tests', 'tests', 'test-cases'],
    '集成测试': ['integration-tests', 'e2e-tests', 'test-integration'],
}


def suggest_module_names(responsibility):
    """根据职责推荐模块名"""
    resp_lower = responsibility.lower()
    suggestions = []
    
    # 直接匹配
    for key, names in RESPONSIBILITY_MAP.items():
        if key in responsibility or key in resp_lower:
            suggestions.extend(names)
    
    # 关键词匹配
    keyword_map = {
        'model': ['data-models', 'entity-definitions'],
        'db': ['db-migrations', 'database'],
        'sql': ['db-migrations', 'sql-layer'],
        'api': ['api-endpoints', 'api'],
        'http': ['http-api', 'web-api'],
        'service': ['services', 'business-logic'],
        'logic': ['business-logic', 'core-service'],
        'auth': ['auth-validation', 'authentication'],
        'cache': ['cache-optimization', 'cache-layer'],
        'config': ['config', 'configuration'],
        'util': ['utils', 'utilities'],
        'helper': ['helpers', 'utils'],
        'test': ['tests', 'testing'],
    }
    
    for keyword, names in keyword_map.items():
        if keyword in resp_lower:
            suggestions.extend(names)
    
    # 去重
    seen = set()
    unique = []
    for s in suggestions:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    
    return unique[:5]


def analyze_complexity(description):
    """分析需求复杂度，建议模块数量"""
    indicators = {
        'simple': ['简单', '单一', '一个', '单个', '修复', '优化', '修改'],
        'complex': ['系统', '平台', '模块', '多个', '重构', '架构', '整体', '全量'],
    }
    
    desc_lower = description.lower()
    simple_score = sum(1 for i in indicators['simple'] if i in desc_lower)
    complex_score = sum(1 for i in indicators['complex'] if i in desc_lower)
    
    if complex_score > simple_score:
        return 'complex', 3
    elif simple_score > 0:
        return 'simple', 1
    else:
        return 'medium', 2


def main():
    if len(sys.argv) < 2:
        print("用法: module-suggest.py <职责描述>")
        print("\n示例:")
        print('  module-suggest.py "数据模型定义"')
        print('  module-suggest.py "业务逻辑实现"')
        print('  module-suggest.py "API接口层"')
        sys.exit(1)
    
    responsibility = sys.argv[1]
    suggestions = suggest_module_names(responsibility)
    
    print(f"职责描述: {responsibility}")
    print("\n推荐模块名:")
    for i, name in enumerate(suggestions, 1):
        print(f"  {i}. {name}")
    
    if len(sys.argv) > 2:
        overall_desc = sys.argv[2]
        complexity, count = analyze_complexity(overall_desc)
        print(f"\n复杂度分析:")
        print(f"  描述: {overall_desc}")
        print(f"  类型: {complexity}")
        print(f"  建议模块数: {count}")


if __name__ == '__main__':
    main()
