import urllib.parse
from agents.base_agent import BaseAgent
from state.schema import AgentStatus
from state.init import DEFAULT_DESTINATION_RESULT
from services.groq_client import batcher
from utils.logger import logger

class DestinationAgent(BaseAgent):
    name = "destination"

    async def run(self, user_input: dict) -> dict:
        self.set_status(AgentStatus.RUNNING)
        logger.info(f"[{self.name}] Validating destination and fetching attractions.")

        dest = user_input.get("destination", "")
        days = user_input.get("days", 0)
        nights = user_input.get("nights", 0)
        style = user_input.get("travel_style", "")

        system_prompt = """
        You are a world-class travel expert.
        Validate whether the destination is a real, visitable place. Accept whole countries (like 'Japan' or 'Pakistan') as valid destinations, and if a whole country is given, suggest attractions across major cities in that country.
        If valid, return 5-7 must-visit attractions.
        Respond ONLY in valid JSON.
        Format:
        {
          "is_valid": true,
          "validated_destination": "Canonical Name, Country",
          "reason": null,
          "attractions": [
            {
              "id": "slug-name",
              "name": "Attraction Name",
              "description": "2-3 sentences.",
              "image_query": "keyword for image search"
            }
          ]
        }
        """

        user_prompt = f"""
        Destination: {dest}
        Style: {style or 'not specified'}
        Duration: {days} days, {nights} nights
        """

        try:
            result = await batcher.submit(system_prompt, user_prompt, max_tokens=1000)
            
            if not result.get("is_valid"):
                self.set_status(AgentStatus.DONE)
                return {**DEFAULT_DESTINATION_RESULT, "status": "error", "error_msg": result.get("reason", "Invalid destination.")}

            # Add real images from Wikipedia concurrently
            import urllib.request
            import urllib.parse
            import json
            import asyncio
            
            def fetch_image_url(attr):
                try:
                    query = urllib.parse.quote(attr.get("name", ""))
                    url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={query}&gsrlimit=1&prop=pageimages&format=json&pithumbsize=400"
                    req = urllib.request.Request(url, headers={'User-Agent': 'TravelPlannerBot/1.0 (test@example.com)'})
                    with urllib.request.urlopen(req, timeout=3) as response:
                        data = json.loads(response.read().decode())
                        pages = data.get("query", {}).get("pages", {})
                        if pages:
                            page = next(iter(pages.values()))
                            if "thumbnail" in page:
                                return page["thumbnail"]["source"]
                except Exception as e:
                    logger.warning(f"Failed to fetch image for {attr.get('name')}: {e}")
                return "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/400px-No_image_available.svg.png"

            attractions = result.get("attractions", [])
            image_urls = await asyncio.gather(*[asyncio.to_thread(fetch_image_url, attr) for attr in attractions])
            
            for attr, img_url in zip(attractions, image_urls):
                attr["know_more_fetched"] = False
                attr["details"] = None
                attr["image_url"] = img_url

            self.set_status(AgentStatus.DONE)
            return {
                "status": "success",
                "is_valid": True,
                "validated_destination": result.get("validated_destination"),
                "error_msg": None,
                "attractions": result.get("attractions", [])
            }
        except Exception as e:
            return self.handle_error(e, DEFAULT_DESTINATION_RESULT)

    async def fetch_detail(self, attraction_name: str, validated_destination: str) -> str:
        """Called separately when the user clicks 'Know More'"""
        logger.info(f"[{self.name}] Fetching details for {attraction_name}.")
        system = "You are a travel guide. Provide an engaging 150-word detail about this attraction including history, entry fees, and tips. JSON ONLY: {'details': '...'}"
        user = f"Attraction: {attraction_name} in {validated_destination}"
        try:
            res = await batcher.submit(system, user, max_tokens=500)
            return res.get("details", "Details not available.")
        except Exception as e:
            logger.error(f"Error fetching detail: {e}")
            return "Details temporarily unavailable."

destination_agent = DestinationAgent()
