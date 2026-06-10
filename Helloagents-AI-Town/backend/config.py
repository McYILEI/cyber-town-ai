"""配置管理：读取 .env，并集中定义所有 NPC 的角色设定。"""
from typing import Dict, List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """后端配置，可通过 .env 覆盖。"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 服务
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # LLM（留空则自动使用 mock 回复，无需 API key 也能跑）
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = ""
    USE_MOCK: bool = True  # True 或未配置 key 时，使用内置 mock LLM

    # 后台背景对话刷新间隔（秒）
    BATCH_INTERVAL_SECONDS: int = 60

    # 日志目录
    LOG_DIR: str = "logs"

    @property
    def use_mock_effective(self) -> bool:
        """实际是否使用 mock：显式开启，或没有提供 API key。"""
        return self.USE_MOCK or not self.LLM_API_KEY.strip()


settings = Settings()


# ---------------------------------------------------------------------------
# NPC 角色定义（单一数据源，state / agents / batch 都从这里取）
# ---------------------------------------------------------------------------
NPCS: List[dict] = [
    {
        "npc_id": "zhang_san",
        "name": "张三",
        "title": "Python工程师",
        "personality": "严谨、专业、喜欢分享技术知识，说话直接，注重代码质量。",
        "location": "工位",
        "activity": "调试 HelloAgents 框架的核心代码",
        "position": {"x": 300, "y": 200},
    },
    {
        "npc_id": "li_si",
        "name": "李四",
        "title": "产品经理",
        "personality": "外向、善于沟通、注重用户体验，喜欢从用户角度思考问题。",
        "location": "会议区",
        "activity": "梳理下一版本的产品需求",
        "position": {"x": 500, "y": 200},
    },
    {
        "npc_id": "wang_wu",
        "name": "王五",
        "title": "UI设计师",
        "personality": "温和、富有创意、审美独特，注重视觉呈现和用户体验。",
        "location": "设计角",
        "activity": "打磨界面配色和图标",
        "position": {"x": 700, "y": 200},
    },
]

# 便捷映射
NPC_BY_ID: Dict[str, dict] = {n["npc_id"]: n for n in NPCS}
NPC_BY_NAME: Dict[str, dict] = {n["name"]: n for n in NPCS}
# 批量生成器使用的 name -> 配置
NPC_ROLES: Dict[str, dict] = {n["name"]: n for n in NPCS}


def resolve_npc(npc_key: str) -> dict | None:
    """通过 npc_id 或中文名解析 NPC 配置。"""
    return NPC_BY_ID.get(npc_key) or NPC_BY_NAME.get(npc_key)
