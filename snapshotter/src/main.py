import asyncio
from pathlib import Path

from loguru import logger

from snapshotter import SnapshotWorker

if __name__ == "__main__":
    try:
        CURRENT_DIR = Path(__file__).resolve().parent
        worker = SnapshotWorker(CURRENT_DIR)
        asyncio.run(worker.run())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
