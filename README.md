# Claude Code 自定义命令与技能仓库

个人 Claude Code 工具配置仓库，包含自定义命令和技能。

## 目录结构

```
.claude/
├── commands/          # 自定义命令
│   ├── agents-init.md   # 初始化 AI 工具配置
│   └── git-push.md      # 一键 git 提交推送
└── skills/            # 技能模块
    ├── api-to-curl/     # API 转 curl 命令
    └── work-in-process/ # 飞书文档处理工具
```

## 自定义命令

| 命令 | 描述 |
|------|------|
| `/agents-init` | 初始化项目 AI 工具配置，让 Claude Code 和 Cursor 共享 `AGENTS.md` |
| `/git-push` | 一键完成 `git add → commit → push`，自动生成中文提交信息 |

## 技能模块

- **api-to-curl**: 将 API 请求转换为 curl 命令
- **work-in-process**: 飞书文档处理工具集（上传、下载、搜索等）

## 配置说明

- `AGENTS.md` - 项目规范文档（Claude Code 和 Cursor 共享）
- `.gitignore` - 忽略敏感配置和本地 AI 工具配置

## 使用方式

1. 克隆仓库
2. 将 `.claude/` 内容复制到项目根目录
3.  Claude Code 将自动识别自定义命令

## 许可证

MIT
