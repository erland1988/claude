---
name: work-in-process
description: 当用户需要规划、设计、拆解一个开发需求，或提到 wip、技术方案、执行计划时使用。基于 .wip/ 目录管理设计与执行，支持多模块并行开发。
---

# WorkInProcess

基于 `.wip/` 目录结构，管理从需求设计到编码实现的完整开发流程。支持：
- 智能命名（中文描述 → 英文项目/模块名）
- 强制模块化（设计文档 + 执行计划分离）
- 多项目并行（各自独立目录）
- 自动账本更新（进度持久化）

## 执行

若调用时未指定子命令，直接返回以下介绍信息：

可用子命令：

| 命令 | 功能 |
|------|------|
| `wip` | 展示技能简介及可用子命令 |
| `wip-init` | 初始化项目结构，中文描述智能推荐英文项目名 |
| `wip-build` | 生成设计文档（总体+模块），自动判断模块数量并命名 |
| `wip-plan [module]` | 为指定模块生成详细执行计划（Phase/Step 结构） |
| `wip-check` | 设计完整性检查（需求覆盖/模块划分/计划完整性） |
| `wip-code [module]` | 按 plan.md 执行编码，自动选择执行模式 |
| `wip-review [module]` | 编码后复核（对照计划/测试验证/代码质量） |
| `wip-feishu-upload [project]` | 合并上传设计文档（总体+各模块 design.md） |
| `wip-feishu-*` | 飞书文档管理（list/search/read/delete） |

**新工作流程**：`wip-init` → `wip-build` → `wip-check` → `wip-plan [module]` → `wip-code [module]` → `wip-review [module]` → `wip-feishu-upload`（可选）

**目录结构**：
```
.wip/{project-name}/
├── design.md                   # 总体设计（wip-build 生成）
├── modules/
│   └── {module-name}/          # 自动命名（如 data-models）
│       ├── design.md           # 模块设计
│       └── plan.md             # 执行计划（wip-plan 生成）
└── ledger.md                   # 进度账本（自动更新）
```

## 子命令

### `wip-init`

初始化 `.wip/` 项目结构，支持中文描述智能推荐英文项目名。

**执行流程**：
1. 询问项目描述（中文，如"订单系统重构"）
2. **智能命名**：分析描述关键词，推荐 2-3 个英文项目名选项
   - 命名规范：kebab-case（短横线连接）
   - 示例：
     | 中文描述 | 推荐选项 |
     |---------|---------|
     | 订单系统重构 | order-system-refactor / order-refactoring / order-v2 |
     | 用户权限改造 | user-auth-upgrade / permission-system / user-center-auth |
     | 支付流程优化 | payment-flow-optimization / payment-process-v2 |
3. 用户选择或自定义项目名
4. 创建目录结构：
   ```
   .wip/{project-name}/
   ├── design.md              # 总体设计骨架（预填充章节）
   ├── modules/               # 模块目录
   │   └── {module-name}/     # 简单需求：自动命名单模块（如 core/main/service）
   │       └── design.md      # 模块设计骨架（预留）
   └── ledger.md              # 进度账本（初始化状态）
   ```
5. **自动更新 ledger.md**：记录项目创建，当前阶段 = design
6. 将 `.wip/` 加入 `.gitignore`（若尚未忽略）

**design.md 骨架**：
```markdown
# {项目名称} 总体设计

## 参考资料

## 需求背景

## 设计方案

### 总体思路

### 架构概要

### 关键决策

## 模块划分

| 模块 | 说明 | 状态 |
|------|------|------|
| {module-name} | 待定义 | ⬜ |

## 变更文件汇总（预估）

## 依赖关系图
```

**ledger.md 初始化**：
```markdown
# 项目进度账本: {project-name}

## 项目信息
- 名称: {project-name}
- 创建时间: {YYYY-MM-DD HH:mm:ss}
- 当前阶段: design

## 模块进度
| 模块 | 设计 | 计划 | 编码 | 审查 | 合并 |
|------|------|------|------|------|------|
| {module-name} | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

## 详细日志
| 时间 | 模块 | 动作 | 详情 | 提交 |
|------|------|------|------|------|
| {时间} | - | project_init | 项目初始化 | - |

## 阻塞问题
```

### `wip-build`

生成设计文档（总体设计 + 模块设计），**自动判断模块数量**并根据职责**自动命名**。

**执行流程**：
1. 读取当前项目代码结构，理解技术栈、命名风格
2. 与用户对话澄清需求（背景、范围、约束）
3. **自动判断模块数量**：
   - **简单需求**（单功能/单文件/单一逻辑）：单模块，自动命名（如 `core`, `validator`, `service`）
   - **复杂需求**（多独立子系统/多层架构）：自动拆分多个模块
4. **智能模块命名**（根据职责）：
   | 模块职责 | 自动命名示例 |
   |---------|-------------|
   | 数据模型定义 | `data-models`, `entity-definitions` |
   | 数据库迁移 | `db-migrations`, `schema-changes` |
   | 业务逻辑实现 | `business-logic`, `core-service` |
   | API 接口层 | `api-endpoints`, `controllers` |
   | 权限校验 | `auth-validation`, `permission-check` |
   | 缓存优化 | `cache-optimization`, `redis-layer` |
5. 生成分层设计文档：
   - **总体设计** → `.wip/{name}/design.md`
   - **模块设计** → `.wip/{name}/modules/{module}/design.md`
6. **自动更新 ledger.md**：标记设计完成，更新各模块状态

**总体设计文档结构**：
```markdown
# {项目名称} 总体设计

## 参考资料
（业务流程图、数据表关系、关键方法签名等）

## 需求背景
- 触发条件：
- 范围边界：
- 前置校验：
- 状态约束：
- 幂等语义：

## 设计方案

### 总体思路
用 3-4 句话讲清楚：要解决什么问题 → 用什么方式解决 → 核心设计原则

### 架构概要
- 系统层次：数据层/业务层/接口层
- 各层职责划分
- 模块间调用关系
- 涉及的数据表、接口、上下游依赖
- 是否向后兼容

### 关键决策
| # | 决策 | 方案 | 理由 | 风险 |
|---|------|------|------|------|
| 1 | 为何选方案A而非B | xxx | xxx | xxx |

## 模块划分

| 模块 | 说明 | 前置依赖 | 状态 |
|------|------|----------|------|
| data-models | 数据模型定义 | 无 | ✅ 完成 |
| business-logic | 业务逻辑实现 | data-models | 🔄 进行中 |
| api-endpoints | API接口层 | business-logic | ⬜ 未开始 |

## 变更文件汇总（预估）

| # | 文件 | 操作 | 所属模块 |
|---|------|------|----------|
| 1 | src/models/order.go | 修改 | data-models |

## 依赖关系图
（模块间依赖顺序）
```

**模块设计文档结构**（每个模块一个文件）：
```markdown
# {模块名} 设计

## 模块边界

### 职责
本模块负责什么

### 不做的事
明确超出范围的功能

### 接口契约
- 输入：
- 输出：
- 错误处理：

## 数据模型
（新增/修改的实体、字段、类型）

## 状态机（如有）
```
状态流转图
```

## 实现思路
（技术选型、关键算法、设计模式）

## 预估变更
| 文件 | 操作 | 说明 |
|------|------|------|
| src/xxx.go | 新增 | xxx |

## 依赖
- 前置模块: xxx
- 后置模块: xxx
```

### `wip-plan [module]`

为指定模块生成详细执行计划，**按依赖顺序分阶段拆解**（数据层 → 模型/实体 → 业务逻辑 → 接口/入口 → 联调验证）。

**执行流程**：
1. 读取模块设计文档 `.wip/{project}/modules/{module}/design.md`
2. **按层次分阶段拆解**：
   - Phase 1: 数据层（DDL/SQL/迁移脚本）
   - Phase 2: 模型/实体（数据结构定义）
   - Phase 3: 业务逻辑（核心业务实现）
   - Phase 4: 接口/入口（API/CLI/UI）
   - Phase 5: 联调验证（集成测试）
3. 每阶段拆分为**可执行步骤**（2-5分钟/步骤）
4. 输出执行计划 → `.wip/{project}/modules/{module}/plan.md`
5. **自动更新 ledger.md**：标记计划完成

**执行计划文档结构**：
```markdown
# {模块名} 执行计划

**目标**: 一句话描述
**设计文档**: 相对路径链接
**所属项目**: {project-name}

## 全局约束
- 语言版本: xxx
- 框架约束: xxx
- 命名规范: xxx
- 测试要求: xxx

---

## Phase 1: 数据层

### Step 1: {步骤名}

**文件**: `path/to/file.sql`
**位置**: 新建文件 / 修改某方法（第 X 行）
**背景**: 为何改（建立订单主表，存储核心订单信息）
**操作**:
```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_no VARCHAR(32) UNIQUE NOT NULL,
    ...
);
```
**验证**:
- Run: `mysql -e "DESC orders;"`
- Expected: 表结构正确，字段类型匹配

### Step 2: ...

## Phase 2: 模型/实体
...

## Phase 3: 业务逻辑
...

## Phase 4: 接口/入口
...

## Phase 5: 联调验证

**测试矩阵**:
| # | 场景 | 前置条件 | 操作步骤 | 预期结果 |
|---|------|----------|----------|----------|
| 1 | 正常创建订单 | 用户已登录 | 调用 CreateOrder | 返回订单号，状态 pending |
| 2 | 重复订单号 | 订单号已存在 | 重复提交 | 返回幂等错误，不重复创建 |
| 3 | 并发创建 | 10 线程同时创建 | 并发调用 | 数据一致，无重复订单号 |
| 4 | 金额校验 | 金额为负数 | 调用 CreateOrder | 返回参数错误，订单未创建 |

**步骤号管理**：
- 步骤号一经分配不复用
- 迭代中被取消的步骤保留占位并注明「已移除 + 原因」
- 不静默删除，保持可追溯

### `wip-worktree create [project] [module]` ★

为指定模块创建 Git Worktree，实现独立分支并行开发。

**执行流程**：
1. 读取当前分支（作为基分支，如 v1.0.0）
2. 创建 feature 分支：`feature/{project}-{module}`（基于当前分支）
3. 创建 worktree 目录：`.wip/worktrees/{project}/{module}/`
4. 切回基分支

**示例**：
```
# 当前在 v1.0.0 分支
$ wip-worktree create order-system data-models
[OK] worktree 创建成功
  基分支: v1.0.0
  功能分支: feature/order-system-data-models
  工作目录: .wip/worktrees/order-system/data-models/

# 在 worktree 中开发
$ cd .wip/worktrees/order-system/data-models
$ wip-code data-models
```

### `wip-worktree list`

列出所有 worktree 及其状态。

**输出示例**：
```
[主工作区]
  路径: ~/my-project
  分支: v1.0.0

[模块工作区]
  项目: order-system
    - data-models
      分支: feature/order-system-data-models
      路径: .wip/worktrees/order-system/data-models
    - business-logic
      分支: feature/order-system-business-logic
      路径: .wip/worktrees/order-system/business-logic
```

### `wip-worktree merge [project] [module]`

将模块分支合并回基分支。

**执行流程**：
1. 确认当前分支（目标分支）
2. 执行 `git merge feature/{project}-{module}`
3. 输出合并提交哈希
4. **自动更新 ledger.md**

**示例**：
```
# 当前在 v1.0.0 分支（基分支）
$ wip-worktree merge order-system data-models
[OK] 合并成功
  源分支: feature/order-system-data-models
  目标分支: v1.0.0
  提交: a1b2c3d
```

### `wip-worktree clean [project] [module]`

清理已合并的 worktree。

**执行流程**：
1. 执行 `git worktree remove .wip/worktrees/{project}/{module}`
2. 询问是否删除 feature 分支
3. **自动更新 ledger.md**

**完整工作流示例**：
```
# 1. 创建 worktree
$ wip-worktree create order-system data-models

# 2. 在 worktree 中开发
$ cd .wip/worktrees/order-system/data-models
$ wip-code data-modules  # 编码完成，自动提交到 feature 分支

# 3. 回到基分支合并
$ cd ~/my-project  # 回到主工作区
$ git checkout v1.0.0
$ wip-worktree merge order-system data-models

# 4. 清理 worktree
$ wip-worktree clean order-system data-models
```

### `wip-check`

设计完整性检查，编码前轻量自查——校验方案自洽性。

**检查项**：

1. **需求覆盖检查**：
   - 需求背景中的每条要点在设计文档中是否有对应？
   - 范围边界是否清晰？（什么做、什么明确不做）

2. **模块划分合理性**：
   - 各模块边界是否清晰，有无职责重叠？
   - 模块间接口契约是否完整定义？
   - 前置/后置依赖关系是否形成环？

3. **执行计划完整性**（如已生成 plan.md）：
   - 是否按依赖顺序分阶段（数据层→模型→业务→接口→验证）？
   - 每个步骤是否齐备「文件/位置/背景/操作/验证」？
   - 测试矩阵是否覆盖正常流、边界、幂等、并发？

4. **ledger 一致性**：
   - 文档中标记已完成的阶段与 ledger 记录是否一致？

**输出**：问题清单（如有），无问题则标记 `wip-check` 通过，**自动更新 ledger.md**。

### `wip-code [module]`

按模块执行计划（plan.md）逐步骤编写代码，**自动选择执行模式**。

**执行模式（自动判断）**：

| 信号 | 当前会话执行 | 子代理驱动 |
|------|-------------|-----------|
| Task/Step 数量 | ≤3 个 | >3 个 |
| 复杂度 | 单文件修改 | 多文件协调 |
| 风险等级 | 低风险（工具函数） | 高风险（核心逻辑） |
| 测试要求 | 简单单元测试 | 复杂集成测试 |

**模式 A：当前会话执行**
- 在当前 Claude 会话中逐步执行
- 适合：简单任务、快速修复、原型验证
- 流程：
  1. 读取 plan.md，确认当前模块
  2. 按 Step 顺序执行：写代码 → 验证 → 提交
  3. 每步完成后更新进度

**模式 B：子代理驱动（复杂任务）** ★
- 每个 Step 派独立子代理执行
- 实现子代理 → 审查子代理 → 修复子代理
- 质量更高，适合复杂任务

**子代理驱动流程**：

```
读取 plan.md
    │
    ├── Step N: 派实现子代理 (implementer)
    │       ├── 输入：Task Brief + 接口契约 + 全局约束
    │       ├── 动作：编码 → 测试 → 提交 → 自审
    │       └── 输出：
    │           STATUS: DONE
    │           COMMITS: <commit-list>
    │           TESTS: <test-results>
    │           SELF-REVIEW: <checklist>
    │
    ├── 生成审查包 (review-package.py)
    │       └── 输出：review-package-{timestamp}.md
    │
    ├── 派审查子代理 (reviewer)
    │       ├── 输入：Task Brief + 审查包 + 全局约束
    │       ├── 动作：规格符合性检查 + 代码质量检查
    │       └── 输出：
    │           SPEC_COMPLIANCE: PASS/FAIL
    │           CODE_QUALITY_VERDICT: APPROVED/NEEDS_FIX
    │           FINDINGS: <Critical/Important/Minor issues>
    │
    ├── 判断审查结果
    │       ├── 通过 → 标记 Step N 完成
    │       └── 需修复 → 派修复子代理
    │
    ├── 派修复子代理 (fixer) [如需]
    │       ├── 输入：Review Findings + 当前代码
    │       ├── 动作：修复问题 → 重新测试 → 提交
    │       └── 输出：
    │           STATUS: FIXED
    │           FIXES_APPLIED: <list>
    │           VERIFICATION: <test-results>
    │
    └── 重新审查 [如需]
            └── 循环直到通过

全部 Step 完成后: 派最终审查子代理
```

**子代理类型**：

| 子代理 | 职责 | 输入 | 输出 |
|--------|------|------|------|
| **Implementer** | 实现单个 Step | Task Brief + 接口契约 | 代码 + 测试 + 状态报告 |
| **Reviewer** | 审查实现质量 | 审查包 + Task Brief | 合规性判定 + 问题清单 |
| **Fixer** | 修复审查发现的问题 | 问题清单 + 当前代码 | 修复后的代码 + 验证结果 |

**子代理提示词位置**：
- `.claude/skills/work-in-process/subagents/implementer.md`
- `.claude/skills/work-in-process/subagents/reviewer.md`
- `.claude/skills/work-in-process/subagents/fixer.md`

**工具脚本**：
- `scripts/review-package.py`：生成审查包（diff 文件）

**自动判断逻辑**：
```python
if step_count <= 3 and complexity == 'simple':
    mode = 'current_session'
elif step_count > 3 or complexity == 'complex':
    mode = 'subagent_driven'
```

**通用执行要求**：
1. 执行前用 `git status` 确认工作区干净
2. 按 Step 模板执行：文件 / 位置 / 操作 / 验证
3. 若发现 plan.md 与实际代码有出入，先回写更新 plan.md 再继续
4. 每步验证通过后再进行下一步
5. **自动更新 ledger.md**：记录每步完成状态

### `wip-review [module]`

编码后全面复核——对照已完成源码，逐步骤检查实现是否正确。

**复核维度**：

1. **执行计划对照**：
   - 每个 Step 的「文件/位置/操作」是否已正确落地？
   - 有无 plan.md 中定义但未实现的步骤？
   - 实际改动文件是否与「变更文件汇总」一致？

2. **测试验证**：
   - 各 Step 的「验证」条件是否全部通过（编译/单测/联调）？
   - 联调测试矩阵的场景是否逐项验证？
   - 回归测试：现有测试是否全部通过？

3. **代码质量**：
   - 新增代码风格是否与项目既有代码一致？
   - 资源（连接/句柄/锁/事务）是否正确释放？
   - 边界条件（空值/并发/幂等）是否正确处理？

4. **Git 检查**：
   - `git status` / `git diff` 核对实际改动范围
   - 确认未触及计划外的文件
   - 提交历史是否清晰（每 Step 独立提交）

**输出**：复核报告（通过项 / 问题清单），逐项修正后重新确认，**自动更新 ledger.md**。

### 飞书子命令：通用环境要求

所有 `wip-feishu-*` 子命令通过本地 Python 脚本与飞书 API 交互，需满足：

- **Python 3.7+**（脚本使用了 `sys.stdout.reconfigure` 和 f-string）
- **`requests` 库**：在 `scripts/` 目录下执行 `pip install -r requirements.txt`
- **虚拟环境（推荐）**：建议在项目内创建 `.venv/`，避免 `requests` 版本与系统或其他项目冲突（`.venv/` 已在 `.gitignore` 中，不会入库）

执行脚本时，优先使用虚拟环境中的 Python（`.venv/Scripts/python`）；若虚拟环境不存在，则回退到系统 `python` 并先检查 `requests` 是否可用，不可用时提示安装。

### `wip-feishu-upload [project]`

合并上传设计文档（总体设计 + 各模块设计），不包括执行计划（plan.md 留在本地执行用）。

**合并规则**：
1. **主文档**：`.wip/{project}/design.md`（总体设计）
2. **子文档**：`.wip/{project}/modules/{module}/design.md`（各模块设计）
3. **不上传**：`plan.md`（执行计划留在本地）

**执行流程**：
1. 若未指定 project，自动发现 `.wip/` 下的项目（只有一个时直接使用，多个时提示选择）
2. 读取 `config.json` 获取飞书配置
3. 扫描项目目录，发现所有模块
4. 按顺序读取并合并设计文档（内存中处理，不生成临时文件）
5. 调用飞书 API 创建文档

**合并后文档标题**：`{日期}_{项目名称}_设计文档`

**合并后文档结构**：
```markdown
# {项目名称} 完整设计文档

> 生成时间: YYYY-MM-DD HH:mm:ss
> 项目路径: .wip/{project-name}/

---

# 第一部分：总体设计

[总体 design.md 全文]

---

# 第二部分：模块设计

## 模块: data-models

[模块 design.md 全文]

---

## 模块: business-logic

[模块 design.md 全文]

---

# 附录：项目元数据

| 属性 | 值 |
|------|-----|
| 项目名称 | {project-name} |
| 模块数量 | N |
| 设计完成时间 | YYYY-MM-DD |
```

**示例**：
```
用户: wip-feishu-upload
Claude: 发现以下项目:
      1. order-system-refactor
      2. user-center-v2
Claude: 请选择要上传的项目编号: 1
Claude: 正在合并设计文档...
      - 总体设计: 1200 字
      - data-models: 800 字
      - business-logic: 1500 字
      - api-endpoints: 600 字
Claude: 已上传到飞书: https://bytedance.feishu.cn/docx/xxxxx
Claude: ledger 已自动更新: uploaded order-system-refactor
```

### `wip-feishu-list`

列出飞书云空间中已上传的 WIP 文档。

1. 读取 `.claude/skills/work-in-process/config.json` 获取飞书配置。
2. 执行 `scripts/feishu_list.py [--tsv] [page_size] [page]`：
   - `--tsv`：可选，输出 Tab 分隔值（可直接复制粘贴到 Excel）
   - `page_size`：可选，每页数量（默认 100，最大 200）
   - `page`：可选，页码（默认第 1 页）
   - **步骤 A**：获取 `tenant_access_token`
   - **步骤 B**：查找或创建根目录 `work-in-process`
   - **步骤 C**：在根目录下查找或创建子文件夹 `{folderName}`，列出其中所有 `docx` 文档
3. 输出样式由 `templates/list.json` 控制：
   - `columns`：列定义（key / label / width），width=0 表示不截断
   - `separator`：分隔线字符
   - `dateFormat`：日期格式（如 `%Y-%m-%d`）
   模板缺失时使用内置默认样式。
4. 输出文档列表：序号、标题、日期、链接。

> **前置依赖**：飞书应用需有 `drive:drive` 权限（Python 环境见上方「通用环境要求」）。

### `wip-feishu-delete`

删除飞书云空间中的 WIP 文档。

1. 读取 `.claude/skills/work-in-process/config.json` 获取飞书配置。
2. 执行 `scripts/feishu_delete.py <关键字|doc_id|--all>`：
   - **步骤 A**：获取 `tenant_access_token`，在 `work-in-process/{folderName}` 中列出文档
   - **步骤 B**：按参数匹配目标文档（标题关键字 / doc_id / token）
   - **步骤 C**：确认后调用 `DELETE /drive/v1/files/{token}` 移入回收站
3. 支持以下删除模式：
   - `wip-feishu-delete is_transfer` — 按标题关键字匹配（唯一匹配时直接删除，多项匹配提示用更精确的关键字）
   - `wip-feishu-delete FCjUdotqjoRpl0xcZqbcATO9nTd` — 按 doc_id 精确删除
   - `wip-feishu-delete --all` — 删除文件夹内全部 WIP 文档（需二次确认）

> **前置依赖**：飞书应用需有 `drive:drive` 权限（Python 环境见上方「通用环境要求」）。

### `wip-feishu-search`

按关键字搜索已上传的 WIP 文档，输出匹配结果。

1. 读取 `.claude/skills/work-in-process/config.json` 获取飞书配置。
2. 执行 `scripts/feishu_search.py <关键字> [--tsv]`：
   - **步骤 A**：获取 `tenant_access_token`，在 `work-in-process/{folderName}` 中列出所有文档
   - **步骤 B**：按标题关键字过滤，输出匹配文档列表
3. 输出格式与 `wip-feishu-list` 一致（支持 `--tsv` 导出）。

> **前置依赖**：飞书应用需有 `drive:drive` 权限（Python 环境见上方「通用环境要求」）。

### `wip-feishu-read`

按关键字搜索并阅读所有匹配的 WIP 文档完整内容。

1. 读取 `.claude/skills/work-in-process/config.json` 获取飞书配置。
2. 执行 `scripts/feishu_read.py <关键字|doc_id>`：
   - **步骤 A**：同 `wip-feishu-search`，在 `work-in-process/{folderName}` 中按标题关键字/doc_id 搜索匹配文档（支持多项匹配）
   - **步骤 B**：对每篇匹配文档，通过 `GET /docx/v1/documents/{doc_id}/blocks` 获取全部 block
   - **步骤 C**：将 blocks 渲染为 Markdown 风格文本输出（h1/h2/h3 + 正文），多篇文档间以分隔线区分
3. 输出每篇文档的标题、链接、完整内容，末尾汇总篇数。

> **前置依赖**：飞书应用需有 `drive:drive` 和 `docx:document` 权限（Python 环境见上方「通用环境要求」）。

## Ledger 机制（进度账本）

`.wip/{project}/ledger.md` 用于持久化项目进度，防止会话 compact 后丢失上下文。

**自动更新时机**：
| 命令 | 更新内容 |
|------|----------|
| `wip-init` | 创建项目，当前阶段 = design |
| `wip-build` | 标记设计完成，更新模块列表 |
| `wip-plan [module]` | 标记模块计划完成 |
| `wip-check` | 标记检查通过/问题清单 |
| `wip-code [module]` | 每 Step 完成追加日志 |
| `wip-review [module]` | 标记审查完成 |
| `wip-feishu-upload` | 标记已上传飞书 |

**ledger.md 格式**：
```markdown
# 项目进度账本: {project-name}

## 项目信息
- 名称: {project-name}
- 创建时间: YYYY-MM-DD HH:mm:ss
- 当前阶段: design/planning/coding/review/done

## 模块进度
| 模块 | 设计 | 计划 | 编码 | 审查 | 合并 |
|------|------|------|------|------|------|
| data-models | ✅ | ✅ | 🔄 | ⬜ | ⬜ |
| business-logic | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |

## 详细日志
| 时间 | 模块 | 动作 | 详情 | 提交 |
|------|------|------|------|------|
| 10:30 | data-models | step_complete | Step 3 完成 | a1b2c3d |
| 10:15 | data-models | step_start | Step 3 开始 | - |
| 10:00 | data-models | plan_created | 计划生成 | - |

## 阻塞问题
<!-- 如有 BLOCKED 状态记录这里 -->
```

## 通用规则

### 每个步骤必须可执行

每个步骤用统一模板呈现，缺一不可：

- **文件**：目标文件路径，标注新建/修改/删除
- **位置**：精确到方法名 + 行号锚点（如 `CreatePerformance() 之后，第 68 行后`），让改动落点无歧义
- **背景**：为何改（仅在改动原因不直观时需要）
- **操作**：具体代码/SQL，可直接落地
- **验证**：编译/单测/联调的具体方式

禁止放入"仅确认""参考""梳理现有行为"等非执行项。

### 独立章节要求

以下为执行计划之外的独立顶层章节，必须单独成节：

- 「变更文件汇总」→ 独立章节，表格 `# | 文件 | 操作 | 对应阶段`，带阶段回溯列
- 「构建顺序」→ 独立章节，依赖图 + 阶段内并行链路说明

以下内容禁止独立成节，融入执行计划各步骤：

- 「数据库变更」→ 融入数据层相关阶段的步骤
- 「详细实现方案」→ 融入业务逻辑层相关阶段的步骤

### 自查清单

- [ ] 数据变更涉及事务时已正确处理原子性
- [ ] 常量/枚举定义完整，边界条件已正确处理
- [ ] SQL 或配置替换精确匹配源码（含原有缩进格式）
- [ ] 已规避目标语言的常见陷阱（如变量捕获/作用域、可变默认值、隐式类型转换等）
- [ ] 资源（连接/句柄/锁/事务）已正确释放，无泄漏
- [ ] 查询方法变更后空结果处理正确
- [ ] 新增字段/表/属性与现有命名风格一致