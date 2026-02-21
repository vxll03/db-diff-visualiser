import asyncio
import json

import aio_pika
from aio_pika.abc import AbstractIncomingMessage
from loguru import logger
from pydantic import ValidationError

from src.core.config import settings
from src.core.database import get_db_context
from src.schemas.rabbit_schemas import IncomingMessageSchema
from src.services.file_service import FileService
from src.services.project_service import ProjectService


class RabbitService:
    def __init__(self):
        self._connection = None

    async def _get_connection(self):
        if self._connection is None or self._connection.is_closed:
            self._connection = await aio_pika.connect_robust(settings.rabbit.URL)
        return self._connection

    async def publish_task(self, project_name: str, revision: str):
        connection = await self._get_connection()
        async with connection.channel() as channel:
            await channel.declare_queue(
                settings.rabbit.MIGRATION_TASK_QUEUE, durable=True
            )

            payload = {
                "project": project_name,
                "target_revision": revision,
            }

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(payload).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key="migration_tasks",
            )
        logger.info(f"Task sent for {project_name}")

    async def consume_results(self):
        connection = await self._get_connection()
        channel = await connection.channel()

        await channel.set_qos(prefetch_count=1)
        queue = await channel.declare_queue(
            settings.rabbit.TASK_RESULT_QUEUE, durable=True
        )
        await queue.consume(self._process_result)
        try:
            await asyncio.Future()
        finally:
            await channel.close()

    async def _process_result(self, message: AbstractIncomingMessage):
        async with message.process():
            try:
                data = json.loads(message.body.decode())
                message_schema = IncomingMessageSchema.model_validate(data)
                async with get_db_context() as session:
                    project_srv = ProjectService(session)
                    file_srv = FileService(project_srv=project_srv)
                    await file_srv.process_schema(message=message_schema)
            except ValidationError as e:
                logger.error(f"Validation error: {e}")
