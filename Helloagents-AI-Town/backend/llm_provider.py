"""LLM 提供器。

- 配置了 API key 时返回真正的 HelloAgentsLLM。
- 否则返回 MockLLM：duck-type 兼容 SimpleAgent（invoke 返回带 .content 的对象），
  让整个项目无需 key 也能启动、联调和看日志。
"""
import random
import re
from typing import Dict, List, Optional

from config import settings


class MockResponse:
    """模拟 HelloAgentsLLM 的 LLMResponse：SimpleAgent 只读取 .content。"""

    def __init__(self, content: str):
        self.content = content
        self.usage: Dict = {}

    def __str__(self) -> str:
        return self.content


# 角色专属的口头禅 / 回复模板（mock 模式下让 NPC 有点个性）
_ROLE_FLAVOR = {
    "张三": [
        "（推了推眼镜）这个问题嘛，从代码角度看，{topic}其实可以写得更优雅。",
        "我刚在调一个 bug，不过你说的{topic}我有点想法，要不要看看实现？",
        "嗯，先把单元测试补上再说。关于{topic}，我建议别过早优化。",
    ],
    "李四": [
        "有意思！从用户角度想，{topic}的核心痛点到底是什么？我们得先搞清楚。",
        "我正好在写需求文档，你提到的{topic}可以列进下个迭代，说说你的想法？",
        "为什么会想到{topic}呢？多聊聊，我觉得这里有产品机会。",
    ],
    "王五": [
        "（端着咖啡）{topic}啊……我脑子里已经有画面了，配色可以更柔和一点。",
        "灵感来了！{topic}的视觉呈现我想做成像素风，你觉得呢？",
        "审美这种事见仁见智，不过{topic}我会优先考虑留白和呼吸感。",
    ],
}

_LEVEL_TONE = {
    "陌生": "（语气礼貌但略显客气）",
    "熟悉": "（语气自然了一些）",
    "友好": "（笑了笑，很热情）",
    "亲密": "（像老朋友一样）",
    "挚友": "（毫无保留地）",
}


class MockLLM:
    """无需联网的假 LLM。根据 system_prompt 里的 NPC 名 + 玩家输入生成像样的回复。"""

    def __init__(self, *args, **kwargs):
        # SimpleAgent/Agent 基类会读取这些属性
        self.model = "mock"
        self.temperature = 0.7

    # SimpleAgent.run 会调用这个
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> MockResponse:
        return MockResponse(self._generate(messages))

    # 兼容真实接口（流式）
    def think(self, messages: List[Dict[str, str]], temperature: Optional[float] = None):
        yield self._generate(messages)

    def ainvoke(self, messages: List[Dict[str, str]], **kwargs):  # pragma: no cover
        raise NotImplementedError("MockLLM 不支持异步，请用 invoke")

    # ----- 内部 -----
    def _generate(self, messages: List[Dict[str, str]]) -> str:
        system = next((m["content"] for m in messages if m.get("role") == "system"), "")
        user = next((m["content"] for m in reversed(messages) if m.get("role") == "user"), "")

        name = self._match_name(system)
        level = self._match_level(system)
        topic = self._topic(user)

        flavor_list = _ROLE_FLAVOR.get(name)
        if not flavor_list:
            return f"（{name or 'NPC'}）你说的“{topic}”，我想想哈。"

        tone = _LEVEL_TONE.get(level, "")
        line = random.choice(flavor_list).format(topic=topic)
        return f"{tone}{line}"

    @staticmethod
    def _match_name(system: str) -> str:
        m = re.search(r"你是([^，,。\n]+?)[，,]", system)
        return m.group(1).strip() if m else ""

    @staticmethod
    def _match_level(system: str) -> str:
        for lv in ("挚友", "亲密", "友好", "熟悉", "陌生"):
            if lv in system:
                return lv
        return "陌生"

    @staticmethod
    def _topic(user: str) -> str:
        user = (user or "").strip()
        if not user:
            return "这件事"
        return user if len(user) <= 12 else user[:12] + "…"


_real_llm = None


def get_llm():
    """返回 LLM 实例：真实优先，否则 mock。"""
    global _real_llm
    if settings.use_mock_effective:
        return MockLLM()

    if _real_llm is None:
        from hello_agents import HelloAgentsLLM  # 延迟导入
        kwargs = {"model": settings.LLM_MODEL, "api_key": settings.LLM_API_KEY}
        if settings.LLM_BASE_URL.strip():
            kwargs["base_url"] = settings.LLM_BASE_URL
        _real_llm = HelloAgentsLLM(**kwargs)
    return _real_llm


def is_mock() -> bool:
    return settings.use_mock_effective
