# 🏗️ CheatSheet 新架构说明

## 重构完成 ✅

已按照PRD要求重新组织代码结构，采用模块化架构。

---

## 📁 新项目结构

```
nova25/
├── python/
│   ├── mcp_cheatsheet/              # MCP服务器模块
│   │   ├── src/
│   │   │   └── mcp_cheatsheet/
│   │   │       ├── __init__.py
│   │   │       ├── server.py        # FastMCP服务器
│   │   │       ├── database.py      # JSON数据库管理
│   │   │       ├── tools.py         # 11个MCP工具实现
│   │   │       └── models.py        # 数据模型定义
│   │   └── pyproject.toml
│   │
│   └── agent/                       # Agent模块
│       ├── src/
│       │   └── agent/
│       │       ├── __init__.py
│       │       ├── agent.py         # 主Agent循环
│       │       ├── tool_manager.py  # MCP工具聚合
│       │       ├── mcp_client.py    # MCP协议客户端
│       │       ├── config.py        # LLM & 配置
│       │       ├── webui.py         # Flask Web服务器
│       │       ├── prompts/
│       │       │   └── system_prompt.txt
│       │       └── templates/
│       │           └── webui.html
│       └── pyproject.toml
│
├── data/                            # 数据文件
│   ├── db.json
│   ├── knowledge_distributed_map.json
│   └── cur_progress.json
│
├── run.py                           # 主入口文件 ⭐
└── requirements.txt
```

---

## 🚀 快速启动

### 1. 启动应用

```bash
python run.py
```

### 2. 访问应用

打开浏览器访问: **http://localhost:5001**

（注意：端口改为5001，避免与macOS AirPlay冲突）

---

## 📦 模块说明

### MCP CheatSheet Server (`python/mcp_cheatsheet/`)

**教育领域的MCP服务器**，提供11个工具：

#### 数据管理工具
1. `distributeData` - 知识分布映射
2. `databaseSearch` - 智能数据库搜索
3. `getCurProgress` - 获取学习进度
4. `getSystemPrompt` - 生成系统提示

#### 测验评估工具
5. `evaluateAnswer` - 评估答案
6. `updateFreshnessAndLog` - 更新掌握度
7. `decideNext` - 决策下一步

#### 测验生成工具
8. `generateExplaination` - 生成解释
9. `generateQue_singleChoice` - 单选题
10. `generateQue_multiChoice` - 多选题
11. `generateQue_shortAnswer` - 简答题

**核心文件：**
- `server.py` - MCP服务器工厂
- `database.py` - 数据库操作封装
- `tools.py` - 11个工具的完整实现
- `models.py` - 数据模型（Concept, Course, Quiz等）

---

### Agent Module (`python/agent/`)

**工具调用代理**，集成LLM和MCP工具：

**核心文件：**
- `agent.py` - 主Agent，协调LLM和工具
- `mcp_client.py` - MCP客户端，连接MCP服务器
- `tool_manager.py` - 工具管理器，提供统一接口
- `config.py` - 配置管理（LLM、速率限制、服务器）
- `webui.py` - Flask Web服务器和API端点

**API端点：**
- `POST /api/upload` - 上传PDF
- `GET /api/courses` - 获取课程列表
- `POST /api/save_concepts` - 保存概念
- `POST /api/generate_quizzes` - 生成测验
- `POST /api/evaluate_answer` - 评估答案
- `GET /api/system_prompt` - 获取系统提示

---

## 🔄 与旧架构对比

### 旧架构（单文件）
```
app.py (746行)
└── 所有功能都在一个文件
```

### 新架构（模块化）
```
python/
├── mcp_cheatsheet/     # MCP服务器 (独立模块)
│   ├── models.py       # 数据模型
│   ├── database.py     # 数据库
│   ├── tools.py        # 11个工具
│   └── server.py       # 服务器
└── agent/              # Agent模块 (独立模块)
    ├── agent.py        # Agent逻辑
    ├── mcp_client.py   # MCP客户端
    ├── tool_manager.py # 工具管理
    ├── config.py       # 配置
    └── webui.py        # Web服务器
```

---

## ✨ 新架构优势

### 1. **模块化设计**
- MCP服务器和Agent完全分离
- 每个模块职责清晰
- 易于测试和维护

### 2. **可扩展性**
- 可独立升级MCP服务器或Agent
- 易于添加新工具
- 支持多个Agent连接同一MCP服务器

### 3. **代码复用**
- MCP服务器可被其他项目使用
- 工具和数据库操作完全解耦
- Agent可以连接不同的MCP服务器

### 4. **更好的组织**
- 遵循PRD定义的项目结构
- 符合MCP协议标准
- 便于团队协作

### 5. **易于部署**
- 每个模块有独立的`pyproject.toml`
- 可以分别打包发布
- 支持pip安装

---

## 🔧 开发指南

### 添加新的MCP工具

在 `python/mcp_cheatsheet/src/mcp_cheatsheet/tools.py` 中添加新方法：

```python
def my_new_tool(self, param1: str) -> dict:
    """Tool description"""
    # Implementation
    return result
```

在 `server.py` 中暴露工具：

```python
def my_new_tool(self, param1: str):
    """Tool 12: My new tool"""
    return self.tools.my_new_tool(param1)
```

### 修改配置

编辑 `python/agent/src/agent/config.py`：

```python
@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 5001  # 修改端口
    debug: bool = True
```

### 添加新的API端点

在 `python/agent/src/agent/webui.py` 中添加：

```python
@app.route('/api/my_endpoint', methods=['POST'])
def my_endpoint():
    # Implementation
    return jsonify({'success': True})
```

---

## 🧪 测试

### 手动测试清单

- [ ] 访问 http://localhost:5001
- [ ] 上传PDF文件
- [ ] 选择/创建课程
- [ ] 查看概念提取
- [ ] 生成测验
- [ ] 回答测验（单选、多选、简答）
- [ ] 查看评估反馈
- [ ] 检查学习进度

### 数据验证

检查数据文件是否正确更新：
- `data/db.json` - 概念已添加
- `data/knowledge_distributed_map.json` - 分布已更新
- `data/cur_progress.json` - 进度已记录

---

## 📝 配置文件

### `pyproject.toml` (MCP CheatSheet)

定义MCP服务器包：
- 包名: `mcp-cheatsheet`
- 版本: 1.0.0
- 依赖: requests

### `pyproject.toml` (Agent)

定义Agent包：
- 包名: `cheatsheet-agent`
- 版本: 1.0.0
- 依赖: flask, flask-cors, requests, python-dotenv

---

## 🐛 故障排除

### 端口被占用
```bash
# 修改端口 (已改为5001)
# 或关闭占用5000的程序
```

### 模块导入错误
```bash
# 确保Python路径正确
# run.py已自动配置路径
```

### 缺少依赖
```bash
pip install -r requirements.txt
```

---

## 📚 相关文档

- `PRD.md` - 产品需求文档
- `requirements.txt` - Python依赖
- `python/agent/src/agent/prompts/system_prompt.txt` - 系统提示

---

## 🎯 下一步计划

1. ✅ 完成模块化重构
2. ✅ 配置pyproject.toml
3. ✅ 测试新架构
4. 🔄 添加单元测试
5. 🔄 添加API文档
6. 🔄 性能优化

---

**重构完成日期**: 2025-01-08

**架构符合**: PRD Section 26-60

