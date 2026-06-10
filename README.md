# 赛博小镇 · Cyber Town AI

一个可运行的 **AI 小镇**：玩家在 Godot 引擎里自由走动，靠近 NPC 按 `E` 即可对话。每个 NPC 由大语言模型（通义千问 Qwen / 任意 OpenAI 兼容接口）驱动，拥有独立人设、记忆与好感度系统，还会在后台自动生成彼此之间的"日常对话"。

后端为手写的 **FastAPI** 服务，前端为 **Godot 4.5** 游戏，二者通过 HTTP 通信。无需 API Key 也能以内置 **mock 模式** 直接体验。

> 作者：**McYILEI**

---

## 🎬 演示视频

<video src="https://github.com/McYILEI/cyber-town-ai/raw/main/demo.mp4" controls width="100%"></video>

> 如果上方视频未自动加载，请点击直接观看 / 下载：[demo.mp4](demo.mp4)

---

## ✨ 特性

- 🧠 **LLM 驱动的 NPC**：每个角色有独立人设（Python 工程师、产品经理、UI 设计师）。
- ❤️ **好感度系统**：对话会影响 NPC 对玩家的好感等级与分数。
- 💬 **后台自动对话**：NPC 之间会按固定间隔自动生成背景闲聊。
- 🎮 **Godot 前端**：`WASD` 移动，靠近 NPC 按 `E` 触发对话。
- 🔌 **零门槛体验**：不填 API Key 时自动回退到内置 mock 回复，离线可玩。

## 🗂️ 项目结构

```
cyber-town-ai/
├── Helloagents-AI-Town/
│   ├── backend/                # FastAPI 后端
│   │   ├── main.py             # 入口与 API 路由
│   │   ├── agents.py           # NPC Agent 管理
│   │   ├── config.py           # 配置 + NPC 人设
│   │   ├── llm_provider.py     # LLM / mock 切换
│   │   ├── relationship_manager.py  # 好感度
│   │   ├── .env.example        # 配置模板（复制为 .env）
│   │   └── requirements.txt
│   ├── helloagents-ai-town/    # Godot 4.5 游戏工程
│   └── start.ps1               # Windows 一键启动脚本
├── demo.mp4                    # 演示视频
└── README.md
```

> 注：Godot 引擎二进制（约 230MB）超过 GitHub 单文件 100MB 限制，未包含在仓库中，请自行下载（见下文）。

## 🚀 快速开始

### 1. 准备 Godot 引擎

从 [godotengine.org](https://godotengine.org/download) 下载 **Godot 4.5（标准版）**，并把可执行文件放到项目同级的 `_tools/` 目录下，或将其加入系统 `PATH`。`start.ps1` 会自动定位。

### 2. 配置后端

```powershell
cd Helloagents-AI-Town/backend
copy .env.example .env
pip install -r requirements.txt
```

打开 `.env`：
- **想离线体验**：保持 `USE_MOCK=true` 即可，无需任何 Key。
- **想接入真实 LLM**：填入你自己的 `LLM_API_KEY`，并设 `USE_MOCK=false`。默认使用通义千问 Qwen（DashScope 兼容模式），也可改成任意 OpenAI 兼容服务。

> ⚠️ `.env` 已被 `.gitignore` 忽略，请勿把你的 API Key 提交到仓库。

### 3. 一键启动（Windows）

```powershell
cd Helloagents-AI-Town
./start.ps1
```

脚本会依次：启动后端 → 等待就绪 → 启动 Godot 游戏。

### 手动启动（可选）

```powershell
# 终端 1：后端
cd Helloagents-AI-Town/backend
python main.py        # http://127.0.0.1:8000 ，文档见 /docs

# 终端 2：用 Godot 打开 helloagents-ai-town 工程并运行
```

## 🎮 操作

| 操作 | 按键 |
| --- | --- |
| 移动 | `W` `A` `S` `D` |
| 与 NPC 对话 | 靠近后按 `E` |

## 🔧 技术栈

- **后端**：FastAPI · Uvicorn · Pydantic · [HelloAgents](https://github.com/datawhalechina)
- **前端**：Godot 4.5（GDScript）
- **模型**：通义千问 Qwen（DashScope 兼容模式），可替换为任意 OpenAI 兼容接口

## 📡 主要 API

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| `GET` | `/` | 服务状态 |
| `GET` | `/npcs/status` | 所有 NPC 状态 + 背景对话 |
| `POST` | `/chat` | 与指定 NPC 对话（前端使用） |
| `GET` | `/affinity/{npc_id}/{player_name}` | 查询好感度 |

## 🙏 致谢

本项目是对 Datawhale **HelloAgents · AI Town** 思路的一个可运行复刻实现，前端美术资源沿用其开源工程。感谢 Datawhale 社区。

## 📄 License

MIT
