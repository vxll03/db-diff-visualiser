import asyncio
from pathlib import Path

from loguru import logger

from src.snapshot_orchestrator import SnapshotOrchestrator

if __name__ == "__main__":
    try:
        CURRENT_DIR = Path(__file__).resolve().parent
        orchestrator = SnapshotOrchestrator(CURRENT_DIR)
        asyncio.run(orchestrator.run())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
