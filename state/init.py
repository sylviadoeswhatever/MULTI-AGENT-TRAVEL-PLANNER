import streamlit as st
from state.schema import AgentStatus

DEFAULT_DESTINATION_RESULT = {
    "status": "idle", "validated_destination": None,
    "is_valid": False, "error_msg": None, "attractions": []
}

DEFAULT_ITINERARY_RESULT = {
    "status": "idle", "error_msg": None,
    "refresh_count": 0, "last_refreshed_at": None, "days": []
}

DEFAULT_BUDGET_RESULT = {
    "status": "idle", "error_msg": None, "items": [],
    "travel_cost_rs": 0.0, "accommodation_cost_rs": 0.0,
    "total_estimated_rs": 0.0, "remaining_budget_rs": 0.0,
    "is_within_budget": True
}

DEFAULT_PACKING_RESULT = {
    "status": "idle", "error_msg": None,
    "weather_summary": None, "categories": []
}

DEFAULT_AGENT_STATUS = {
    "destination": AgentStatus.IDLE,
    "itinerary": AgentStatus.IDLE,
    "budget": AgentStatus.IDLE,
    "packing": AgentStatus.IDLE,
    "coordinator": AgentStatus.IDLE,
}

DEFAULT_GROQ_QUEUE = {
    "pending_tasks": [], "in_flight_task_ids": [],
    "completed_task_ids": [], "batch_window_ms": 500,
    "total_calls_made": 0
}

def init_session_state():
    defaults = {
        "user_input": {
            "destination": "", "days": 0, "nights": 0,
            "budget_rs": 0.0, "travel_style": None
        },
        "destination_result": DEFAULT_DESTINATION_RESULT,
        "itinerary_result": DEFAULT_ITINERARY_RESULT,
        "budget_result": DEFAULT_BUDGET_RESULT,
        "packing_result": DEFAULT_PACKING_RESULT,
        "agent_status": DEFAULT_AGENT_STATUS,
        "groq_request_queue": DEFAULT_GROQ_QUEUE,
        "pipeline_phase": "idle",
        "active_know_more_id": None,
        "form_submitted": False,
        "form_error_msg": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
