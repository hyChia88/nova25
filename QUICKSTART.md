# 🚀 快速启动指南

## 启动应用

```bash
python run.py
```

## 访问应用

打开浏览器: **http://localhost:5001**

## 使用流程

1️⃣ **上传PDF** → 拖拽或点击上传  
2️⃣ **选择课程** → 选择现有或创建新课程  
3️⃣ **等待生成** → AI提取概念并生成测验  
4️⃣ **开始测验** → 回答问题，获得AI评估反馈

---

## 新架构说明

✅ 已按PRD重构为模块化架构

- **MCP服务器**: `python/mcp_cheatsheet/` - 11个教育工具
- **Agent模块**: `python/agent/` - LLM集成和Web服务器
- **主入口**: `run.py` - 一键启动

详细架构说明请查看: `NEW_ARCHITECTURE.md`

---

## 故障排除

### 端口冲突
端口已改为5001（避免macOS AirPlay冲突）

### 缺少依赖
```bash
pip install -r requirements.txt
```

---

**所有功能已完整实现** ✅

