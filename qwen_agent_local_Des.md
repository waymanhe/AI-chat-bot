# qwen_agent 目录结构

```
qwen_agent/
├── __init__.py
├── agent.py
├── log.py
├── multi_agent_hub.py
├── settings.py
├── agents/
│   ├── __init__.py
│   ├── article_agent.py
│   ├── assistant.py
│   ├── dialogue_retrieval_agent.py
│   ├── dialogue_simulator.py
│   ├── doc_qa/
│   ├── fncall_agent.py
│   ├── group_chat.py
│   ├── group_chat_auto_router.py
│   ├── group_chat_creator.py
│   ├── group_chat.py
│   ├── human_simulator.py
│   ├── keygen_strategies/
│   ├── memo_assistant.py
│   ├── react_chat.py
│   ├── router.py
│   ├── tir_agent.py
│   ├── user_agent.py
│   ├── virtual_memory_agent.py
│   ├── write_from_scratch.py
│   ├── writing/
├── gui/
│   ├── __init__.py
│   ├── gradio_dep.py
│   ├── gradio_utils.py
│   ├── utils.py
│   ├── web_ui.py
│   ├── assets/
├── llm/
│   ├── __init__.py
│   ├── azure.py
│   ├── base.py
│   ├── fncall_prompts/
│   ├── function_calling.py
│   ├── oai.py
│   ├── openvino.py
│   ├── qwen_dashscope.py
│   ├── qwenaudio_dashscope.py
│   ├── qwenomni_oai.py
│   ├── qwenvl_dashscope.py
│   ├── qwenvl_oai.py
│   ├── schema.py
│   ├── transformers_llm.py
│   ├── __pycache__/
├── memory/
│   ├── __init__.py
│   ├── memory.py
│   ├── __pycache__/
├── tools/
│   ├── __init__.py
│   ├── amap_weather.py
│   ├── base.py
│   ├── code_interpreter.py
│   ├── doc_parser.py
│   ├── extract_doc_vocabulary.py
│   ├── image_gen.py
│   ├── mcp_manager.py
│   ├── python_executor.py
│   ├── resource/
│   ├── retrieval.py
│   ├── search_tools/
│   ├── simple_doc_parser.py
│   ├── storage.py
│   ├── web_extractor.py
│   ├── web_search.py
│   ├── __pycache__/
├── utils/
│   ├── __init__.py
│   ├── output_beautify.py
│   ├── parallel_executor.py
│   ├── qwen.tiktoken
│   ├── str_processing.py
│   ├── tokenization_qwen.py
│   ├── utils.py
│   ├── __pycache__/
```

> 说明：部分子目录（如 doc_qa、keygen_strategies、resource、search_tools、assets、fncall_prompts、__pycache__）下还有更细的文件结构，可按需补充。 