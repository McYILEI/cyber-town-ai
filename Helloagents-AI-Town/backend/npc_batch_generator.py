"""批量背景对话生成器：一次 LLM 调用生成所有 NPC 的“自言自语”。

mock 模式下 LLM 不会返回合法 JSON，会自动回退到内置的随机背景对话。
"""
import json
import random
from datetime import datetime
from typing import Dict, Optional

from config import NPC_ROLES
from llm_provider import get_llm

_FALLBACK = {
    "张三": ["这个 bug 真是见鬼了，已经调试两小时了……", "刚跑通的测试又红了，喝口咖啡冷静下。",
             "这段逻辑得重构一下，耦合太重了。"],
    "李四": ["嗯，这个功能的优先级需要重新评估一下。", "用户反馈挺有意思，得整理进需求池。",
             "下个迭代的目标要再聚焦一点。"],
    "王五": ["这杯咖啡的拉花真不错，灵感来了！", "这个配色还是太刺眼，再调一版。",
             "图标的圆角再大一点会更亲和。"],
}


class NPCBatchGenerator:
    def __init__(self):
        self.npc_configs = NPC_ROLES

    def generate_batch_dialogues(self, context: Optional[str] = None) -> Dict[str, str]:
        prompt = self._build_batch_prompt(context)
        try:
            resp = get_llm().invoke([
                {"role": "system", "content": "你是一个游戏NPC对话生成器，擅长创作自然真实的办公室对话。"},
                {"role": "user", "content": prompt},
            ])
            text = resp.content if hasattr(resp, "content") else str(resp)
            dialogues = json.loads(self._extract_json(text))
            # 只保留已知 NPC
            return {n: dialogues[n] for n in self.npc_configs if n in dialogues}
        except Exception:
            return self._fallback()

    def _fallback(self) -> Dict[str, str]:
        return {name: random.choice(lines) for name, lines in _FALLBACK.items()}

    @staticmethod
    def _extract_json(text: str) -> str:
        start, end = text.find("{"), text.rfind("}")
        return text[start:end + 1] if start != -1 and end != -1 else text

    def _get_current_context(self) -> str:
        hour = datetime.now().hour
        if hour < 11:
            return "上午工作时间，办公室刚开始忙碌"
        if hour < 14:
            return "午餐时间前后，节奏稍微放松"
        if hour < 18:
            return "下午工作时间，大家专注推进任务"
        return "傍晚加班时间，办公室安静下来"

    def _build_batch_prompt(self, context: Optional[str] = None) -> str:
        if context is None:
            context = self._get_current_context()
        descs = [
            f"- {name}（{cfg['title']}）：在{cfg['location']}{cfg['activity']}，性格{cfg['personality']}"
            for name, cfg in self.npc_configs.items()
        ]
        npc_desc_text = "\n".join(descs)
        return f"""请为 Datawhale 办公室的 3 个 NPC 生成当前的对话或行为描述。

【场景】{context}

【NPC信息】
{npc_desc_text}

【生成要求】
1. 每个 NPC 生成 1 句话（20-40 字）
2. 内容符合角色设定、当前活动和场景氛围
3. 可以是自言自语、工作状态描述或简单思考
4. 自然真实，像真实的办公室同事
5. **必须严格按照 JSON 格式返回**

【输出格式】（严格遵守）
{{"张三": "...", "李四": "...", "王五": "..."}}

请生成（只返回 JSON，不要其他内容）："""


_generator: Optional[NPCBatchGenerator] = None


def get_batch_generator() -> NPCBatchGenerator:
    global _generator
    if _generator is None:
        _generator = NPCBatchGenerator()
    return _generator
