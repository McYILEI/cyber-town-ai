"""NPC 智能体系统：每个 NPC 一个持久化的 SimpleAgent（内置对话历史 = 记忆）。

注意：published 的 hello_agents 1.0.0 没有 hello_agents.memory 模块，
因此这里用 SimpleAgent 自带的 history 作为短期记忆，而非书中的 MemoryManager。
"""
from typing import Dict, Optional

from hello_agents import Config, SimpleAgent

from config import NPCS, NPC_BY_ID, resolve_npc
from llm_provider import get_llm

AFFINITY_PROMPTS = {
    "陌生": "你刚认识这位玩家，保持礼貌但不要过于热情，回复简短专业。",
    "熟悉": "你已经认识这位玩家，可以进行正常的交流，回复自然友好。",
    "友好": "你把这位玩家当作朋友，愿意分享更多信息，回复详细热情。",
    "亲密": "你非常信任这位玩家，可以分享私人话题，回复充满关心。",
    "挚友": "你把这位玩家当作最好的朋友，无话不谈，回复亲切真诚。",
}


def _build_system_prompt(name: str, title: str, personality: str, level: str) -> str:
    return f"""你是{name}，一位{title}。
你的性格特点：{personality}

当前与玩家的关系：{level}
{AFFINITY_PROMPTS.get(level, AFFINITY_PROMPTS['陌生'])}

你在 Datawhale 办公室工作，与同事们一起推动开源社区的发展。
请根据你的角色、性格和与玩家的关系，自然地用中文回复。回复控制在 2-4 句话。"""


class NPCAgentManager:
    def __init__(self):
        self.agents: Dict[str, SimpleAgent] = {}

    def initialize_npcs(self):
        llm = get_llm()
        config = Config(trace_enabled=False)  # 关闭 trace 文件输出
        for npc in NPCS:
            prompt = _build_system_prompt(
                npc["name"], npc["title"], npc["personality"], "陌生")
            self.agents[npc["npc_id"]] = SimpleAgent(
                name=npc["name"],
                llm=llm,
                system_prompt=prompt,
                config=config,
                enable_tool_calling=False,  # NPC 不需要工具调用
            )

    def has_npc(self, npc_key: str) -> bool:
        return resolve_npc(npc_key) is not None

    def get_agent(self, npc_key: str, affinity_level: str = "陌生") -> Optional[SimpleAgent]:
        """取得 NPC 的 Agent，并按当前好感度动态调整 system_prompt（保留历史记忆）。"""
        npc = resolve_npc(npc_key)
        if not npc:
            return None
        agent = self.agents.get(npc["npc_id"])
        if agent is None:
            return None
        # 动态更新好感度对应的系统提示词（不重建 Agent，保留对话历史）
        agent.system_prompt = _build_system_prompt(
            npc["name"], npc["title"], npc["personality"], affinity_level)
        return agent

    def chat(self, npc_key: str, player_message: str, affinity_level: str = "陌生") -> str:
        agent = self.get_agent(npc_key, affinity_level)
        if agent is None:
            raise KeyError(npc_key)
        return agent.run(player_message)
