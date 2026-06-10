"""赛博小镇后端：FastAPI 主程序。"""
import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool

from agents import NPCAgentManager
from config import resolve_npc, settings
from llm_provider import is_mock
from logger import DialogueLogger
from models import (AffinityInfo, ChatRequest, ChatResponse, DialogueRequest,
                    DialogueResponse, NPCStatusResponse)
from npc_batch_generator import get_batch_generator
from relationship_manager import RelationshipManager
from state_manager import StateManager

agent_manager = NPCAgentManager()
relationship_manager = RelationshipManager()
state_manager = StateManager()
dialogue_logger = DialogueLogger(settings.LOG_DIR)


async def _background_dialogue_update():
    """后台任务：定期批量刷新 NPC 背景对话。"""
    generator = get_batch_generator()
    while True:
        try:
            dialogues = await run_in_threadpool(generator.generate_batch_dialogues)
            for name, text in dialogues.items():
                state_manager.update_npc_background_dialogue(name, text)
            dialogue_logger.log_info(f"✅ 背景对话更新完成: {len(dialogues)} 个 NPC")
        except Exception as e:  # noqa: BLE001
            dialogue_logger.log_error(f"❌ 背景对话更新失败: {e}")
        await asyncio.sleep(settings.BATCH_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print("🎮 赛博小镇后端服务启动中...")
    print("=" * 60)
    agent_manager.initialize_npcs()
    print("✅ NPC Agents 已初始化")
    state_manager.initialize_npcs()
    print("✅ 状态管理器已初始化")
    print(f"🤖 LLM 模式: {'MOCK（无需 API key）' if is_mock() else '真实 LLM: ' + settings.LLM_MODEL}")
    task = asyncio.create_task(_background_dialogue_update())
    print("✅ 所有服务已启动!")
    print(f"📡 API地址: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 API文档: http://{settings.HOST}:{settings.PORT}/docs")
    print("=" * 60)
    yield
    task.cancel()


app = FastAPI(title="赛博小镇后端服务",
              description="基于 HelloAgents 的 AI NPC 对话系统",
              version="1.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])


@app.get("/")
async def root():
    return {"status": "running", "message": "赛博小镇后端服务正在运行",
            "version": "1.0.0", "mock": is_mock(),
            "npcs": state_manager.get_npc_count()}


@app.get("/npcs")
async def get_npcs():
    return {"npcs": state_manager.get_all_npc_states()}


@app.get("/npcs/status", response_model=NPCStatusResponse)
async def get_npc_status():
    return {"npcs": state_manager.get_all_npc_states(),
            "dialogues": state_manager.get_background_dialogues()}


@app.get("/npcs/{npc_id}/status")
async def get_single_npc_status(npc_id: str):
    npc = state_manager.get_npc_state(npc_id)
    if not npc:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} 不存在")
    return npc


@app.get("/affinity/{npc_id}/{player_name}", response_model=AffinityInfo)
async def get_affinity(npc_id: str, player_name: str):
    if not agent_manager.has_npc(npc_id):
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} 不存在")
    return relationship_manager.get_affinity(npc_id, player_name)


async def _handle_dialogue(npc_key: str, player_name: str, player_message: str) -> dict:
    """对话核心逻辑，被 /chat 和 /dialogue 共用。"""
    npc = resolve_npc(npc_key)
    if not npc:
        raise HTTPException(status_code=404, detail=f"NPC {npc_key} 不存在")
    npc_id = npc["npc_id"]

    if state_manager.is_npc_busy(npc_id):
        raise HTTPException(status_code=409, detail=f"NPC {npc['name']} 正在与其他玩家对话")

    state_manager.set_npc_busy(npc_id, True)
    try:
        affinity = relationship_manager.get_affinity(npc_id, player_name)
        # agent.run 是同步阻塞调用，丢到线程池里执行，避免阻塞事件循环
        reply = await run_in_threadpool(
            agent_manager.chat, npc_id, player_message, affinity["level"])

        new_affinity = relationship_manager.update_affinity(
            npc_id, player_name, player_message, reply)

        dialogue_logger.log_dialogue(
            npc_id=npc_id, player_name=player_name, player_message=player_message,
            npc_reply=reply, affinity_info=new_affinity, extra=new_affinity)

        return {"npc": npc, "reply": reply, "affinity": new_affinity}
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        dialogue_logger.log_error(f"对话处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"对话处理失败: {e}")
    finally:
        state_manager.set_npc_busy(npc_id, False)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Godot 前端使用的对话接口。"""
    result = await _handle_dialogue(request.npc_name, request.player_name, request.message)
    return ChatResponse(success=True, npc_name=result["npc"]["name"], message=result["reply"],
                        affinity_level=result["affinity"]["level"],
                        affinity_score=result["affinity"]["score"])


@app.post("/dialogue", response_model=DialogueResponse)
async def dialogue(request: DialogueRequest):
    """书中风格的对话接口（按 npc_id）。"""
    result = await _handle_dialogue(request.npc_id, request.player_name, request.player_message)
    return DialogueResponse(npc_reply=result["reply"],
                            affinity_level=result["affinity"]["level"],
                            affinity_score=result["affinity"]["score"])


if __name__ == "__main__":
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, log_level="info")
