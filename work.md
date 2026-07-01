# Work-in-Process Skill 改进方案

## 背景

借鉴 obra/superpowers 的先进理念，对现有 `work-in-process` skill 进行重构，实现：
- 设计与执行分离（设计文档 vs 执行计划）
- 多模块支持（大项目拆解）
- Git Worktree 隔离（独立分支开发）
- 账本机制（进度持久化防丢失）
- 子代理驱动（可选的高级模式）

---

## 核心改进点

### 1. 文档结构重构（强制模块化）

```
.wip/                               # 隐藏目录，不入版本控制
└── {project-name}/                 # 每个需求/项目独立目录
    ├── design.md                   # 总体设计文档（wip-build 生成）
    ├── modules/                    # 模块目录（强制，至少一个模块）
    │   └── {module-name}/          # 简单需求：自动命名单模块（如 config-validator）
    │       ├── design.md           # 模块设计
    │       └── plan.md             # 模块执行计划（wip-plan 生成）
    └── ledger.md                   # 进度账本
```

**设计意图**：
- **强制模块化**：所有需求都按模块拆分，简单需求 = 单模块
- 无需询问是否分模块，流程统一
- `.wip/` 为隐藏目录，天然被 `.gitignore` 忽略
- 支持多项目/多需求并行开发，各项目完全隔离

### 2. 新的子命令体系

| 原命令 | 新命令 | 变化 |
|--------|--------|------|
| `wip-init` | `wip-init` | 增加项目结构初始化 |
| `wip-build` | `wip-build` | 输出到 `.wip/{name}/design.md`，支持分模块 |
| - | `wip-plan` | 新增：为每个模块生成详细执行计划 |
| - | `wip-worktree` | 新增：Git worktree 管理（创建/切换/合并） |
| `wip-check` | `wip-check` | 增加设计文档完整性检查 |
| `wip-code` | `wip-code` | 支持子代理模式（可选） |
| `wip-review` | `wip-review` | 增加逐步审查模式 |
| `wip-feishu-*` | `wip-feishu-*` | 合并上传设计文档（总体+各模块 design.md） |

### 3. 详细设计

#### 3.1 wip-init（初始化项目结构）

**功能**：
1. 询问项目描述（中文，如"订单系统重构"、"用户中心权限改造"）
2. **智能命名**：根据中文描述推荐英文项目名
   - 分析描述关键词
   - 生成候选英文名（2-3个选项）
   - 用户确认或修改
3. 创建目录结构（**强制模块化**）：
   ```
   .wip/{english-project-name}/
   ├── design.md              # 总体设计骨架
   ├── modules/               # 模块目录
   │   └── {module-name}/     # 简单需求：自动命名单模块（如 config-validator）
   │       └── design.md      # 模块设计骨架（预留）
   └── ledger.md              # 进度账本（初始化状态）
   ```
   
   **说明**：
   - `wip-init` 创建单模块骨架，模块名根据项目职责自动命名（如 `core`, `validator`, `service`）
   - `wip-build` 根据复杂度：简单需求复用该模块，复杂需求拆分为多个命名模块
4. 将 `.wip/` 加入 `.gitignore`

**命名示例**：
| 中文描述 | 推荐英文名 |
|---------|-----------|
| 订单系统重构 | order-system-refactor |
| 用户中心权限改造 | user-center-auth |
| 支付流程优化 | payment-flow-optimization |
| 数据迁移工具 | data-migration-tool |

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
| module-a | xxx | 未开始 |

## 变更文件汇总（预估）

## 依赖关系图
```

**ledger.md 格式**：
```markdown
# 项目进度账本

## 项目信息
- 名称: {project-name}
- 创建时间: YYYY-MM-DD HH:mm:ss
- 当前阶段: design  # design / planning / coding / review / done

## 模块进度
| 模块 | 设计 | 计划 | 编码 | 审查 | 合并 |
|------|------|------|------|------|------|
| module-a | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ |

## 已完成任务日志
<!-- 每完成一个任务追加一行 -->
<!-- 格式: [时间] [模块] [任务] [提交哈希] -->

## 备注
```

#### 3.2 wip-build（生成设计文档）

**功能**：
1. 读取项目上下文（现有代码、技术栈）
2. 与用户对话澄清需求
3. **自动判断模块数量并智能命名**：
   - **简单需求**（改动范围小、逻辑单一）：创建单模块，根据职责自动命名
   - **复杂需求**（多独立子系统）：自动拆分，每个模块根据职责生成英文名称
4. 生成分层设计：
   - **总体设计** → `.wip/{name}/design.md`
   - **模块设计** → `.wip/{name}/modules/{english-module-name}/design.md`
5. 每个模块设计包含：
   - 模块边界（做什么、不做什么）
   - 接口契约（输入输出、依赖关系）
   - 状态机/数据模型
   - 预估变更文件
6. **自动更新 ledger.md**

**智能命名示例**：
| 模块职责 | 自动命名 |
|---------|---------|
| 数据模型定义 | data-models |
| 业务逻辑实现 | business-logic |
| API 接口层 | api-endpoints |
| 数据库迁移 | db-migrations |
| 缓存优化 | cache-optimization |
| 权限校验 | auth-validation |

**拆分与命名流程**：
```
分析需求 → 识别独立子系统 → 按职责命名模块 → 创建目录结构
```

**模块设计模板**：
```markdown
# {模块名} 设计

## 模块边界

### 职责
### 不做的事
### 接口契约

## 数据模型

## 状态机（如有）

## 实现思路

## 预估变更
| 文件 | 操作 | 说明 |

## 依赖
- 前置模块: xxx
- 后置模块: xxx
```

#### 3.3 wip-plan（生成详细执行计划）

**功能**：
1. 读取模块设计文档
2. **按依赖顺序拆解**（数据层 → 模型/实体 → 业务逻辑 → 接口/入口 → 联调验证）
3. 每阶段拆分为**可执行步骤**（2-5分钟/任务）
4. 输出 `.wip/{name}/modules/{module}/plan.md`
5. **自动更新 ledger.md**

**执行计划结构**：
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
**位置**: 新建文件
**背景**: 为何改（建立订单主表，存储核心订单信息）
**操作**:
```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    order_no VARCHAR(32) UNIQUE NOT NULL,
    user_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status TINYINT NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_order_no (order_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
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
```

**核心产出要求**（与原 WIP.md 保持一致）：
1. **按层次分阶段**：数据层 → 模型/实体 → 业务逻辑 → 接口/入口 → 联调验证
2. **每个步骤统一模板**：`文件` / `位置`（精确到方法名+行号锚点）/ `背景`（为何改）/ `操作`（具体代码/SQL）/ `验证`（编译/单测/联调）
3. **联调验证阶段**：用测试矩阵呈现 `# | 场景 | 前置条件 | 操作步骤 | 预期结果`，覆盖正常流、边界、幂等、并发等场景
4. **步骤号管理**：一经分配不复用；迭代中被取消的步骤保留占位并注明「已移除 + 原因」，不静默删除，保持可追溯

**与原设计的关系**：
- `wip-build` 生成「设计方案」（做什么、架构、关键决策）
- `wip-plan` 生成「执行计划」（怎么做、具体步骤、验证方式）
- 两者分离：设计可评审，计划可执行

#### 3.4 wip-check（设计完整性检查）

**功能**：
编码前轻量自查——校验方案自洽性，不深入比对源码（源码级精确校验留给 `wip-review`）。

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

**输出**：问题清单（如有），无问题则标记 `wip-check` 通过，ledger 自动更新。

#### 3.5 wip-worktree（Git Worktree 管理）★ 新增

**什么是 Git Worktree？**

Git Worktree 是 Git 的一个功能，允许你在**同一个仓库**中同时检出（checkout）**多个分支**到**不同的目录**，实现真正的并行开发：

```
传统方式（分支切换）          Worktree 方式（多目录并行）
    当前分支                    当前分支 → ~/project/（主目录）
       │                         feature-a → ~/project/.wip/worktrees/a/（工作树1）
       ├── checkout feature-a     feature-b → ~/project/.wip/worktrees/b/（工作树2）
       │    （切换，原分支不可见）   
       ├── 开发 a                  三个目录同时存在，同时可操作
       │
       ├── checkout feature-b     
       │    （切换，a 的改动被保存）
       └── 开发 b
```

**核心优势**：
| 对比项 | 传统分支切换 | Git Worktree |
|--------|-------------|--------------|
| 并行开发 | ❌ 只能同时在一个分支工作 | ✅ 同时在多个分支工作 |
| 编译状态 | ❌ 切换分支后需要重新编译 | ✅ 各目录独立，无需重复编译 |
| IDE 配置 | ❌ 频繁切换 IDE 项目 | ✅ 每个 worktree 独立 IDE 窗口 |
| 上下文切换 | ❌ 容易混淆不同分支的改动 | ✅ 物理隔离，清晰分明 |
| 临时文件 | ❌ 切换后临时文件丢失 | ✅ 各目录独立，互不干扰 |

**为什么在这个方案中使用 Worktree？**

在多模块开发场景下：
```
项目: order-system-refactor
├── 模块 A: data-models（已完成）
├── 模块 B: business-logic（开发中）
└── 模块 C: api-endpoints（未开始）

传统方式的问题：
- 开发模块 B 时，模块 A 的改动还在工作区，容易混淆
- 模块 B 编译失败可能影响模块 A 的代码
- 无法同时让同事 review 模块 A 的同时你开发模块 B

Worktree 方案：
- .wip/worktrees/order-system-refactor/data-models/ → 模块 A（稳定，可测试）
- .wip/worktrees/order-system-refactor/business-logic/ → 模块 B（开发中）
- 两个目录完全独立，互不影响
```

**子命令详解**：

| 命令 | 功能 | 使用场景 |
|------|------|----------|
| `wip-worktree create {module}` | 为模块创建独立 worktree | 开始开发某个模块前 |
| `wip-worktree list` | 列出所有 worktree | 查看当前有哪些模块在开发 |
| `wip-worktree switch {module}` | 切换到模块 worktree | 需要在多个模块间切换时 |
| `wip-worktree merge {module}` | 合并模块分支到主分支 | 模块开发完成，合并代码 |
| `wip-worktree clean {module}` | 清理已合并的 worktree | 合并后清理工作目录 |

**完整工作流程示例**（基于当前分支）：

```
【场景 1：在 main 分支开发】
主目录: ~/my-project/ (当前在 main 分支)
Claude: wip-init
Claude: wip-build → 拆分出 3 个模块

Claude: wip-worktree create data-models
  ✓ 基于当前分支 (main) 创建: feature/order-system-refactor-data-models
  ✓ 创建 worktree: .wip/worktrees/order-system-refactor/data-models/

Claude: wip-worktree merge data-models
  → 合并 feature/order-system-refactor-data-models 到 main
  → 主目录 ~/my-project/ (main) 现在包含新代码

【场景 2：在 v1.0.0 分支开发（你的情况）】
主目录: ~/my-project/ (当前在 v1.0.0 分支)
Claude: wip-init
Claude: wip-build → 拆分出模块

Claude: wip-worktree create data-models
  ✓ 基于当前分支 (v1.0.0) 创建: feature/order-system-refactor-data-models
  ✓ 创建 worktree: .wip/worktrees/order-system-refactor/data-models/
  
Claude: wip-code data-models
  → 在 worktree 中开发，基于 v1.0.0 的代码

Claude: wip-worktree merge data-models
  → 合并 feature/order-system-refactor-data-models 到 v1.0.0
  → 主目录 ~/my-project/ (v1.0.0) 现在包含新代码
  → 不是合并到 main！

【场景 3：在 dev 分支开发】
主目录: ~/my-project/ (当前在 dev 分支)
Claude: wip-worktree create api-endpoints
  ✓ 基于当前分支 (dev) 创建: feature/order-system-refactor-api-endpoints
  
Claude: wip-worktree merge api-endpoints
  → 合并回 dev 分支
```

**关键原则**：
- `wip-worktree create` 基于**当前所在分支**创建 feature 分支
- `wip-worktree merge` 合并回**创建时的基分支**（即当前分支）
- 与 main/master 无关，完全取决于你执行命令时所在的分支

**技术实现细节**：

```bash
# 创建 worktree（底层命令）
git worktree add .wip/worktrees/order-system-refactor/data-models \
    -b feature/order-system-refactor-data-models

# 目录结构
~/my-project/                                    # 主工作区 (main 分支)
├── src/
├── .wip/                                        # 隐藏目录
│   └── worktrees/
│       └── order-system-refactor/
│           ├── data-models/                     # worktree 1: feature/xxx-data-models
│           │   └── src/                         # 独立检出的代码
│           ├── business-logic/                  # worktree 2: feature/xxx-business-logic
│           │   └── src/
│           └── api-endpoints/                   # worktree 3: feature/xxx-api-endpoints
│               └── src/
└── .git/worktrees/                              # Git 管理的 worktree 元数据

# 各 worktree 之间的关系
# - 共享同一个 .git 仓库（对象数据库）
# - 各自有独立的 HEAD、index、工作区文件
# - 提交到同一个仓库历史
```

**使用限制与注意事项**：

1. **不能嵌套**：worktree 不能放在另一个 worktree 内部
2. **分支独占**：一个分支只能检出一个 worktree（不能同时在两个目录 checkout 同一个分支）
3. **清理顺序**：合并后先 `git worktree remove` 再删除目录
4. **磁盘空间**：每个 worktree 有独立的工作区文件（不共享编译产物）

**对比传统方案的改进**：

| 场景 | 传统分支方案 | Worktree 方案 |
|------|-------------|---------------|
| 开发模块 A 时测试模块 B | ❌ 需要 stash/切换分支 | ✅ 直接在 B 的 worktree 中测试 |
| 模块 A review 时开发模块 B | ❌ 需要等 A 合并 | ✅ 并行进行，互不干扰 |
| 模块 B 依赖模块 A 的改动 | ❌ 需要 rebase/merge 本地 | ✅ worktree 基于最新基分支 |
| 编译缓存 | ❌ 切换后重新编译 | ✅ 各 worktree 保持编译状态 |

#### 3.5 wip-code（增强版）

**两种执行模式（自动判断）**：

系统根据以下信号**自动选择**执行模式，无需用户指定：

| 信号 | 当前会话执行 | 子代理驱动 |
|------|-------------|-----------|
| 任务数量 | ≤3 个 Task | >3 个 Task |
| 复杂度 | 单文件修改 | 多文件协调 |
| 风险等级 | 低风险（工具函数） | 高风险（核心逻辑） |
| 测试要求 | 简单单元测试 | 复杂集成测试 |

**模式 A：当前会话执行**
- 在当前 Claude 会话中逐步执行
- 适合：简单任务、快速修复、原型验证

**模式 B：子代理驱动（推荐用于复杂任务）**
- 每个 Task 派独立子代理执行
- 实现子代理 → 审查子代理 → 修复子代理
- 质量更高，适合复杂任务

**子代理驱动流程**：
```
读取 plan.md
    │
    ├── Task 1: 派实现子代理
    │       ├── 编码 → 测试 → 提交 → 自审 → 写报告
    │       └── 状态: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
    │
    ├── 派审查子代理（规格符合性 + 代码质量）
    │       └── 结果: 通过 / 需修复（Critical/Important/Minor）
    │
    ├── 如需修复: 派修复子代理 → 重新审查
    │
    └── 标记 Task 1 完成，更新 ledger

...（继续下一个 Task）

全部完成后: 派最终审查子代理
```

#### 3.6 wip-review（编码后复核）

**功能**：
编码后全面复核——对照已完成源码，逐步骤检查实现是否正确、有无遗漏或引入问题。

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

**输出**：复核报告（通过项 / 问题清单），逐项修正后重新确认，ledger 自动更新。

#### 3.7 wip-feishu-upload（合并上传设计文档）

**功能**：
将当前项目的总体设计文档与各模块设计文档合并，生成一份完整的设计文档上传到飞书。

**合并规则**：
1. **主文档**：`.wip/{project-name}/design.md`（总体设计）
2. **子文档**：`.wip/{project-name}/modules/{module}/design.md`（各模块设计）
3. **不上传**：`plan.md`（执行计划留在本地，用于编码执行）

**合并格式**：
```markdown
# {项目名称} 完整设计文档

> 生成时间: YYYY-MM-DD HH:mm:ss
> 项目路径: .wip/{project-name}/

---

# 第一部分：总体设计

[总体 design.md 全文]

---

# 第二部分：模块设计

## 模块: {module-a}

[模块 design.md 全文]

---

## 模块: {module-b}

[模块 design.md 全文]

---

# 附录：项目元数据

| 属性 | 值 |
|------|-----|
| 项目名称 | {project-name} |
| 模块数量 | N |
| 设计完成时间 | YYYY-MM-DD |
```

**执行流程**：
1. 读取 `config.json` 获取飞书配置
2. 扫描 `.wip/{project-name}/` 目录，发现所有模块
3. 按顺序读取并合并设计文档
4. 生成临时合并文件（不上传到磁盘，内存中处理）
5. 调用飞书 API 创建文档（标题格式：`{日期}_{项目名称}_设计文档`）
6. 输出飞书文档链接

**命令格式**：
```
wip-feishu-upload [project-name]
```
- 不传参数：自动发现当前 `.wip/` 下的项目（只有一个时直接使用，多个时提示选择）
- 传参数：上传到指定项目的设计文档

**示例**：
```
用户: wip-feishu-upload
Claude: 发现以下项目:
      1. order-system-refactor
      2. user-center-v2
Claude: 请选择要上传的项目编号: 1
Claude: 正在合并设计文档...
      - 总体设计: 1200 字
      - 数据模型模块: 800 字
      - 业务逻辑模块: 1500 字
      - API接口模块: 600 字
Claude: 已上传到飞书: https://bytedance.feishu.cn/docx/xxxxx
```

#### 3.8 ledger.md（进度账本）机制

**作用**：
- 会话 compact 后恢复进度
- 多模块并行时追踪状态
- 审计和复盘

**更新时机**：
- 设计完成 → 更新设计状态
- 计划完成 → 更新计划状态
- 任务完成 → 追加日志行
- 合并完成 → 更新合并状态

**格式**：
```markdown
# 项目进度账本: {project-name}

## 概览
- 当前阶段: coding
- 活跃模块: module-a
- 最后更新: 2024-01-15 10:30:00

## 模块矩阵
| 模块 | 设计 | 计划 | worktree | 编码 | 审查 | 合并 |
|------|------|------|----------|------|------|------|
| module-a | ✅ | ✅ | ✅ | 🔄 | ⬜ | ⬜ |
| module-b | ✅ | ✅ | ⬜ | ⬜ | ⬜ | ⬜ |

## 详细日志
| 时间 | 模块 | 动作 | 详情 | 提交 |
|------|------|------|------|------|
| 10:30 | module-a | task_complete | Task 3 完成 | a1b2c3d |
| 10:15 | module-a | task_start | Task 3 开始 | - |
| 10:00 | module-a | plan_created | 计划生成 | - |

## 阻塞问题
<!-- 如有 BLOCKED 状态记录这里 -->
```

---

## 文件结构（改进后）

```
.claude/skills/work-in-process/
├── SKILL.md                      # 主技能定义（简化，引用子技能）
├── README.md                     # 使用指南
├── config.json.example           # 飞书配置模板
│
├── skills/                       # 子技能目录（仿 superpowers）
│   ├── wip-init/
│   │   └── SKILL.md
│   ├── wip-build/
│   │   └── SKILL.md
│   ├── wip-plan/
│   │   └── SKILL.md
│   ├── wip-worktree/
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       ├── create.sh
│   │       ├── merge.sh
│   │       └── clean.sh
│   ├── wip-check/
│   │   └── SKILL.md
│   ├── wip-code/
│   │   ├── SKILL.md
│   │   └── subagents/            # 子代理提示词
│   │       ├── implementer.md
│   │       ├── reviewer.md
│   │       └── fixer.md
│   ├── wip-review/
│   │   └── SKILL.md
│   └── wip-feishu/
│       └── SKILL.md
│
├── scripts/                      # 公共脚本
│   ├── ledger-update.py          # 更新账本
│   ├── task-extract.py           # 提取任务片段
│   └── review-package.py         # 生成审查包
│
└── templates/                    # 文档模板
    ├── design-module.md
    ├── plan-task.md
    └── ledger.md
```

---

## 渐进式实施计划

### Phase 1: 基础重构（文档分离 + 账本）
1. [ ] 修改 `wip-init`：创建项目结构（design.md + ledger.md）
2. [ ] 修改 `wip-build`：输出到设计文档，支持模块划分
3. [ ] 新增 `wip-plan`：生成详细执行计划
4. [ ] 实现账本机制（ledger-update 脚本）
5. [ ] 修改 `wip-code`：读取 plan.md 格式

### Phase 2: Git Worktree（分支隔离）
6. [ ] 新增 `wip-worktree` 命令族
7. [ ] 修改 `wip-code`：支持在 worktree 中执行
8. [ ] 集成 worktree 状态到 ledger

### Phase 3: 子代理驱动（高级模式）
9. [ ] 设计子代理提示词（实现/审查/修复）
10. [ ] 新增 `wip-code --subagent` 模式
11. [ ] 实现审查包生成脚本

### Phase 4: 飞书增强
12. [ ] 实现 `wip-feishu-upload` 合并上传（总体设计 + 各模块设计）
13. [ ] 支持从飞书文档恢复项目状态

---

## 关键设计决策（已确认）

| 决策 | 方案 | 理由 |
|------|------|------|
| 设计文档位置 | `.wip/{name}/` | 隐藏目录，不入版本控制，支持多项目并行 |
| WIP.md 单文件模式 | **不保留** | 完全迁移到新结构 |
| 是否入库 | 不入库（`.wip/` 在 .gitignore） | 临时工作文档，用完即弃 |
| 模块化策略 | **强制模块化**，自动判断数量 | 简单需求=单模块，复杂需求=自动拆分 |
| Worktree 位置 | `.wip/worktrees/{project}/{module}/` | 与源码分离，避免冲突 |
| 子代理模式 | **自动判断** | 根据任务复杂度自动选择 |
| 账本更新 | **自动更新** | 命令执行时自动更新，用户只读 |
| 账本格式 | Markdown 表格 | 人类可读，易手动修复 |

---

## 用户交互示例

```
用户: wip-init
Claude: 项目描述？（中文，如"订单系统重构"）
用户: 订单系统重构
Claude: 根据描述推荐项目名：
      1. order-system-refactor
      2. order-refactoring  
      3. order-system-v2
Claude: 请选择（输入序号或直接输入名称）：1
Claude: 已创建项目结构 .wip/order-system-refactor/

用户: wip-build
Claude: 正在读取项目上下文...
Claude: 需求背景是什么？
...（对话澄清）...
Claude: 分析需求复杂度...【复杂需求】识别出 3 个独立子系统
Claude: 自动拆分并命名模块：
      - data-models（数据模型定义）
      - business-logic（业务逻辑实现）
      - api-endpoints（API接口层）
Claude: 已生成设计文档
      - .wip/order-system-refactor/design.md（总体）
      - .wip/order-system-refactor/modules/data-models/design.md
      - .wip/order-system-refactor/modules/business-logic/design.md
      - .wip/order-system-refactor/modules/api-endpoints/design.md
Claude: ledger 已自动更新

【简单需求场景】
用户: wip-build
...对话澄清...
Claude: 分析需求复杂度...【简单需求】单模块即可
Claude: 自动命名模块：config-validator（配置校验器）
Claude: 已生成设计文档
      - .wip/config-loader/design.md（总体）
      - .wip/config-loader/modules/config-validator/design.md

用户: wip-plan data-models
Claude: 已为「data-models」模块生成执行计划
      - .wip/order-system-refactor/modules/data-models/plan.md
      - 包含 3 个 Phase（数据层/模型层/验证层），共 8 个 Step，预估 40 分钟
      - 联调验证：4 个测试场景（正常流/边界/幂等/并发）
Claude: ledger 已自动更新: data-models 状态 ⬜→✅(计划完成)

用户: wip-worktree create data-models
Claude: 已创建 worktree: .wip/worktrees/order-system-refactor/data-models/
      - 分支: feature/order-system-refactor-data-models
Claude: ledger 已自动更新: data-models worktree ✅

用户: wip-code data-models
Claude: 分析任务复杂度...（8个Step，多文件协调，涉及数据层变更）
Claude: 【子代理驱动模式】自动启用
      Phase 1/3 数据层:
        Step 1: 派实现子代理（创建订单表）... DONE
        Step 2: 派审查子代理... 通过
        Step 3: 派实现子代理（创建订单明细表）... DONE
        Step 4: 派审查子代理... 通过
      Phase 2/3 模型层:
        Step 5: 派实现子代理（Order 实体定义）... DONE
        ...
      Task 1: 派审查子代理... 通过
      ...
Claude: data-models 编码完成，ledger 已自动更新

用户: wip-worktree merge data-models
Claude: 已将 feature/order-system-refactor-data-models 合并到当前分支
      - 提交: a1b2c3d
      - ledger 已自动更新: data-models 状态 → 已合并
```
```

---

## 设计确认清单（已全部确认）

- [x] **不保留 WIP.md 单文件模式** — 完全迁移到 `.wip/{project}/` 新结构
- [x] **自动判断是否使用子代理** — 根据任务数量/复杂度自动选择
- [x] **自动账本更新** — 各命令执行时自动更新 ledger.md

---

## 渐进式实施计划

### Phase 1: 基础重构（文档分离 + 账本 + 智能命名）
1. [ ] 修改 `wip-init`：创建 `.wip/{project}/` 结构，**中文描述→英文项目名推荐**
2. [ ] 修改 `wip-build`：输出到设计文档，**自动判断模块数+模块职责自动命名**
3. [ ] 新增 `wip-plan`：生成详细执行计划（保留原 WIP.md 核心产出格式）
4. [ ] 新增 `wip-check`：设计完整性检查
5. [ ] 实现**自动账本更新**机制（ledger-update 脚本）
6. [ ] 修改 `wip-code`：读取 plan.md 格式，**自动选择执行模式**
7. [ ] 修改 `wip-review`：编码后逐步复核

### Phase 2: Git Worktree（分支隔离）
8. [ ] 新增 `wip-worktree` 命令族（create/list/switch/merge/clean）
9. [ ] 修改 `wip-code`：支持在 worktree 中执行
10. [ ] 集成 worktree 状态到 ledger

### Phase 3: 子代理驱动（高级模式）
11. [ ] 设计子代理提示词（implementer/reviewer/fixer）
12. [ ] 实现**自动判断逻辑**（根据 Task 数/复杂度自动选择执行模式）
13. [ ] 实现审查包生成脚本（review-package）

### Phase 4: 飞书增强
14. [ ] 实现 `wip-feishu-upload` 合并上传（总体设计 + 各模块 design.md）
15. [ ] 支持从飞书文档恢复项目状态
