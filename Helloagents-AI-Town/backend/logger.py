"""对话日志：同时输出到控制台和按天分文件的日志。"""
import logging
from datetime import datetime
from pathlib import Path


class DialogueLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"dialogue_{today}.log"

        self.logger = logging.getLogger("DialogueLogger")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        # 避免重复添加 handler（多次实例化 / reload 时）
        if not self.logger.handlers:
            console = logging.StreamHandler()
            console.setFormatter(logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"))
            self.logger.addHandler(console)

            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
            self.logger.addHandler(fh)

    def log_dialogue(self, npc_id, player_name, player_message, npc_reply,
                     affinity_info, extra: dict | None = None):
        extra = extra or {}
        change = extra.get("change")
        reason = extra.get("reason", "")
        sentiment = extra.get("sentiment", "")
        change_str = f"{change:+.1f}" if isinstance(change, (int, float)) else str(change)
        msg = f"""
{'=' * 60}
NPC: {npc_id}
玩家: {player_name}
玩家消息: {player_message}
NPC回复: {npc_reply}
好感度: {affinity_info['level']} ({affinity_info['score']}/100)  变化: {change_str}
变化原因: {reason}   情感: {sentiment}
互动次数: {affinity_info['interaction_count']}
{'=' * 60}"""
        self.logger.info(msg)

    def log_info(self, message: str):
        self.logger.info(message)

    def log_error(self, message: str):
        self.logger.error(message)
