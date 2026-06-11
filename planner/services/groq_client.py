import os
import asyncio
from groq import AsyncGroq
from dotenv import load_dotenv
from typing import Dict, Any, List
from utils.logger import logger
from utils.json_parser import safe_parse_json

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.error("GROQ_API_KEY not found in environment variables.")

# Initialize async client
client = AsyncGroq(api_key=GROQ_API_KEY)

class GroqBatcher:
    """
    Executes Groq requests. Since we use asyncio.gather in the Coordinator,
    parallel requests natively run concurrently without needing a complex queue
    that breaks Streamlit's event loops.
    """
    async def submit(self, system_prompt: str, user_prompt: str, max_tokens: int = 1500, temperature: float = 0.7) -> Dict[str, Any]:
        max_retries = 3
        backoff = 1.0
        
        for attempt in range(max_retries):
            try:
                response = await client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    response_format={"type": "json_object"}
                )
                
                raw_content = response.choices[0].message.content
                
                parsed = safe_parse_json(raw_content)
                
                if parsed is None:
                    raise ValueError("Failed to parse Groq output as JSON.")
                    
                return parsed
                
            except Exception as e:
                err_str = str(e)
                logger.warning(f"Groq API error on attempt {attempt + 1}: {err_str}")
                
                if attempt == max_retries - 1:
                    raise e
                    
                # Handle Groq 429 Rate Limits dynamically
                if "429" in err_str and "Please try again in" in err_str:
                    import re
                    match = re.search(r"Please try again in ([0-9.]+)s", err_str)
                    if match:
                        sleep_time = float(match.group(1)) + 1.0
                        logger.info(f"Rate limited. Sleeping for {sleep_time} seconds before retrying...")
                        await asyncio.sleep(sleep_time)
                        continue
                        
                await asyncio.sleep(backoff)
                backoff *= 2.0

# Singleton instance
batcher = GroqBatcher()
