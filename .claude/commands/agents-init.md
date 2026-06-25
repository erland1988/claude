# /agents-init

初始化项目 AI 工具配置，让 Claude Code 和 Cursor 都能自动读取 `AGENTS.md`。

## 执行步骤

按顺序完成：

### 1. 检查并补全 `.gitignore`

读取 `.gitignore`，确保包含以下行（若缺失则追加）：

```
# AI 工具本地配置
.claude/
.cursor/
```

### 2. 创建 `AGENTS.md`

若项目根目录下 `AGENTS.md` 不存在，则创建基础模板：

```
# AGENTS.md

## 项目概述

<!-- 简要描述项目是什么、做什么 -->

## 技术栈

<!-- 列出主要技术栈 -->

## 项目结构

<!-- 描述关键目录结构 -->

## 开发规范

<!-- 编码规范、提交规范等 -->

## 常用命令

<!-- 构建、运行、测试等命令 -->
```

> 创建后请根据项目实际情况补充内容。

### 3. 创建 `.claude/CLAUDE.md`

确保 `.claude/` 目录存在，写入内容：

```
@AGENTS.md
```

### 4. 创建 `.cursor/settings.json`

确保 `.cursor/` 目录存在，写入：

```json
{
  "cursor.rules": "AGENTS.md"
}
```

### 5. 输出结果

列出已创建/修改的文件清单及状态。
