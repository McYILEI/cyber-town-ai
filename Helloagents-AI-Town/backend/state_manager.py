"""NPC 状态管理：位置、忙碌状态、背景对话。"""
from datetime import datetime
from typing import Dict, List, Optional

from config import NPCS


class StateManager:
    def __init__(self):
        self.npc_states: Dict[str, dict] = {}

    def initialize_npcs(self):
        for npc in NPCS:
            self.npc_states[npc["npc_id"]] = {
                "npc_id": npc["npc_id"],
                "name": npc["name"],
                "title": npc["title"],
                "position": npc["position"],
                "is_busy": False,
                "current_action": "idle",
                "last_interaction": None,
                "background_dialogue": f"正在{npc['activity']}…",
            }

    def get_npc_state(self, npc_id: str) -> Optional[dict]:
        return self.npc_states.get(npc_id)

    def get_all_npc_states(self) -> List[dict]:
        return list(self.npc_states.values())

    def is_npc_busy(self, npc_id: str) -> bool:
        npc = self.npc_states.get(npc_id)
        return npc["is_busy"] if npc else False

    def set_npc_busy(self, npc_id: str, busy: bool):
        if npc_id in self.npc_states:
            self.npc_states[npc_id]["is_busy"] = busy
            if busy:
                self.npc_states[npc_id]["last_interaction"] = datetime.now().isoformat()

    def update_npc_background_dialogue(self, npc_key: str, dialogue: str):
        """npc_key 可以是 id 或中文名。"""
        for state in self.npc_states.values():
            if npc_key in (state["npc_id"], state["name"]):
                state["background_dialogue"] = dialogue
                return

    def get_background_dialogues(self) -> Dict[str, str]:
        """返回 {中文名: 背景对话}，供前端气泡显示。"""
        return {s["name"]: s["background_dialogue"] for s in self.npc_states.values()}

    def get_npc_count(self) -> int:
        return len(self.npc_states)
