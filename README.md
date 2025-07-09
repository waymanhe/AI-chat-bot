# Like it? Give it a star! ⭐ | 好用点个星！⭐
# Qwen Agent 本地知识库问答系统

本项目是一个基于 Qwen Agent 的本地知识库问答与网络搜索应用，支持 RAG 检索增强生成，适合个人或团队自建智能问答系统。

---

## ✨ 主要特性

- **本地知识库检索（RAG）**：支持 txt/pdf 文档自动导入、向量化、Elasticsearch 检索，支持 bm25/embedding/hybrid 多通道召回。
- **网络搜索集成**：可选用 tavily-mcp 等网络搜索工具，补充知识库不足。
- **多模型支持**：兼容 OpenAI embedding、通义千问等主流模型。
- **知乎风格 WebUI**：现代圆角卡片、浅色美观，CSS 独立管理，侧边栏按钮支持弹窗提示。
- **易于扩展**：支持自定义工具、索引、检索逻辑，所有 import 路径本地化，便于二次开发。

---

## 💡 架构说明与开发思考

- **基于 qwen-agent 二次开发**，充分利用其智能体调度、插件机制和 WebUI，专注业务创新。
- **知识库检索能力增强**，定制 ES+embedding 检索工具，支持高效语义召回与多源融合。
- **开箱即用与深度定制兼得**，既保留易用性，又便于底层扩展和长期维护。
- **私有化部署与数据安全**，本地可控，适合企业/团队。
- **技术选型**：qwen-agent 工具化、模块化、界面友好，适合智能体知识库问答系统基础。

---

## 📝 主要定制与扩展

- **1. ES+Embedding 检索工具**：`qwen_agent_local/memory/es_memory.py`，支持 dense_vector、bm25/embedding/hybrid 检索。
- **2. 检索主入口**：`qwen_agent_local/tools/retrieval.py`，支持多检索类型参数。
- **3. WebUI 美化**：`qwen_agent_local/gui/web_ui.py` + `assets/app.css`，知乎直答风格，侧边栏按钮弹窗。
- **4. 互联网检索集成**：`qwen_agent_local/tools/mcp_manager.py`，tavily-mcp 网络搜索。
- **5. 其他**：所有 import 路径本地化，便于维护。

---

## 🛠️ 技术栈

- **后端**：
  - Python 3.8+
  - Qwen Agent（阿里通义千问智能体框架）
  - Elasticsearch 8.x（向量数据库，支持 dense_vector）
  - OpenAI Embedding / 通义千问 Embedding（可选）
  - Tavily-mcp（可选，网络搜索工具）
  - pypdf、requests 等
- **前端**：
  - Gradio WebUI（知乎风格美化）
- **主要依赖**：
  - gradio、elasticsearch、openai、dashscope、pypdf、langchain

---

## 🖥️ 系统环境要求

- **Python**：3.8 及以上
- **Elasticsearch**：建议 8.x，需支持 dense_vector
- **依赖包**：见 requirements.txt

---

## 🚀 快速上手

### 1. 安装依赖

```bash
pip install -r requirements.txt
# 如需用到 openai embedding、ES 检索等，需额外安装：
pip install openai elasticsearch pypdf requests
```

### 2. 启动 Elasticsearch

请确保本地或远程已启动 Elasticsearch 服务，并配置好地址、端口。

### 3. 配置 API Key

- **OpenAI embedding（如 dashscope）**：
  - 设置环境变量 `DASHSCOPE_API_KEY` 或在代码中填写明文 key
- **Tavily 网络搜索**：
  - 设置环境变量 `TAVILY_API_KEY` 或在代码中填写明文 key

### 4. 准备知识库文档

- 将所有 txt/pdf 等文档放入 `docs/` 目录
- 支持中文/英文，建议 UTF-8 编码

### 5. 批量导入知识库到 ES

```bash
python docs_es.py
```
- 自动批量索引 `docs/` 下所有文档，并生成 embedding 向量
- 如需自定义索引名、ES 地址等，可在脚本内修改

### 6. 启动智能体/问答服务

```bash
python ai_bot.py
```
- 支持 WebUI 图形界面
- 支持本地知识库检索（RAG）与网络搜索（tavily-mcp）

---

## 📚 知识库更新与维护

1. **添加/修改文档**：将新文档（txt/pdf）直接放入 `docs/` 目录，或替换已有文档
2. **重新批量导入**：重新运行 `docs_es.py`，会自动删除旧索引并重建，导入所有最新文档
   - 如只需增量导入，可自行修改脚本逻辑
3. **刷新检索服务**：文档导入后，重新启动智能体服务（如 ai_bot.py），即可用最新知识库内容进行问答

---

## ❓ 常见问题排查

- **找不到文档**：请确保运行目录为项目根目录，且 `docs/` 路径正确。
- **ES 连接失败**：确认 ES 服务已启动，地址、端口、认证信息正确。
- **API Key 报错**：请检查环境变量或明文 key 是否填写正确。
- **知识库未被 LLM 参考**：可通过调试输出确认召回内容是否拼接到 prompt。

---

## 🧾 许可证与商业使用
本项目采用 **AGPL-3.0 许可证**，这意味着：
- 您可以自由地使用、修改和分发本项目，但必须遵守 AGPL-3.0 协议要求
- **闭源商用需要购买商业授权**
- 项目的**重要贡献者**可免费获得商业授权

> ℹ️ 我们强烈建议优先考虑AGPL-3.0合规方案。如有商业授权疑问，请邮件联系作者

---

# English Quick Start

## Qwen Agent Local Knowledge Base QA System

This project is a local knowledge base QA and web search application based on Qwen Agent, supporting RAG (Retrieval-Augmented Generation), suitable for individuals or teams to build their own intelligent Q&A system.

### ✨ Features

- **Local Knowledge Base Retrieval (RAG)**: Supports txt/pdf auto import, vectorization, Elasticsearch retrieval (bm25/embedding/hybrid).
- **Internet Search Integration**: Optionally use tavily-mcp and other web search tools to supplement the knowledge base.
- **Multi-Model Support**: Compatible with OpenAI embedding, Qwen embedding, etc.
- **Modern WebUI**: Zhihu-style, beautiful, CSS managed independently, sidebar buttons with popup tips.
- **Easy to Extend**: Custom tools, indexes, retrieval logic, all imports are local for easy secondary development.

### 🛠️ Tech Stack

- **Backend**: Python 3.8+, Qwen Agent, Elasticsearch 8.x, OpenAI/Qwen Embedding, tavily-mcp, pypdf, requests, etc.
- **Frontend**: Gradio WebUI (Zhihu style)
- **Main dependencies**: gradio, elasticsearch, openai, dashscope, pypdf, langchain

### 🚀 Quick Start

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install openai elasticsearch pypdf requests
   ```
2. Start Elasticsearch and configure API keys (see above).
3. Put your txt/pdf files in `docs/`.
4. Import docs to ES:
   ```bash
   python docs_es.py
   ```
5. Start the QA service:
   ```bash
   python ai_bot.py
   ```

### 📚 Knowledge Base Maintenance
- Add/replace docs in `docs/`, re-run `docs_es.py`, restart service.

### License
AGPL-3.0. Commercial use requires a license. See above for details. 