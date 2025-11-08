# CheatSheet 测试指南

## 功能说明
这是一个 PDF 文件分析和概念提取工具，使用 OpenRouter API 来处理上传的 PDF 文件并提取关键概念。

系统会将 PDF 文档分析后，以结构化的 JSON 格式返回概念列表，每个概念包含：
- **title**: 概念的标题（2-5个词）
- **content**: 概念的描述（1-3句话）

## 安装步骤

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置 API Key
API Key 已经在代码中配置（从 PRD.md 中获取），但也可以通过环境变量设置：

创建 `.env` 文件（可选）：
```
OPENROUTER_API_KEY=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
```

### 3. 运行应用
```bash
python app.py
```

服务器将在 http://localhost:5000 启动

## 使用方法

### 方法 1: 拖放文件
1. 打开浏览器访问 http://localhost:5000
2. 将 PDF 文件拖放到上传区域
3. 等待处理（会显示加载动画）
4. 查看提取的概念列表（每个概念以卡片形式展示）
5. 结果会自动保存到 `pdf2points_example.json` 文件

### 方法 2: 点击上传
1. 打开浏览器访问 http://localhost:5000
2. 点击上传区域
3. 选择 PDF 文件
4. 等待处理
5. 查看提取的概念列表
6. 结果会自动保存到 `pdf2points_example.json` 文件

## 功能特点

✅ **极简设计**：简洁的浅色主题界面  
✅ **拖放上传**：支持拖放和点击两种上传方式  
✅ **概念提取**：自动从 PDF 中提取 5-15 个关键概念  
✅ **结构化展示**：每个概念以卡片形式展示，包含标题和描述  
✅ **自动保存**：提取的概念自动保存到 `pdf2points_example.json` 文件  
✅ **实时反馈**：显示处理状态和加载动画  
✅ **错误处理**：友好的错误提示和回退机制  
✅ **多次上传**：可以重置并上传多个文件  

## API 配置

- **模型**: openai/gpt-4o（GPT-5 暂不可用）
- **PDF 引擎**: pdf-text
- **端点**: https://openrouter.ai/api/v1/chat/completions
- **输出格式**: JSON 数组，包含概念对象（title + content）

## 故障排除

### 问题 1: 模块未找到
```bash
pip install -r requirements.txt
```

### 问题 2: API 密钥错误
检查 `.env` 文件或 `app.py` 中的 API_KEY 配置

### 问题 3: 端口被占用
修改 `app.py` 最后一行的端口号：
```python
app.run(debug=True, port=5001)  # 改为其他端口
```

### 问题 4: PDF 处理失败
- 确保上传的是有效的 PDF 文件
- 检查文件大小（过大的文件可能需要更长时间）
- 查看控制台输出的错误信息

## 注意事项

⚠️ 这是一个测试版本，用于验证基本功能  
⚠️ 处理大型 PDF 文件可能需要较长时间  
⚠️ API 调用可能产生费用，请注意使用量  

## 输出示例

```json
[
    {
        "title": "Machine Learning Basics",
        "content": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed."
    },
    {
        "title": "Neural Networks",
        "content": "Neural networks are computing systems inspired by biological neural networks. They consist of interconnected nodes that process information in layers."
    }
]
```

## 下一步开发

- [ ] 添加文件大小限制
- [ ] 支持多文件上传  
- [ ] 添加导出 JSON 功能
- [ ] 添加概念搜索和筛选
- [ ] 优化移动端体验
- [ ] 添加更多 AI 模型选项

