from typing import TypedDict, Optional, Literal, List
from enum import Enum

class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"

class TravelStyle(str, Enum):
    ADVENTURE = "adventure"
    CALM_PEACEFUL_SIGHTINGS = "calm_peaceful_sightings"
    LOCAL_TRAVELLER = "local_traveller"
    CORPORATE = "corporate"

class UserInputState(TypedDict):
    destination: str
    days: int
    nights: int
    budget_rs: float
    travel_style: Optional[TravelStyle]

class AttractionModel(TypedDict):
    id: str
    name: str
    description: str
    image_query: str
    image_url: Optional[str]
    know_more_fetched: bool
    details: Optional[str]

class DestinationResult(TypedDict):
    status: Literal["success", "error", "idle"]
    validated_destination: Optional[str]
    is_valid: bool
    error_msg: Optional[str]
    attractions: List[AttractionModel]

class ItinerarySlot(TypedDict):
    time: str
    attraction_name: str
    activity_description: str
    duration_hours: float
    tips: Optional[str]

class ItineraryDay(TypedDict):
    day_number: int
    date_label: str
    slots: List[ItinerarySlot]

class ItineraryResult(TypedDict):
    status: Literal["success", "error", "idle"]
    error_msg: Optional[str]
    refresh_count: int
    last_refreshed_at: Optional[str]
    days: List[ItineraryDay]

class BudgetItem(TypedDict):
    category: str
    name: str
    estimated_cost_rs: float
    notes: Optional[str]

class BudgetResult(TypedDict):
    status: Literal["success", "error", "idle"]
    error_msg: Optional[str]
    items: List[BudgetItem]
    travel_cost_rs: float
    accommodation_cost_rs: float
    total_estimated_rs: float
    remaining_budget_rs: float
    is_within_budget: bool

class PackingItem(TypedDict):
    name: str
    quantity: str
    notes: Optional[str]
    essential: bool

class PackingCategoryGroup(TypedDict):
    category_name: str
    items: List[PackingItem]

class PackingResult(TypedDict):
    status: Literal["success", "error", "idle"]
    error_msg: Optional[str]
    weather_summary: Optional[str]
    categories: List[PackingCategoryGroup]

class GroqPromptTask(TypedDict):
    task_id: str
    agent_name: str
    system_prompt: str
    user_prompt: str
    model: str
    max_tokens: int
    temperature: float

class GroqRequestQueue(TypedDict):
    pending_tasks: List[GroqPromptTask]
    in_flight_task_ids: List[str]
    completed_task_ids: List[str]
    batch_window_ms: int
    total_calls_made: int

class AgentStatusMap(TypedDict):
    destination: AgentStatus
    itinerary: AgentStatus
    budget: AgentStatus
    packing: AgentStatus
    coordinator: AgentStatus
