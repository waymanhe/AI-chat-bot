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

from abc import ABC
from typing import List

from qwen_agent_local.agent import Agent
from qwen_agent_local.log import logger


class MultiAgentHub(ABC):

    @property
    def agents(self) -> List[Agent]:
        try:
            agent_list = self._agents
            assert isinstance(agent_list, list)
            assert all(isinstance(a, Agent) for a in agent_list)
            assert len(agent_list) > 0
            assert all(a.name for a in agent_list), 'All agents must have a name.'
            assert len(set(a.name for a in agent_list)) == len(agent_list), 'Agents must have unique names.'
        except (AttributeError, AssertionError) as e:
            logger.error(
                f'Class {self.__class__.__name__} inherits from MultiAgentHub. '
                'However, the following constraints are violated: '
                "1) A class that inherits from MultiAgentHub must have an '_agents' attribute of type 'List[Agent]'. "
                "2) The '_agents' must be a non-empty list containing at least one agent. "
                "3) All agents in '_agents' must have non-empty, non-duplicate string names.")
            raise e
        return agent_list

    @property
    def agent_names(self) -> List[str]:
        return [x.name for x in self.agents]

    @property
    def nonuser_agents(self):
        from qwen_agent_local.agents.user_agent import UserAgent  # put here to avoid cyclic import
        return [a for a in self.agents if not isinstance(a, UserAgent)]
