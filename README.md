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
    │   ├── SKILL.md       #   技能定义与执行规则
    │   └── templates/     #   输出模板
    └── work-in-process/   # WIP.md 驱动开发 + 飞书归档
        ├── SKILL.md       #   技能定义与执行规则
        ├── config.json.example   #   飞书应用配置模板（入库）
        ├── config.json           #   飞书应用配置（不入库，复制自 .example 并填写）
        ├── scripts/       #   飞书 API 交互脚本
        │   ├── requirements.txt
        │   ├── feishu_common.py
        │   ├── feishu_upload.py
        │   ├── feishu_list.py
        │   ├── feishu_delete.py
        │   ├── feishu_search.py
        │   └── feishu_read.py
        └── templates/     #   输出模板
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

围绕 `WIP.md` 文件，生成并维护可执行的技术方案，覆盖**需求设计 → 自查 → 编码 → 复核 → 飞书归档**的完整开发流程。

**开发子命令**：

| 命令 | 功能 |
|------|------|
| `wip-init` | 创建或重置 `WIP.md`，写入需求骨架（参考资料/需求背景/设计方案/执行计划等） |
| `wip-build` | 从对话中提取需求，完善 `WIP.md`——生成设计方案（总体思路/架构概要/关键决策）+ 分阶段执行计划 |
| `wip-check` | 编码前自查：需求覆盖、方案自洽性、步骤依赖、状态机/数据模型一致性 |
| `wip-code` | 按执行计划逐步骤编写代码，每步即验，偏差回写 WIP.md |
| `wip-review` | 编码后全面复核：逐步骤对照源码、回归检查、边界条件验证，输出复核报告 |

**工作流程**：`wip-init` → `wip-build` → `wip-check` → `wip-code` → `wip-review` → `wip-feishu-upload`（可选）

**飞书管理子命令**（需配置飞书应用）：

| 命令 | 功能 |
|------|------|
| `wip-feishu-upload` | 将 WIP.md 上传为飞书云文档，按项目归类到 `work-in-process/{folderName}` |
| `wip-feishu-list` | 列出已上传的 WIP 文档，支持分页和 `--tsv` 导出 |
| `wip-feishu-search` | 按标题关键字搜索已上传的 WIP 文档 |
| `wip-feishu-read` | 按关键字搜索并阅读匹配文档的完整内容 |
| `wip-feishu-delete` | 删除 WIP 文档（按关键字/doc_id/--all） |

**飞书配置**：将 `.claude/skills/work-in-process/config.json.example` 复制为 `config.json`（去 `.example` 后缀），然后填入飞书应用凭证：

```json
{
  "appId": "cli_xxx",
  "appSecret": "xxx",
  "folderName": "项目名"
}
```

所有文档统一存放在 **云文档根目录 > `work-in-process` > `{folderName}`** 下。

**环境要求**：Python 3.7+，安装 `pip install -r scripts/requirements.txt`（推荐使用 `.venv/` 虚拟环境）；飞书应用需开启 `drive:drive` 权限（读写文档内容额外需要 `docx:document`）。

**执行计划格式**：每个步骤统一模板——`文件 | 位置（方法名+行号） | 背景 | 操作（具体代码/SQL） | 验证`，步骤号不复用，取消步骤保留占位并注明原因。禁止放入"仅确认""参考"等非执行项。

## 配置说明

| 文件 | 用途 |
|------|------|
| `AGENTS.md` | 项目规范文档（Claude Code 和 Cursor 共享），由 `/agents-init` 创建 |
| `.claude/CLAUDE.md` | Claude Code 入口，指向 `@AGENTS.md` |
| `.cursor/settings.json` | Cursor 配置，指向 `AGENTS.md` |
| `.gitignore` | 忽略 `.claude/`、`.cursor/`、`.venv/`、`WIP.md` 等本地文件 |

## 使用方式

1. 将本仓库 `.claude/` 目录复制到你的项目根目录
2. Claude Code 自动识别自定义命令和技能模块
3. 如需飞书功能，复制 `config.json.example` 为 `config.json` 并填入飞书应用凭证
4. 输入 `/命令名` 触发命令，或在对话中描述需求自动匹配技能

## 许可证

MIT
