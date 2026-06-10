"""好感度管理：五级好感度 + 情感分析。

mock 模式下用关键词启发式给出分数变化（保证日志里能看到真实变化）；
配置了真实 LLM 时，优先用 LLM 判断情感。
"""
from typing import Dict

from llm_provider import get_llm, is_mock

POSITIVE_WORDS = ["谢谢", "感谢", "你好", "厉害", "棒", "赞", "喜欢", "哈哈", "辛苦",
                  "加油", "佩服", "牛", "酷", "开心", "太好了", "请教", "麻烦你"]
NEGATIVE_WORDS = ["笨", "垃圾", "讨厌", "滚", "闭嘴", "无聊", "傻", "烦", "差劲", "废物"]


class RelationshipManager:
    def __init__(self):
        self.affinity_data: Dict[str, dict] = {}

    # ---- 情感分析 ----
    def analyze_sentiment(self, player_message: str, npc_reply: str) -> dict:
        """返回 {change, reason, sentiment}。"""
        if not is_mock():
            try:
                return self._analyze_with_llm(player_message, npc_reply)
            except Exception:
                pass  # LLM 失败时退回启发式
        return self._analyze_heuristic(player_message)

    def _analyze_with_llm(self, player_message: str, npc_reply: str) -> dict:
        prompt = f"""分析以下对话中玩家的态度：
玩家: {player_message}
NPC: {npc_reply}

判断玩家态度并只返回一个数字：
友好返回 5，中立返回 2，不友好返回 -3。
只返回数字，不要其他内容。"""
        resp = get_llm().invoke([{"role": "user", "content": prompt}])
        text = (resp.content if hasattr(resp, "content") else str(resp)).strip()
        num = int("".join(ch for ch in text if ch in "-0123456789") or "2")
        num = max(-3, min(5, num))
        sentiment = "positive" if num > 2 else ("negative" if num < 0 else "neutral")
        reason = {"positive": "友好交流", "neutral": "正常交流", "negative": "态度冷淡"}[sentiment]
        return {"change": float(num), "reason": reason, "sentiment": sentiment}

    def _analyze_heuristic(self, player_message: str) -> dict:
        msg = player_message or ""
        pos = sum(w in msg for w in POSITIVE_WORDS)
        neg = sum(w in msg for w in NEGATIVE_WORDS)
        if neg > pos:
            return {"change": -3.0, "reason": "态度冷淡", "sentiment": "negative"}
        if pos > 0:
            change = min(5.0, 2.0 + pos)
            return {"change": change, "reason": "友好问候", "sentiment": "positive"}
        return {"change": 2.0, "reason": "正常交流", "sentiment": "neutral"}

    # ---- 好感度读写 ----
    def _ensure(self, key: str) -> dict:
        if key not in self.affinity_data:
            self.affinity_data[key] = {"score": 0, "level": "陌生", "interaction_count": 0}
        return self.affinity_data[key]

    def get_affinity(self, npc_id: str, player_name: str) -> dict:
        return dict(self._ensure(f"{npc_id}_{player_name}"))

    def update_affinity(self, npc_id: str, player_name: str,
                        player_message: str, npc_reply: str) -> dict:
        key = f"{npc_id}_{player_name}"
        data = self._ensure(key)

        analysis = self.analyze_sentiment(player_message, npc_reply)
        new_score = max(0, min(100, int(round(data["score"] + analysis["change"]))))

        data.update({
            "score": new_score,
            "level": self.get_affinity_level(new_score),
            "interaction_count": data["interaction_count"] + 1,
        })
        # 把本次分析附在返回值里，方便记日志
        result = dict(data)
        result.update(analysis)
        return result

    @staticmethod
    def get_affinity_level(score: int) -> str:
        if score <= 20:
            return "陌生"
        elif score <= 40:
            return "熟悉"
        elif score <= 60:
            return "友好"
        elif score <= 80:
            return "亲密"
        return "挚友"
