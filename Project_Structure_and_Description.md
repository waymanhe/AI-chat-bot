# 项目目录结构与说明

本项目为“本地知识库+互联网检索”AI助手，支持 Elasticsearch 检索、embedding 语义召回、hybrid 检索、tavily-mcp 网络搜索，适合企业/个人搭建智能问答系统。

---

## 1. 顶层目录结构

```
├── ai_bot.py      # 不同功能演示入口
├── config.py                                # 全局配置（ES、embedding、API密钥等）
├── docs/                                    # 本地知识库文档（PDF/txt等）
├── docs_es.py                               # 文档入库/ES相关脚本
├── qwen_agent_local/                        # 主包，核心代码
├── readmeImg/                               # 项目配图、界面预览
├── workspace/                               # 用户上传文档/分块/缓存等
└── 项目目录结构与说明.md                    # 本文件
```

---

## 2. qwen_agent_local 主包结构

```
qwen_agent_local/
├── agents/                # 各类智能体（助手、用户、写作、文档QA等）
│   ├── assistant.py       # 主助手Agent
│   ├── user_agent.py      # 用户Agent
│   ├── ...                # 其他Agent（写作、分组、模拟等）
│   ├── writing/           # 写作相关Agent
│   ├── keygen_strategies/ # 知识分块/关键词生成策略
│   └── doc_qa/            # 文档问答Agent
├── gui/                   # WebUI界面与静态资源
│   ├── web_ui.py          # Gradio主界面，知乎风格美化
│   ├── assets/            # 静态资源（CSS、图片、logo等）
│   └── ...                # Gradio工具/辅助
├── llm/                   # 大模型/Embedding/Schema等
│   ├── schema.py          # 消息格式/多模态Schema
│   ├── qwen_dashscope.py  # 通义千问API支持
│   ├── oai.py             # OpenAI API支持
│   └── ...
├── memory/                # 知识库存储（本地/ES/向量）
│   ├── memory.py          # 本地内存存储
│   ├── es_memory.py       # Elasticsearch+embedding存储
│   └── ...
├── tools/                 # 检索、解析、网络搜索等工具
│   ├── retrieval.py       # 检索主入口，支持bm25/embedding/hybrid
│   ├── doc_parser.py      # 文档解析与分块
│   ├── mcp_manager.py     # tavily-mcp网络检索
│   ├── code_interpreter.py# 代码解释器
│   └── ...
├── utils/                 # 工具函数、embedding、分词等
│   ├── embedding_utils.py # embedding获取与适配
│   ├── utils.py           # 通用工具
│   └── ...
├── agent.py / multi_agent_hub.py / log.py / settings.py / __init__.py
└── ...
```

---

## 3. 其他重要目录

- **docs/**：本地知识库文档（PDF/txt），可通过 docs_es.py 入库ES。
- **workspace/**：运行时缓存、分块、用户上传文档等。
- **readmeImg/**：项目配图、WebUI界面预览、ES入库效果等。

---

## 4. 特色功能说明

- **本地知识库检索**：支持 PDF/txt 文档解析、分块、embedding 生成，ES高效检索。
- **Elasticsearch+embedding**：支持 bm25、embedding、hybrid 检索，提升语义召回。
- **互联网检索**：集成 tavily-mcp 工具，支持网络实时搜索。
- **WebUI**：知乎直答风格美化，CSS 独立管理，侧边栏按钮支持弹窗提示。
- **多Agent/多模型**：支持多智能体协作、插件扩展。
- **代码结构清晰**：所有 import 均指向本地包，便于二次开发。

---

## 5. 运行入口说明

- `ai_bot.py`：本地+互联网双通道问答，集成 tavily-mcp。
- `qwen_agent_multi_files_gui.py`：多文件检索 WebUI 演示。

---

## 6. 静态资源与美化

- `qwen_agent_local/gui/assets/app.css`：主CSS，知乎风格美化，圆角卡片、浅色、现代风格。
- `logo.jpeg`、`user.jpeg`：WebUI头像、logo等。
- `readmeImg/`：界面预览、效果截图。

---
 
# Project Structure and Description

This project is an "AI Assistant for Local Knowledge Base + Internet Search". It supports Elasticsearch retrieval, embedding-based semantic recall, hybrid retrieval, tavily-mcp web search, and a modern Zhihu-style WebUI. It is suitable for enterprises or individuals to build intelligent Q&A systems.

---

## 1. Top-level Directory Structure

```
├── ai_bot.py      # Main entry for different demo modes
├── config.py      # Global configuration (ES, embedding, API keys, etc.)
├── docs/          # Local knowledge base documents (PDF/txt, etc.)
├── docs_es.py     # Scripts for document import/ES operations
├── qwen_agent_local/  # Main package, core code
├── readmeImg/     # Project images, UI previews
├── workspace/     # User-uploaded docs, chunk cache, etc.
└── Project_Structure_and_Description_EN.md  # This file
```

---

## 2. qwen_agent_local Main Package Structure

```
qwen_agent_local/
├── agents/                # Various agents (assistant, user, writing, doc QA, etc.)
│   ├── assistant.py       # Main assistant agent
│   ├── user_agent.py      # User agent
│   ├── ...                # Other agents (writing, group, simulation, etc.)
│   ├── writing/           # Writing-related agents
│   ├── keygen_strategies/ # Knowledge chunking/keyword generation strategies
│   └── doc_qa/            # Document QA agents
├── gui/                   # WebUI and static resources
│   ├── web_ui.py          # Gradio main UI, Zhihu-style
│   ├── assets/            # Static resources (CSS, images, logo, etc.)
│   └── ...                # Gradio utilities/helpers
├── llm/                   # LLM/embedding/schema, etc.
│   ├── schema.py          # Message format/multimodal schema
│   ├── qwen_dashscope.py  # Qwen Dashscope API support
│   ├── oai.py             # OpenAI API support
│   └── ...
├── memory/                # Knowledge storage (local/ES/vector)
│   ├── memory.py          # Local memory storage
│   ├── es_memory.py       # Elasticsearch + embedding storage
│   └── ...
├── tools/                 # Retrieval, parsing, web search, etc.
│   ├── retrieval.py       # Main retrieval entry, supports bm25/embedding/hybrid
│   ├── doc_parser.py      # Document parsing and chunking
│   ├── mcp_manager.py     # tavily-mcp web search
│   ├── code_interpreter.py# Code interpreter
│   └── ...
├── utils/                 # Utility functions, embedding, tokenization, etc.
│   ├── embedding_utils.py # Embedding utilities/adapters
│   ├── utils.py           # General utilities
│   └── ...
├── agent.py / multi_agent_hub.py / log.py / settings.py / __init__.py
└── ...
```

---

## 3. Other Important Directories

- **docs/**: Local knowledge base documents (PDF/txt), can be imported into ES via docs_es.py.
- **workspace/**: Runtime cache, chunked docs, user uploads, etc.
- **readmeImg/**: Project images, WebUI previews, ES import screenshots, etc.

---

## 4. Key Features

- **Local Knowledge Base Retrieval**: Supports PDF/txt parsing, chunking, embedding generation, and efficient ES retrieval.
- **Elasticsearch + Embedding**: Supports bm25, embedding, and hybrid retrieval for improved semantic recall.
- **Internet Search**: Integrated tavily-mcp tool for real-time web search.
- **WebUI**: Modern Zhihu-style, CSS managed independently, sidebar buttons with popup tips.
- **Multi-Agent/Multi-Model**: Supports multi-agent collaboration and plugin extension.
- **Clean Code Structure**: All imports point to local packages, easy for secondary development.

---

## 5. Main Entry Scripts

- `ai_bot.py`: Local + internet dual-channel Q&A, integrated tavily-mcp.
- `qwen_agent_multi_files_gui.py`: Multi-file retrieval WebUI demo.

---

## 6. Static Resources & UI

- `qwen_agent_local/gui/assets/app.css`: Main CSS, Zhihu-style, rounded cards, light/modern look.
- `logo.jpeg`, `user.jpeg`: WebUI avatars, logo, etc.
- `readmeImg/`: UI previews, effect screenshots.

---
