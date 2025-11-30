import os
from dataclasses import dataclass
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService


os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "False")

@dataclass
class Configuration:
    worker_model: str = "gemini-2.5-flash-lite"
    max_attempts: int = 5

config = Configuration()

retry_config = types.HttpRetryOptions(
    attempts=config.max_attempts,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

memory_service = InMemoryMemoryService()
session_service = InMemorySessionService()
