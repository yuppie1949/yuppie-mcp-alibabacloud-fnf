# yuppie-mcp-fnf

阿里云 FNF (Serverless 工作流) MCP Server — 让 AI 助手通过 MCP 协议操作阿里云 FNF。

## 功能

### 流程管理
- **查询流程详情**: 获取指定流程的名称、类型、执行模式、描述等信息
- **流程列表**: 批量查询流程，支持分页

### 执行管理
- **异步启动执行**: 启动流程执行并立即返回
- **同步启动执行**: 启动流程执行并等待完成
- **停止执行**: 停止正在运行的执行
- **查询执行状态**: 获取指定执行的状态信息
- **执行历史列表**: 查询流程的执行记录列表，支持分页
- **执行步骤详情**: 获取执行的每个步骤的详细信息

## 快速开始

### 安装

```bash
pip install yuppie-mcp-fnf
```

### 配置

通过环境变量配置阿里云凭证：

```bash
export FNF_ACCESS_KEY_ID=your_access_key_id
export FNF_ACCESS_KEY_SECRET=your_access_key_secret
# 可选：指定 endpoint（默认 cn-hangzhou.fnf.aliyuncs.com）
export FNF_ENDPOINT=cn-hangzhou.fnf.aliyuncs.com
```

### 运行

```bash
yuppie-mcp-fnf
```

## 开发

```bash
git clone https://github.com/yuppie1949/yuppie-mcp-fnf
cd yuppie-mcp-fnf
uv pip install -e ".[dev]"
uv run pytest -v
```

### 本地调试

```bash
# 方式1: 直接通过环境变量运行
FNF_ACCESS_KEY_ID=xxx FNF_ACCESS_KEY_SECRET=xxx uv run yuppie-mcp-fnf

# 方式2: 使用 .env 文件（推荐）
# 先编辑 .env 填入真实凭证，然后：
uv run yuppie-mcp-fnf

# 方式3: 使用 MCP Inspector 调试
npx @modelcontextprotocol/inspector uv run yuppie-mcp-fnf
```

## 工具列表

| 工具名 | 说明 |
|--------|------|
| `fnf_describe_flow` | 获取 FNF 流程信息 |
| `fnf_describe_flow_inputs` | 获取 FNF 流程信息及入参定义（含类型、示例 JSON） |
| `fnf_list_flows` | 查询 FNF 流程列表 |
| `fnf_start_execution` | 异步启动 FNF 流程执行 |
| `fnf_start_sync_execution` | 同步启动 FNF 流程执行 |
| `fnf_stop_execution` | 停止 FNF 流程执行 |
| `fnf_describe_execution` | 查询 FNF 执行状态 |
| `fnf_list_executions` | 查询 FNF 执行历史列表 |
| `fnf_get_execution_history` | 获取 FNF 执行步骤详情 |

## 入参定义（fnf_describe_flow_inputs）

`fnf_describe_flow_inputs` 可以从 Flow 的 States 中解析出入参定义，让 AI 知道每个参数的格式。

在 FNF Flow 中创建一个 **模板转换** 节点（`Action: Extensions:TemplateTransform`），
`template` 字段写入参的 JSON 定义：

### 支持的类型

| 类型 | 含义 | 示例值 |
|------|------|--------|
| `string` | 字符串 | `"示例文本"` |
| `int` | 整数 | `0` |
| `select` | 下拉选择（需 `enum`） | `"第一个选项"` |
| `object` | JSON 对象 | `{"key": "value"}` |
| `array[string]` | 字符串数组 | `["item1", "item2"]` |
| `file` | 单文件 | `"https://example.com/file.pdf"` |
| `file-list` | 文件列表 | `["url1", "url2"]` |

### 示例

```json
{
    "title": {"type": "string", "label": "文章标题", "required": 1},
    "partment": {"type": "select", "label": "部门", "enum": ["销售部", "技术部"]},
    "count": {"type": "int", "label": "数量"},
    "info": {"type": "object", "label": "详细信息"},
    "tags": {"type": "array[string]", "label": "标签"},
    "cover": {"type": "file", "label": "封面URL"},
    "attachments": {"type": "file-list", "label": "附件列表"}
}
```

## 许可证

MIT
