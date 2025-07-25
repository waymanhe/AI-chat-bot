# Copyright 2023 The Qwen team, Alibaba Group. All rights reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#    http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pprint
import re
from typing import List, Optional, Union

from qwen_agent_local import Agent, MultiAgentHub
from qwen_agent_local.agents.user_agent import PENDING_USER_INPUT
from qwen_agent_local.gui.gradio_utils import format_cover_html
from qwen_agent_local.gui.utils import convert_fncall_to_text, convert_history_to_chatbot, get_avatar_image
from qwen_agent_local.llm.schema import AUDIO, CONTENT, FILE, IMAGE, NAME, ROLE, USER, VIDEO, Message
from qwen_agent_local.log import logger
from qwen_agent_local.utils.utils import print_traceback


class WebUI:
    """A Common chatbot application for agent."""

    def __init__(self, agent: Union[Agent, MultiAgentHub, List[Agent]], chatbot_config: Optional[dict] = None):
        """
        Initialization the chatbot.

        Args:
            agent: The agent or a list of agents,
                supports various types of agents such as Assistant, GroupChat, Router, etc.
            chatbot_config: The chatbot configuration.
                Set the configuration as {'user.name': '', 'user.avatar': '', 'agent.avatar': '', 'input.placeholder': '', 'prompt.suggestions': []}.
        """
        chatbot_config = chatbot_config or {}

        if isinstance(agent, MultiAgentHub):
            self.agent_list = [agent for agent in agent.nonuser_agents]
            self.agent_hub = agent
        elif isinstance(agent, list):
            self.agent_list = agent
            self.agent_hub = None
        else:
            self.agent_list = [agent]
            self.agent_hub = None

        user_name = chatbot_config.get('user.name', 'user')
        self.user_config = {
            'name': user_name,
            'avatar': chatbot_config.get(
                'user.avatar',
                get_avatar_image(user_name),
            ),
        }

        self.agent_config_list = [{
            'name': agent.name,
            'avatar': chatbot_config.get(
                'agent.avatar',
                get_avatar_image(agent.name),
            ),
            'description': agent.description or "集合了本地知识库和互联网搜索的AI助手.",
        } for agent in self.agent_list]

        self.input_placeholder = chatbot_config.get('input.placeholder', '跟我聊聊吧～')
        self.prompt_suggestions = chatbot_config.get('prompt.suggestions', [])
        self.verbose = chatbot_config.get('verbose', False)

    """
    Run the chatbot.

    Args:
        messages: The chat history.
    """

    def run(self,
            messages: List[Message] = None,
            share: bool = False,
            server_name: str = None,
            server_port: int = None,
            concurrency_limit: int = 10,
            enable_mention: bool = False,
            **kwargs):
        self.run_kwargs = kwargs

        from qwen_agent_local.gui.gradio_dep import gr, mgr, ms

        customTheme = gr.themes.Default(
            primary_hue=gr.themes.utils.colors.blue,
            radius_size=gr.themes.utils.sizes.radius_none,
        )

        with gr.Blocks(
                css="qwen_agent_local/gui/assets/app.css",
                theme=customTheme,
        ) as demo:
            history = gr.State([])
            with ms.Application():
                with gr.Row(elem_classes='container'):
                    with gr.Column(scale=4):
                        chatbot = mgr.Chatbot(value=convert_history_to_chatbot(messages=messages),
                                              avatar_images=[
                                                  self.user_config,
                                                  self.agent_config_list,
                                              ],
                                              height=850,
                                              avatar_image_width=80,
                                              flushing=False,
                                              show_copy_button=True,
                                              latex_delimiters=[{
                                                  'left': '\\(',
                                                  'right': '\\)',
                                                  'display': True
                                              }, {
                                                  'left': '\\begin{equation}',
                                                  'right': '\\end{equation}',
                                                  'display': True
                                              }, {
                                                  'left': '\\begin{align}',
                                                  'right': '\\end{align}',
                                                  'display': True
                                              }, {
                                                  'left': '\\begin{alignat}',
                                                  'right': '\\end{alignat}',
                                                  'display': True
                                              }, {
                                                  'left': '\\begin{gather}',
                                                  'right': '\\end{gather}',
                                                  'display': True
                                              }, {
                                                  'left': '\\begin{CD}',
                                                  'right': '\\end{CD}',
                                                  'display': True
                                              }, {
                                                  'left': '\\[',
                                                  'right': '\\]',
                                                  'display': True
                                              }])

                        input = mgr.MultimodalInput(placeholder=self.input_placeholder,)
                        audio_input = gr.Audio(
                            sources=["microphone"],
                            type="filepath"
                        )

                    with gr.Column(scale=1):
                        # 侧边栏四个按钮，点击弹出“暂未实现，敬请期待”
                        search_btn = gr.Button("搜索")
                        kb_btn = gr.Button("知识库")
                        fav_btn = gr.Button("收藏")
                        history_btn = gr.Button("历史")
                        for btn in [search_btn, kb_btn, fav_btn, history_btn]:
                            btn.click(lambda: gr.Info("暂未实现，敬请期待"), outputs=None)

                        if len(self.agent_list) > 1:
                            agent_selector = gr.Dropdown(
                                [(agent.name, i) for i, agent in enumerate(self.agent_list)],
                                label='Agents',
                                info='选择一个Agent',
                                value=0,
                                interactive=True,
                            )

                        agent_info_block = self._create_agent_info_block()

                        agent_plugins_block = self._create_agent_plugins_block()

                        if self.prompt_suggestions:
                            gr.Examples(
                                label='推荐对话',
                                examples=self.prompt_suggestions,
                                inputs=[input],
                            )

                    if len(self.agent_list) > 1:
                        agent_selector.change(
                            fn=self.change_agent,
                            inputs=[agent_selector],
                            outputs=[agent_selector, agent_info_block, agent_plugins_block],
                            queue=False,
                        )

                    input_promise = input.submit(
                        fn=self.add_text,
                        inputs=[input, audio_input, chatbot, history],
                        outputs=[input, audio_input, chatbot, history],
                        queue=False,
                    )

                    if len(self.agent_list) > 1 and enable_mention:
                        input_promise = input_promise.then(
                            self.add_mention,
                            [chatbot, agent_selector],
                            [chatbot, agent_selector],
                        ).then(
                            self.agent_run,
                            [chatbot, history, agent_selector],
                            [chatbot, history, agent_selector],
                        )
                    else:
                        input_promise = input_promise.then(
                            self.agent_run,
                            [chatbot, history],
                            [chatbot, history],
                        )

                    input_promise.then(self.flushed, None, [input])

            demo.load(None)

        demo.queue(default_concurrency_limit=concurrency_limit).launch(share=share,
                                                                       server_name=server_name,
                                                                       server_port=server_port)

    def change_agent(self, agent_selector):
        yield agent_selector, self._create_agent_info_block(agent_selector), self._create_agent_plugins_block(
            agent_selector)

    def add_text(self, _input, _audio_input, _chatbot, _history):
        _history.append({
            ROLE: USER,
            CONTENT: [{
                'text': _input.text
            }],
        })

        if self.user_config[NAME]:
            _history[-1][NAME] = self.user_config[NAME]
        
        # if got audio from microphone, append it to the multimodal inputs
        if _audio_input:
            from qwen_agent_local.gui.gradio_dep import gr, mgr, ms
            audio_input_file = gr.data_classes.FileData(path=_audio_input, mime_type="audio/wav")
            _input.files.append(audio_input_file)

        if _input.files:
            for file in _input.files:
                if file.mime_type.startswith('image/'):
                    _history[-1][CONTENT].append({IMAGE: 'file://' + file.path})
                elif file.mime_type.startswith('audio/'):
                    _history[-1][CONTENT].append({AUDIO: 'file://' + file.path})
                elif file.mime_type.startswith('video/'):
                    _history[-1][CONTENT].append({VIDEO: 'file://' + file.path})
                else:
                    _history[-1][CONTENT].append({FILE: file.path})

        _chatbot.append([_input, None])

        from qwen_agent_local.gui.gradio_dep import gr

        yield gr.update(interactive=False, value=None), None, _chatbot, _history

    def add_mention(self, _chatbot, _agent_selector):
        if len(self.agent_list) == 1:
            yield _chatbot, _agent_selector

        query = _chatbot[-1][0].text
        match = re.search(r'@\w+\b', query)
        if match:
            _agent_selector = self._get_agent_index_by_name(match.group()[1:])

        agent_name = self.agent_list[_agent_selector].name

        if ('@' + agent_name) not in query and self.agent_hub is None:
            _chatbot[-1][0].text = '@' + agent_name + ' ' + query

        yield _chatbot, _agent_selector

    def agent_run(self, _chatbot, _history, _agent_selector=None):
        if self.verbose:
            logger.info('agent_run input:\n' + pprint.pformat(_history, indent=2))

        num_input_bubbles = len(_chatbot) - 1
        num_output_bubbles = 1
        _chatbot[-1][1] = [None for _ in range(len(self.agent_list))]

        agent_runner = self.agent_list[_agent_selector or 0]
        if self.agent_hub:
            agent_runner = self.agent_hub
        responses = []
        for responses in agent_runner.run(_history, **self.run_kwargs):
            if not responses:
                continue
            if responses[-1][CONTENT] == PENDING_USER_INPUT:
                logger.info('Interrupted. Waiting for user input!')
                break

            display_responses = convert_fncall_to_text(responses)
            if not display_responses:
                continue
            if display_responses[-1][CONTENT] is None:
                continue

            while len(display_responses) > num_output_bubbles:
                # Create a new chat bubble
                _chatbot.append([None, None])
                _chatbot[-1][1] = [None for _ in range(len(self.agent_list))]
                num_output_bubbles += 1

            assert num_output_bubbles == len(display_responses)
            assert num_input_bubbles + num_output_bubbles == len(_chatbot)

            for i, rsp in enumerate(display_responses):
                agent_index = self._get_agent_index_by_name(rsp[NAME])
                _chatbot[num_input_bubbles + i][1][agent_index] = rsp[CONTENT]

            if len(self.agent_list) > 1:
                _agent_selector = agent_index

            if _agent_selector is not None:
                yield _chatbot, _history, _agent_selector
            else:
                yield _chatbot, _history

        if responses:
            _history.extend([res for res in responses if res[CONTENT] != PENDING_USER_INPUT])

        if _agent_selector is not None:
            yield _chatbot, _history, _agent_selector
        else:
            yield _chatbot, _history

        if self.verbose:
            logger.info('agent_run response:\n' + pprint.pformat(responses, indent=2))

    def flushed(self):
        from qwen_agent_local.gui.gradio_dep import gr

        return gr.update(interactive=True)

    def _get_agent_index_by_name(self, agent_name):
        if agent_name is None:
            return 0

        try:
            agent_name = agent_name.strip()
            for i, agent in enumerate(self.agent_list):
                if agent.name == agent_name:
                    return i
            return 0
        except Exception:
            print_traceback()
            return 0

    def _create_agent_info_block(self, agent_index=0):
        from qwen_agent_local.gui.gradio_dep import gr

        agent_config_interactive = self.agent_config_list[agent_index]

        return gr.HTML(
            format_cover_html(
                bot_name=agent_config_interactive['name'],
                bot_description=agent_config_interactive['description'],
                bot_avatar=agent_config_interactive['avatar'],
            ))

    def _create_agent_plugins_block(self, agent_index=0):
        from qwen_agent_local.gui.gradio_dep import gr

        agent_interactive = self.agent_list[agent_index]

        if agent_interactive.function_map:
            capabilities = [key for key in agent_interactive.function_map.keys()]
            return gr.CheckboxGroup(
                label='插件',
                value=capabilities,
                choices=capabilities,
                interactive=False,
            )

        else:
            return gr.CheckboxGroup(
                label='插件',
                value=[],
                choices=[],
                interactive=False,
            )
