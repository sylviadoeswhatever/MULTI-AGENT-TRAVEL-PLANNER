from agents.base_agent import BaseAgent
from state.schema import AgentStatus
from state.init import DEFAULT_PACKING_RESULT
from services.groq_client import batcher
from utils.logger import logger

class PackingAgent(BaseAgent):
    name = "packing"

    async def run(self, itinerary_result: dict, user_input: dict, destination_result: dict) -> dict:
        self.set_status(AgentStatus.RUNNING)
        logger.info(f"[{self.name}] Generating weather-aware packing list.")

        dest = destination_result.get("validated_destination", user_input.get("destination", ""))
        days = user_input.get("days", 1)
        style = user_input.get("travel_style", "")

        # Extract activities from itinerary to inform packing
        activities = []
        for day in itinerary_result.get("days", []):
            for slot in day.get("slots", []):
                activities.append(slot.get("attraction_name", ""))

        system_prompt = """
        You are a travel packing advisor and meteorologist.
        First, estimate the typical weather for the destination for the next few days.
        Then generate a packing list tailored to the weather and planned activities.
        JSON format:
        {
          "weather_summary": "Expected: 28-34°C, partly cloudy...",
          "categories": [
            {
              "category_name": "Clothing",
              "items": [
                {
                  "name": "Item name",
                  "quantity": "e.g. 3-4 pieces",
                  "notes": "Optional tip",
                  "essential": true
                }
              ]
            }
          ]
        }
        """

        user_prompt = f"""
        Destination: {dest}
        Duration: {days} days
        Travel style: {style or 'general'}
        Planned activities: {', '.join(activities)}
        """

        try:
            result = await batcher.submit(system_prompt, user_prompt, max_tokens=800)
            
            self.set_status(AgentStatus.DONE)
            return {
                "status": "success",
                "error_msg": None,
                "weather_summary": result.get("weather_summary", "Weather data estimated."),
                "categories": result.get("categories", [])
            }
        except Exception as e:
            return self.handle_error(e, DEFAULT_PACKING_RESULT)

packing_agent = PackingAgent()
