from agents.base_agent import BaseAgent
from state.schema import AgentStatus
from state.init import DEFAULT_BUDGET_RESULT
from services.groq_client import batcher
from utils.logger import logger

class BudgetAgent(BaseAgent):
    name = "budget"

    async def run(self, destination_result: dict, user_input: dict, itinerary_result: dict = None) -> dict:
        self.set_status(AgentStatus.RUNNING)
        logger.info(f"[{self.name}] Estimating trip budget.")

        dest = destination_result.get("validated_destination", "")
        days = user_input.get("days", 1)
        nights = user_input.get("nights", 0)
        budget_rs = user_input.get("budget_rs", 0.0)
        style = user_input.get("travel_style", "")

        margin = user_input.get("budget_margin", 0.0)
        
        # Extract itinerary activities
        itinerary_activities = []
        if itinerary_result and itinerary_result.get("status") == "success":
            for day in itinerary_result.get("days", []):
                for slot in day.get("slots", []):
                    desc = slot.get('activity_desc', '')
                    desc_str = f" ({desc})" if desc else ""
                    itinerary_activities.append(f"Day {day['day_number']}: {slot['attraction_name']}{desc_str}")
        else:
            itinerary_activities = [a["name"] for a in destination_result.get("attractions", [])]

        system_prompt = """
        You are a travel budget analyst.
        Provide realistic INR cost estimates for each activity, meal, and transport based precisely on the user's itinerary.
        The user has provided a Maximum Budget and an allowed flexibility Margin.
        JSON format:
        {
          "items": [
            {
              "category": "Activities|Meals|Transport|Accommodation|Miscellaneous",
              "name": "Item name",
              "estimated_cost_rs": 500,
              "notes": "Optional note"
            }
          ],
          "travel_cost_rs": 2000,
          "accommodation_cost_rs": 8000
        }
        """

        user_prompt = f"""
        Destination: {dest}
        Duration: {days} days, {nights} nights
        Travel style: {style or 'standard'}
        Planned Itinerary / Attractions:
        {chr(10).join(itinerary_activities)}
        
        Maximum budget: ₹{budget_rs}
        Margin of flexibility: ± ₹{margin}
        
        CRITICAL: Make sure to estimate costs for the specific activities listed in the itinerary!
        """

        try:
            result = await batcher.submit(system_prompt, user_prompt, max_tokens=800)
            
            items = result.get("items", [])
            if not isinstance(items, list):
                items = []
                
            travel_cost = float(result.get("travel_cost_rs", 0.0))
            acc_cost = float(result.get("accommodation_cost_rs", 0.0))
            
            total = sum(float(item.get("estimated_cost_rs", 0)) for item in items) + travel_cost + acc_cost
            remaining = budget_rs - total
            is_within = remaining >= -margin

            self.set_status(AgentStatus.DONE)
            return {
                "status": "success",
                "error_msg": None,
                "items": items,
                "travel_cost_rs": travel_cost,
                "accommodation_cost_rs": acc_cost,
                "total_estimated_rs": total,
                "remaining_budget_rs": remaining,
                "is_within_budget": is_within
            }
        except Exception as e:
            return self.handle_error(e, DEFAULT_BUDGET_RESULT)

budget_agent = BudgetAgent()
