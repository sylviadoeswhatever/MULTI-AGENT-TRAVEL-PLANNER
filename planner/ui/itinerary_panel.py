import streamlit as st
import asyncio
from state.schema import AgentStatus
from agents.itinerary_agent import itinerary_agent

def render_itinerary_panel():
    st.header("Itinerary")
    status = st.session_state.agent_status["itinerary"]
    
    if status == AgentStatus.RUNNING:
        st.info("Planning your perfect itinerary...")
        with st.spinner():
            # Check if this is a refresh
            if "refresh_pending_seed" in st.session_state:
                new_seed = st.session_state.refresh_pending_seed
                del st.session_state.refresh_pending_seed
                
                async def refresh():
                    itin_res = await itinerary_agent.run(st.session_state.destination_result, st.session_state.user_input, refresh_seed=new_seed)
                    st.session_state.itinerary_result = itin_res
                    st.session_state.agent_status["itinerary"] = AgentStatus.DONE
                    
                asyncio.run(refresh())
                st.rerun()
        return
        
    res = st.session_state.itinerary_result
    
    if status == AgentStatus.ERROR or res.get("status") == "error":
        st.error(f"Error: {res.get('error_msg', 'Failed to generate itinerary.')}")
        return

    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.write(f"Refreshed: {res.get('refresh_count')} times")
    with col2:
        if st.button("Refresh", help="Wanna shuffle the plan?"):
            st.session_state.agent_status["itinerary"] = AgentStatus.RUNNING
            st.session_state.refresh_pending_seed = res.get("refresh_count", 0) + 1
            st.rerun()

    for day in res.get("days", []):
        with st.expander(f"Day {day['day_number']}", expanded=day['day_number']==1):
            for slot in day.get("slots", []):
                st.markdown(f"**{slot['time']} - {slot['attraction_name']}** ({slot['duration_hours']} hours)")
                st.write(slot.get('activity_desc', slot.get('activity_description', '')))
                st.markdown("---")
                if slot.get("tips"):
                    st.caption(f"Tip: {slot.get('tips')}")
