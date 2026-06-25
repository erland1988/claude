---
name: api-to-curl
description: 当用户需要把项目接口导出为 cURL 命令、导入 Apifox/Postman，或提到 curl、apifox、postman、接口文档、接口调试时使用。从源码（路由→控制器→参数定义）提取接口定义，生成可直接导入的 cURL。
---

# ApiToCurl

从项目源码提取接口定义（路由、方法、路径、入参），生成可直接导入 Apifox/Postman 的 cURL 命令。支持多种语言和框架。

## 执行

若调用时未指定子命令，直接返回以下介绍信息：

可用子命令：

| 命令 | 功能 |
|------|------|
| `curl` | 展示技能简介及可用子命令 |
| `curl-scan` | 扫描项目，定位路由注册、host/port、全局前缀等基础信息 |
| `curl-gen` | 针对指定接口/关键词，提取路由+入参并生成 cURL |
| `curl-batch` | 批量生成一组相关接口的 cURL（如某功能涉及的全部接口） |
| `curl-export` | 输出可导入 Apifox 的格式（cURL 清单或 OpenAPI/Apifox JSON） |

工作流程：`curl-scan`（首次/换项目时）→ `curl-gen` 或 `curl-batch` → `curl-export`。

## 子命令

### `curl-scan`

扫描项目，建立生成 cURL 所需的基础上下文。只读，不改文件。

1. **识别技术栈**：根据项目文件特征识别语言和框架：
   - **Go**：main.go、go.mod + gin/echo/fiber/beego 等
   - **Node.js**：package.json + express/koa/nestjs/fastify 等
   - **Java**：pom.xml/build.gradle + Spring Boot/Servlet 等
   - **Python**：requirements.txt + Flask/Django/FastAPI 等
   - **PHP**：composer.json + Laravel/Symfony 等
   - **其他**：通过启动文件和依赖推断
   
2. **定位服务地址**：
   - 查启动入口（main/app/server/bootstrap 等）确认监听 host/port
   - 查配置文件（.env / config / application.yml / settings.py 等）是否覆盖端口
   - 常见默认端口：Spring Boot 8080、Express 3000、Django 8000、Go gin 常见 8080/2233 等
   - 无法确认则用占位 `http://localhost:{PORT}` 并提示用户补全

3. **定位路由前缀**：
   - 查路由注册处的 Group/前缀（如 gin 的 `Group("api")`、Express 的 `app.use('/api')`、Spring 的 `@RequestMapping("/api")`）
   - 确认完整路径拼接规则（前缀+子路由，是否自动加斜杠等）

4. **定位路由表**：
   - **Go**：router 目录、路由注册函数中的 `GET/POST/...` 调用
   - **Node.js**：routes/controllers 目录、`app.get/post`、decorator/annotation
   - **Java**：`@RestController` + `@GetMapping/@PostMapping`
   - **Python**：`@app.route` / `path()` / `@api_view` 等
   - **PHP**：routes 文件、Route facade、Attribute 等
   
5. **识别参数绑定方式**：
   - JSON body：Content-Type: application/json，参数从请求体解析
   - Query：URL 参数 `?a=1&b=2`
   - Form：Content-Type: application/x-www-form-urlencoded 或 multipart/form-data
   - Path：路径变量 `/user/:id` 或 `/user/{id}`
   - 各框架约定：
     - **Go**：struct tag `json/form/uri`、`binding:"required"` 等
     - **Node.js**：req.body/query/params、validation decorator、schema
     - **Java**：`@RequestBody/@RequestParam/@PathVariable`、validation annotations
     - **Python**：Pydantic model、form/query params、type hints
     - **PHP**：Request $request、Validator、FormRequest
   
6. 输出一份「项目接口基础信息」速查：
   - 技术栈（语言 + 框架版本）
   - host:port、全局前缀
   - 路由表位置（文件路径列表）
   - 参数绑定风格和验证方式
   - 响应包装格式（如统一的 `{code, message, data}` 结构）

### `curl-gen`

针对单个接口生成 cURL。

1. **定位路由**：按用户给的接口路径/方法名/关键词，在路由表中定位注册行，取出 **HTTP 方法 + 路径**。

2. **定位控制器方法**：顺着路由找到处理函数/方法，定位其所在文件和位置。

3. **提取参数定义**：
   - **Go**：读 struct 定义，取字段 + tag（json/form/uri）+ 注释 + validation tag
   - **Node.js**：
     - DTO class（class-validator）：读 property + decorator（`@IsString()`、`@IsNotEmpty()` 等）
     - Schema（Joi/Yup/Zod）：读 schema 定义
     - 纯 JS：从代码中推断 req.body.xxx 引用
   - **Java**：读 DTO class、`@RequestBody/@RequestParam` 参数、validation annotations（`@NotNull/@Min` 等）
   - **Python**：
     - Pydantic model：读 Field、type hints、validators
     - Django form：读 Form class 字段定义
     - 函数参数：从 type hints 和 default 推断
   - **PHP**：读 FormRequest validation rules、Controller 方法签名、docblock 注释

4. **解析参数字段**：
   - **字段名**：序列化后的名称（JSON key / query key / form name），非源码变量名
   - **类型**：string/int/bool/array/object/date/file 等
   - **必填性**：根据 required/optional 标记、默认值、nullable 推断
   - **说明**：从注释/docstring/description 提取
   - **枚举值**：从注释、常量定义、validation rules 中提取可选值

5. **生成 cURL**：
   - 拼接完整 URL（host:port + 前缀 + 路径，路径变量用示例值占位）
   - 按参数位置生成：
     - **JSON body**：`-H 'Content-Type: application/json' -d '{...}'`
     - **Query**：拼到 URL `?a=1&b=2`
     - **Form**：`-H 'Content-Type: application/x-www-form-urlencoded' -d 'a=1&b=2'` 或 `-F`
     - **Path**：直接替换路径中的 `:id` / `{id}` 为示例值
   - 示例值生成：结合字段名语义推断（phone→手机号、date→日期格式、id→非零整数、枚举→合法值之一）
   - 必填字段给非零值（避免验证报错）
   - 需要鉴权则加占位头：`-H 'Authorization: Bearer {TOKEN}'` 或 `-H 'Cookie: token={TOKEN}'`

6. **附字段说明**：在 cURL 下方生成表格 `字段 | 类型 | 必填 | 说明`，并标注参数来源（哪个文件的哪个结构/类）。

### `curl-batch`

批量生成一组相关接口。

1. 接受范围描述：
   - 某功能模块（如「用户管理」「订单流程」）
   - 某控制器类/文件（如 `UserController`、`user_routes.js`）
   - 某路由前缀（如 `/api/user`）
   - 明确的方法名列表

2. 逐个套用 `curl-gen` 流程，输出多条 cURL，每条前用注释标题标明：
   ```bash
   # 创建用户
   curl -X POST ...
   
   # 查询用户详情
   curl -X GET ...
   ```

3. 顺序按调用链或业务流程排列（创建 → 查询 → 变更 → 删除），方便理解依赖。

4. 末尾附「接口清单表」：`# | 方法 | 路径 | 用途 | 参数来源`。

### `curl-export`

输出可导入 Apifox 的格式。

1. **cURL 清单模式**（默认）：
   - 把所有 cURL 放进 markdown 代码块，每条可单独复制
   - Apifox「导入 → cURL」逐条粘贴即可生成接口

2. **结构化模式**（用户要求时）：
   - 生成 **OpenAPI 3.0 JSON**（Apifox 原生支持）
   - 包含：`paths`、HTTP method、参数 schema、required 字段、示例值、descriptions
   - 或生成 **Apifox Collection JSON**（Apifox 专有格式，更完整但需特殊处理）

3. 输出位置：
   - 用户指定文件路径 → 写入项目目录（如 `docs/api.curl.md` 或 `openapi.json`）
   - 未指定 → 直接在对话中输出

4. 使用提示：
   - Apifox 导入路径：「项目设置 → 导入数据 → cURL / OpenAPI 3.0」
   - 提示替换占位：`localhost:{PORT}` 改为实际域名、`{TOKEN}` 填实际鉴权凭证
   - 提示测试顺序（有依赖的接口需先调上游获取必要参数）

## 通用规则

### 字段值要真实可用

- **字段名取序列化名称**：
  - Go：json/form/uri tag，不是 struct 字段名
  - Java：Jackson/Gson 注解覆盖后的名称，不是属性名
  - Python：Pydantic 的 alias、Django form 的 field name
  - Node.js：class property 或 schema key
  - PHP：array key 或 property name
  
- **示例值语义化**：
  - phone/mobile → `"13800138000"`
  - email → `"user@example.com"`
  - date/time → `"2024-01-01"` 或 ISO 8601 格式
  - id/count → 非零整数（如 `123`）
  - boolean → `true` 或 `false`
  - 枚举 → 从注释/定义中取第一个合法值
  - 嵌套对象/数组 → 如实展开完整结构
  
- **必填字段非零值**：避免框架验证器对零值/空值/null 判空报错。

- **不杜撰字段**：参数定义里没有的字段不出现在 cURL 中。

### 信息来源可追溯

- 每个接口标注：
  - 路由注册位置：`文件名:行号`（如 `routes.go:15` 或 `user.routes.ts:23`）
  - 参数定义来源：`文件名:类型/结构体名`（如 `dto/user.go:CreateUserRequest` 或 `models/User.ts:CreateUserDto`）
  
- host:port、前缀来自源码或配置文件，不是猜测；无法确认的部分标注「占位，待用户确认」。

### 不臆造接口

- 路由表中找不到的接口不生成。
- 先用 `curl-scan` 定位路由表，再按实际注册项生成。
- 参数字段完整提取，嵌套结构如实展开，不简化或省略。

### 适配框架差异

- 路径变量格式：
  - Express/Koa: `:id`
  - Spring/FastAPI: `{id}`
  - Laravel: `{id}` 或 parameter constraint
  
- 验证注解/装饰器映射到「必填」：
  - Go: `binding:"required"`
  - Java: `@NotNull`, `@NotEmpty`, `@NotBlank`
  - Node.js: `@IsNotEmpty()`, `.required()` (Joi/Yup)
  - Python: `...` (Pydantic required), `blank=False` (Django)
  - PHP: `'required'` in validation rules
  
- 默认值处理：有默认值的参数标为可选，示例用默认值。

