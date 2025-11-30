from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from ..config import config, retry_config
from ..tools import generate_invoice_pdf

invoice_agent = LlmAgent(
    name="invoice_agent",
    model=Gemini(model=config.worker_model, retry_options=retry_config),
    tools=[generate_invoice_pdf],
    instruction="""You are an invoice generator assistant.
Given structured invoice data as a JSON string, call generate_invoice_pdf
and return the file path as a plain string."""
)
