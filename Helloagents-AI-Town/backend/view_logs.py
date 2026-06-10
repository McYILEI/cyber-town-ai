"""实时查看今天的对话日志（类似 tail -f）。"""
import time
from datetime import datetime
from pathlib import Path

from config import settings


def main():
    log_dir = Path(settings.LOG_DIR)
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = log_dir / f"dialogue_{today}.log"

    print(f"📜 正在监视日志: {log_file}")
    print("按 Ctrl+C 退出\n" + "=" * 60)

    while not log_file.exists():
        print("等待日志文件生成…")
        time.sleep(1)

    with open(log_file, "r", encoding="utf-8") as f:
        # 先打印已有内容
        print(f.read(), end="")
        # 再持续跟踪新内容
        try:
            while True:
                line = f.readline()
                if line:
                    print(line, end="")
                else:
                    time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n👋 已退出日志查看")


if __name__ == "__main__":
    main()
