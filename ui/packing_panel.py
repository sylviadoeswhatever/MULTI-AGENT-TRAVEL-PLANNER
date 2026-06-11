import streamlit as st
from state.schema import AgentStatus

def render_packing_panel():
    st.header("Packing List")
    status = st.session_state.agent_status["packing"]
    
    if status == AgentStatus.RUNNING:
        st.info("Checking weather & building your packing list...")
        st.spinner()
        return
        
    res = st.session_state.packing_result
    
    if status == AgentStatus.ERROR or res.get("status") == "error":
        st.error(f"Error: {res.get('error_msg', 'Failed to generate packing list.')}")
        return

    st.info(f"{res.get('weather_summary')}")
    
    cats = res.get("categories", [])
    cols = st.columns(3)
    for i, cat in enumerate(cats):
        with cols[i % 3]:
            st.subheader(cat.get("category_name"))
            for item in cat.get("items", []):
                icon = "*" if item.get("essential") else "-"
                notes = f" - {item.get('notes')}" if item.get("notes") else ""
                st.write(f"{icon} {item.get('name')} ({item.get('quantity')}){notes}")
