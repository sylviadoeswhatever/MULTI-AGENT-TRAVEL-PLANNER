from agents.base_agent import BaseAgent
from state.schema import AgentStatus
from state.init import DEFAULT_ITINERARY_RESULT
from services.groq_client import batcher
from utils.logger import logger
import datetime

class ItineraryAgent(BaseAgent):
    name = "itinerary"

    async def run(self, destination_result: dict, user_input: dict, refresh_seed: int = 0) -> dict:
        self.set_status(AgentStatus.RUNNING)
        logger.info(f"[{self.name}] Generating itinerary. Refresh seed: {refresh_seed}")

        dest = destination_result.get("validated_destination", "")
        attractions = [a["name"] for a in destination_result.get("attractions", [])]
        days = user_input.get("days", 1)
        style = user_input.get("travel_style", "")

        system_prompt = """
        You are an expert travel itinerary planner.
        Create a basic, concise day-by-day travel schedule.
        Keep descriptions extremely short and simple to save tokens.
        JSON format:
        {
          "days": [
            {
              "day_number": 1,
              "date_label": "Day 1",
              "slots": [
                {
                  "time": "09:00 AM",
                  "attraction_name": "...",
                  "activity_desc": "...",
                  "duration_hours": 2.0
                }
              ]
            }
          ]
        }
        """

        user_prompt = f"""
        Destination: {dest}
        Days: {days}
        Travel style: {style or 'general'}
        Available attractions: {', '.join(attractions)}
        Variation seed: {refresh_seed} (make it fresh and different)
        """

        try:
            result = await batcher.submit(system_prompt, user_prompt, max_tokens=600)
            
            days_out = result.get("days", [])
            
            self.set_status(AgentStatus.DONE)
            return {
                "status": "success",
                "error_msg": None,
                "refresh_count": refresh_seed,
                "last_refreshed_at": datetime.datetime.now().isoformat(),
                "days": days_out
            }
        except Exception as e:
            return self.handle_error(e, DEFAULT_ITINERARY_RESULT)

itinerary_agent = ItineraryAgent()
