from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from .config import config, retry_config
from .sub_agents.extraction_agent import extraction_agent
from .sub_agents.invoice_agent import invoice_agent
from .memory_utils import auto_save_to_memory


root_agent = LlmAgent(
    name="invoice_generator_agent",
    model=Gemini(model=config.worker_model, retry_options=retry_config),
    sub_agents=[extraction_agent, invoice_agent],
    instruction="""You are the orchestrator.
1. When a user provides invoice details in natural language, first call extraction_agent.
2. Then call invoice_agent with the JSON string result.
3. Return the final PDF file path to the user as a plain string.""",
    after_agent_callback=auto_save_to_memory
)