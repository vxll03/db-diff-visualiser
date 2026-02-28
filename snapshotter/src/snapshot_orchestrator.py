import asyncio
import json
from pathlib import Path

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from loguru import logger

from src.core.config import settings
from src.snapshotter.alembic_snapshotter import AlembicSnapshotter
from src.snapshotter.base_snapshotter import BaseSnapshotWorker


class SnapshotOrchestrator:
    _MESSAGE_MAPPINGS: dict[str, type[BaseSnapshotWorker]] = {
        "alembic": AlembicSnapshotter,
    }

    def __init__(self, work_dir: Path):
        self._work_dir = work_dir
        self.connection = None

    async def run(self):
        self.connection = await aio_pika.connect_robust(settings.rabbit.URL)
        async with self.connection:
            channel = await self.connection.channel()
            await channel.set_qos(prefetch_count=1)
            queue = await channel.declare_queue(
                settings.rabbit.MIGRATION_TASK_QUEUE, durable=True
            )

            await queue.consume(self._start_worker)
            await asyncio.Future()

    async def _send_result(
        self, project_name: str, revision_id: str, prev_revision_id: str | None
    ):
        if not self.connection:
            return
        payload = {
            "project": project_name,
            "revision_id": revision_id,
            "prev_revision_id": prev_revision_id,
        }
        async with self.connection.channel() as channel:
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key="task_results",
            )

    async def _start_worker(self, message: AbstractIncomingMessage):
        async with message.process():
            data = json.loads(message.body.decode())

            worker: type[BaseSnapshotWorker] | None = self._MESSAGE_MAPPINGS.get(
                data.get("type")
            )
            if not worker:
                raise ValueError("Unknown message type")

            project_name = data.get("project")
            target_revision = data.get("target_revision", "head")

            instance = worker(self._work_dir)
            result = await asyncio.to_thread(
                instance.process,
                project_name=project_name,
                target_revision=target_revision,
            )

            if not result:
                logger.error('process result is None')
                return
            rev_id, prev_rev_id = result

            await self._send_result(
                project_name=project_name,
                revision_id=rev_id,
                prev_revision_id=prev_rev_id,
            )
