from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from ..config import config, retry_config
from ..tools import compute_totals

extraction_agent = LlmAgent(
    name="extraction_agent",
    model=Gemini(model=config.worker_model, retry_options=retry_config),
    tools=[compute_totals],
    instruction="""You are a smart data extraction assistant.

1. Parse user input into structured JSON invoice data.
2. Always include the following fields:
   - vendor_info: {name, phone, address, email}
   - customer_info: {name, phone, address, email}
   - invoice_info: {invoice_date, due_date}
   - invoice_number
   - items: [{description, unit_price, quantity, tax}]
3. Then call compute_totals to ensure subtotal, tax, and total are correct.
4. Always return the final JSON inside a single code block.
Dates must be ISO format (yyyy-mm-dd).
"""
)