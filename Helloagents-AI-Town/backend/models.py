"""Pydantic 数据模型：请求 / 响应。"""
from typing import Dict, List
from pydantic import BaseModel, Field


# ---- Godot 前端使用的对话接口（/chat）----
class ChatRequest(BaseModel):
    npc_name: str = Field(..., description="NPC 名字或 id")
    message: str = Field(..., description="玩家输入")
    player_name: str = Field("玩家", description="玩家名")


class ChatResponse(BaseModel):
    success: bool = True
    npc_name: str
    message: str
    affinity_level: str
    affinity_score: int


# ---- 书中风格的对话接口（/dialogue）----
class DialogueRequest(BaseModel):
    npc_id: str
    player_name: str = "玩家"
    player_message: str


class DialogueResponse(BaseModel):
    npc_reply: str
    affinity_level: str
    affinity_score: int


# ---- 好感度 ----
class AffinityInfo(BaseModel):
    score: int
    level: str
    interaction_count: int


# ---- NPC 状态 ----
class NPCState(BaseModel):
    npc_id: str
    name: str
    title: str
    position: Dict[str, int]
    is_busy: bool
    current_action: str
    background_dialogue: str


class NPCStatusResponse(BaseModel):
    npcs: List[NPCState]
    dialogues: Dict[str, str]
