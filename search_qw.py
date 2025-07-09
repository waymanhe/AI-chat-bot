import sys
print("Python 版本:", sys.version)

try:
    import qwen_agent
    print("qwen_agent 路径:", qwen_agent.__file__)
except ImportError:
    print("未安装 qwen_agent 包")