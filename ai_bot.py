import pprint
import urllib.parse
import json5
from qwen_agent_local.agents import Assistant
from qwen_agent_local.gui import WebUI
import os
from config import DASHSCOPE_API_KEY, TAVILY_API_KEY, DASHSCOPE_BASE_URL

# ========== LLM 配置 ========== 
llm_cfg = {
    'model': 'deepseek-v3',
    'model_server': DASHSCOPE_BASE_URL,
    'api_key': DASHSCOPE_API_KEY,
    'generate_cfg': {
        'top_p': 0.8
    }
}

# ========== 智能体初始化 ========== 
system_instruction = '''你是一个AI助手。
请根据用户的问题，优先利用检索工具从本地知识库中查找最相关的信息。
如果本地知识库没有相关信息，再使用 tavily-mcp 工具从互联网上搜索，并结合这些信息给出专业、准确的回答。'''

# 集成 tavily-mcp 工具
mcp_tools = [{
    "mcpServers": {
        "tavily-mcp": {
            "command": "npx",
            "args": ["-y", "tavily-mcp@0.1.4"],
            "env": {
                "TAVILY_API_KEY": TAVILY_API_KEY
            },
            "disabled": False,
            "autoApprove": []
        }
    }
}, 'code_interpreter']

# 获取 docs 文件夹下所有文件
file_dir = os.path.join('./', 'docs')
files = []
if os.path.exists(file_dir):
    for file in os.listdir(file_dir):
        file_path = os.path.join(file_dir, file)
        if os.path.isfile(file_path):
            files.append(file_path)

# ========== agent 服务初始化 ========== 
def init_agent_service():
    """初始化多文件 AI 助手服务，memory_type='es' 用ES存储和检索，支持 tavily-mcp 网络检索"""
    try:
        bot = Assistant(
            llm=llm_cfg,
            system_message=system_instruction,
            function_list=mcp_tools,
            files=files,
            memory_type='es'  # 关键：用ES作为memory
        )
        print("助手初始化成功！（ES+网络检索模式）")
        return bot
    except Exception as e:
        print(f"助手初始化失败: {str(e)}")
        raise

# ========== GUI 启动函数 ========== 
def app_gui():
    """图形界面模式，提供 Web 图形界面（ES存储检索+网络检索）"""
    try:
        print("正在启动 Web 界面...")
        bot = init_agent_service()
        chatbot_config = {
            'prompt.suggestions': [
                '雇主责任险和工伤保险有什么主要区别？',
                '介绍下雇主责任险',
                '2024年保险行业最新政策',
                '保险相关的最新新闻',
            ]
        }
        print("Web 界面准备就绪，正在启动服务...")
        WebUI(
            bot,
            chatbot_config=chatbot_config
        ).run()
    except Exception as e:
        print(f"启动 Web 界面失败: {str(e)}")
        print("请检查网络连接和 API Key 配置")

# ========== 主程序入口 ========== 
if __name__ == '__main__':
    # 运行 GUI 模式（ES存储检索+网络检索）
    app_gui() 