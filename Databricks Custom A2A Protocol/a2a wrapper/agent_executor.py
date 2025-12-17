import logging
import requests

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError,
    InvalidParamsError,
    Part,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError
from config import AGENT_ENDPOINT, SCOPE_NAME, TOKEN
from databricks.sdk import WorkspaceClient

# w = WorkspaceClient()
# dbutils = w.dbutils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class A2AWrapperAgentExecutor(AgentExecutor):
    """Currency Conversion AgentExecutor Example."""

    def __init__(self):
        # self.DATABRICKS_TOKEN = dbutils.secret.get(scope=SCOPE_NAME, key=TOKEN)
        self.AGENT_ENDPOINT = AGENT_ENDPOINT

    # async def model_serving_model(self, user_message: str) -> str:
    #     payload = {"inputs": [{"role": "user", "content": user_message}]}
    #     headers = {
    #         "Authorization": f"Bearer {self.DATABRICKS_TOKEN}",
    #         "Content-Type": "application/json",
    #     }
    #     response = requests.post(
    #         self.AGENT_ENDPOINT, headers=headers, json=payload, timeout=60
    #     )
    #     if response.status_code != 200:
    #         raise Exception(
    #             f"Request failed with status code {response.status_code}: {response.text}"
    #         )
    #     result = response.json()

    #     return next(
    #         item["content"][0]["text"]
    #         for item in result["outputs"]
    #         if item["type"] == "message" and item.get("content")
    #     )

    def model_serving_model(self, user_message: str) -> str:
        return f"The exchange rate for {user_message} YES"
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        error = self._validate_request(context)
        if error:
            raise ServerError(error=InvalidParamsError())

        query = context.get_user_input()
        task = context.current_task
        if not task:
            task = new_task(context.message)  # type: ignore
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        try:
            await updater.update_status(
                TaskState.working,
                new_agent_text_message("Thinking...", task.context_id, task.id),
            )

            model_response = await self.model_serving_model(query)

            await updater.update_status(
                TaskState.working,
                new_agent_text_message(model_response, task.context_id, task.id),
            )

            await updater.add_artifact(
                [Part(root=TextPart(text=model_response))],
                name="agent_response",
            )

            await updater.complete()

        except Exception as e:
            logger.error(f"An error occurred while streaming the response: {e}")
            await updater.upate_status(
                TaskState.failed,
                new_agent_text_message(
                    "An internal error occurred.", task.context_id, task.id
                ),
            )
            raise ServerError(error=InternalError()) from e

    def _validate_request(self, context: RequestContext) -> bool:
        return False

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise ServerError(error=UnsupportedOperationError())
