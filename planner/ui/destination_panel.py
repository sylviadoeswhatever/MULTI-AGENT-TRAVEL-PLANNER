import streamlit as st
import asyncio
from state.schema import AgentStatus
from agents.destination_agent import destination_agent

def render_destination_panel():
    st.header("Destination")
    status = st.session_state.agent_status["destination"]
    
    if status == AgentStatus.RUNNING:
        st.info("Validating destination & discovering attractions...")
        st.spinner()
        return
        
    res = st.session_state.destination_result
    
    if status == AgentStatus.ERROR or res.get("status") == "error":
        st.error(f"Error: {res.get('error_msg', 'Failed to validate destination.')}")
        return
        
    cols = st.columns(4)
    for i, attr in enumerate(res.get("attractions", [])):
        with cols[i % 4]:
            st.subheader(attr["name"])
            st.markdown(f'<img src="{attr["image_url"]}" style="width: 100%; border-radius: 4px;" alt="{attr["name"]}">', unsafe_allow_html=True)
            st.write(attr["description"])
            
            # Know More Expander
            with st.expander("Know More"):
                if attr.get("details"):
                    st.write(attr["details"])
                else:
                    if st.button(f"Fetch Details for {attr['name']}", key=f"fetch_{attr['id']}"):
                        with st.spinner("Fetching details..."):
                            details = asyncio.run(destination_agent.fetch_detail(attr["name"], res.get("validated_destination")))
                            attr["details"] = details
                            attr["know_more_fetched"] = True
                            st.write(details)
                            st.rerun()
