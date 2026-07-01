# Claude Code 自定义命令与技能仓库

个人 Claude Code 工具配置仓库，包含自定义斜杠命令（`/`）和技能模块（Skills），覆盖开发工作流中从需求设计、接口调试、编码、复核到文档归档的完整链路。

## 目录结构

```
.claude/
├── commands/              # 自定义斜杠命令（/）
│   ├── agents-init.md     # 初始化 AI 工具配置
│   └── git-push.md        # 一键 git 提交推送
└── skills/                # 技能模块（可按场景激活）
    ├── api-to-curl/       # 源码 → cURL → Apifox/Postman
    │   └── SKILL.md       #   技能定义与执行规则
    └── work-in-process/   # 需求设计 → 编码 → 飞书归档
        ├── SKILL.md       #   技能定义与执行规则
        ├── README.md      #   使用指南
        ├── skills/        #   子技能（7 个）
        │   ├── wip-init/SKILL.md        # 初始化项目结构
        │   ├── wip-build/SKILL.md       # 生成设计文档
        │   ├── wip-check/SKILL.md       # 设计完整性检查
        │   ├── wip-plan/SKILL.md        # 生成执行计划
        │   ├── wip-code/SKILL.md        # 编码（自动 worktree + 子代理）
        │   ├── wip-review/SKILL.md      # 编码后复核
        │   └── wip-feishu/SKILL.md      # 飞书文档管理
        ├── scripts/        # 14 个 Python 脚本（飞书 + worktree + 账本）
        │   ├── feishu_*.py
        │   ├── worktree-*.py
        │   ├── ledger-update.py
        │   ├── project-init.py
        │   ├── module-suggest.py
        │   └── review-package.py
        ├── templates/      # 输出模板
        │   └── list.json
        ├── config.json.example   # 飞书应用配置模板
        └── config.json           # 飞书应用配置（不入库）
```

## 自定义命令

直接输入 `/命令名` 即可触发。

| 命令 | 功能 | 说明 |
|------|------|------|
| `/agents-init` | 初始化 AI 工具配置 | 创建 `AGENTS.md`、`.claude/CLAUDE.md`、`.cursor/settings.json`，让 Claude Code 和 Cursor 共享项目规范；同时补全 `.gitignore` |
| `/git-push` | 一键提交推送 | `git status` → 展示变更 → 确认 → `git add .` → 自动生成中文提交信息 → `git push` |

## 技能模块

通过对话自然语言触发（如"wip-build"、"curl-gen 这个接口"），Claude 自动匹配对应技能。

### api-to-curl

从项目源码提取接口定义（路由、方法、路径、入参），生成可直接导入 Apifox/Postman 的 cURL 命令。**只读**，不修改源码。

**子命令**：

| 命令 | 功能 |
|------|------|
| `curl-scan` | 扫描项目，定位路由注册、host/port、全局前缀、参数绑定方式等基础上下文 |
| `curl-gen` | 针对指定接口/关键词，定位路由 + 提取 DTO/参数定义，生成带字段说明的 cURL |
| `curl-batch` | 批量生成一组相关接口（某模块/控制器/路由前缀下的全部接口） |
| `curl-export` | 输出 Apifox 兼容格式（cURL 清单 或 OpenAPI 3.0 JSON） |

**工作流程**：`curl-scan`（首次/换项目）→ `curl-gen` / `curl-batch` → `curl-export`

**支持框架**：

| 语言 | 框架 |
|------|------|
| Go | gin, echo, fiber, beego |
| Node.js | express, koa, nestjs, fastify |
| Java | Spring Boot (MVC/WebFlux), Servlet |
| Python | Flask, Django, FastAPI |
| PHP | Laravel, Symfony |

**核心原则**：字段名取序列化名称（json/form/uri tag），不取源码变量名；示例值语义化（phone→13800138000）；路由表中找不到的接口不杜撰。

---

### work-in-process

基于 `.wip/` 目录结构，管理从需求设计到编码实现的完整开发流程。

**开发子命令**：

| 命令 | 功能 |
|------|------|
| `wip-init` | 初始化 `.wip/{project}/` 项目结构，中文描述智能推荐英文项目名 |
| `wip-build` | 生成设计文档（总体设计 + 按职责自动拆分的模块设计） |
| `wip-check` | 设计完整性检查（全流程执行两次：设计方案后 + 执行计划后） |
| `wip-plan` | 为指定模块生成详细执行计划（Phase 分阶段 + Step 步骤模板 + 测试矩阵） |
| `wip-code` | 编码（自动创建 Git Worktree 独立工作区 → 执行编码 → 自动合并回基分支） |
| `wip-review` | 编码后全面复核（对照计划 / 测试验证 / 代码质量 / Git 检查） |

**工作流程**：`wip-init` → `wip-build` → `wip-check` → `wip-plan` → `wip-check` → `wip-code` → `wip-review` → `wip-feishu-upload`（可选）

**核心特性**：

- **子代理驱动**：复杂任务自动启用 3 子代理链（实现 → 审查 → 修复）
- **自动账本更新**：7 列进度表（设计/计划/worktree/编码/审查/合并），compact 后无损恢复
- **Worktree 自动管理**：wip-code 自动创建 feature 分支、编码、合并、清理，用户无感

**飞书管理子命令**（需配置飞书应用）：

| 命令 | 功能 |
|------|------|
| `wip-feishu-upload` | 合并上传设计文档（总体设计 + 各模块设计）到飞书 |
| `wip-feishu-list` | 列出已上传的 WIP 文档，支持分页和 `--tsv` 导出 |
| `wip-feishu-search` | 按标题关键字搜索已上传的文档 |
| `wip-feishu-read` | 按关键字搜索并阅读匹配文档的完整内容 |
| `wip-feishu-delete` | 删除文档（按关键字/doc_id/--all） |

**飞书配置**：将 `.claude/skills/work-in-process/config.json.example` 复制为 `config.json`，填入凭证：

```json
{
  "appId": "cli_xxx",
  "appSecret": "xxx",
  "folderName": "项目名"
}
```

**环境要求**：Python 3.7+，`pip install -r scripts/requirements.txt`；飞书应用需 `drive:drive` + `docx:document` 权限。

## 配置说明

| 文件 | 用途 |
|------|------|
| `AGENTS.md` | 项目规范文档（Claude Code 和 Cursor 共享），由 `/agents-init` 创建 |
| `.claude/CLAUDE.md` | Claude Code 入口，指向 `@AGENTS.md` |
| `.cursor/settings.json` | Cursor 配置，指向 `AGENTS.md` |
| `.gitignore` | 忽略 `.claude/`、`.cursor/`、`.venv/`、`.wip/` 等本地文件 |

## 使用方式

1. 将本仓库 `.claude/` 目录复制到你的项目根目录
2. Claude Code 自动识别自定义命令和技能模块
3. 如需飞书功能，复制 `config.json.example` 为 `config.json` 并填入飞书应用凭证
4. 输入 `/命令名` 触发命令，或在对话中描述需求自动匹配技能

## 许可证

MIT