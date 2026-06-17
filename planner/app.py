import streamlit as st
import asyncio
from state.init import init_session_state
from ui.input_form import render_input_form
from ui.destination_panel import render_destination_panel
from ui.itinerary_panel import render_itinerary_panel
from ui.budget_panel import render_budget_panel
from ui.packing_panel import render_packing_panel
from state.schema import AgentStatus

# Page config
st.set_page_config(page_title="AI Travel Planner", page_icon="🗺️", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Cyberpunk HUD Aesthetic
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');

/* Hide Streamlit elements */
header {visibility: hidden;}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
div[data-testid="InputInstructions"] {display: none !important;}
h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {display: none !important;}

/* Vintage Safari Styling */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Lora&display=swap');

.stApp {
    font-family: 'Lora', serif;
}
h1, h2, h3, h4 {
    font-family: 'Playfair Display', serif !important;
    color: #A36246 !important;
}
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
    background: none;
}
button[kind="primary"] {
    border-radius: 4px !important;
    border: 1px solid #C4BC92 !important;
    background-color: #99331C !important;
    color: #C4BC92 !important;
    box-shadow: 2px 2px 0px rgba(0, 0, 0, 0.5) !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px;
}
div[data-testid="stExpander"], div[data-testid="stMetricValue"], .stTabs [data-baseweb="tab"] {
    border: 1px solid #787D5C !important;
    border-radius: 4px !important;
    background-color: #3B3625 !important;
    box-shadow: inset 0 0 10px rgba(0,0,0,0.2) !important;
}
img {
    border-radius: 4px !important;
    border: 2px solid #A19A71 !important;
    box-shadow: 4px 4px 0px rgba(0, 0, 0, 0.5);
}
.error-text { 
    color: #99331C; 
    font-family: 'Lora', serif;
    font-weight: bold;
    font-size: 0.9rem; 
    margin-top: 4px; 
}
</style>
""", unsafe_allow_html=True)

# Init state
init_session_state()

st.title("Multi-Agent AI Travel Planner")

# Layout: Form inside an expander so it can collapse after submission
form_expanded = st.session_state.get("pipeline_phase", "idle") == "idle" or st.session_state.destination_result.get("status") == "error"
with st.expander("TRIP CONFIGURATION", expanded=form_expanded):
    render_input_form()

# Render results in Tabs
if st.session_state.destination_result.get("status") != "idle":
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["DESTINATION", "ITINERARY", "FINANCIALS", "LOGISTICS"])
    
    with tab1:
        render_destination_panel()
    with tab2:
        if st.session_state.itinerary_result.get("status") != "idle":
            render_itinerary_panel()
    with tab3:
        if st.session_state.budget_result.get("status") != "idle":
            render_budget_panel()
    with tab4:
        if st.session_state.packing_result.get("status") != "idle":
            render_packing_panel()

# Handle the AI generation pipeline with visible feedback
if st.session_state.get("pipeline_phase") == "start":
    st.session_state.pipeline_phase = "complete"
    
    # Import agents here to avoid circular imports if any
    from agents.destination_agent import destination_agent
    from agents.itinerary_agent import itinerary_agent
    from agents.budget_agent import budget_agent
    from agents.packing_agent import packing_agent
    
    with st.status("Planning your trip...", expanded=True) as status:
        st.write("Validating destination and discovering attractions...")
        dest_res = asyncio.run(destination_agent.run(st.session_state.user_input))
        st.session_state.destination_result = dest_res
        
        if dest_res.get("status") == "success":
            st.write("Generating itinerary...")
            itin_res = asyncio.run(itinerary_agent.run(dest_res, st.session_state.user_input))
            st.session_state.itinerary_result = itin_res
            
            st.write("Estimating costs for your itinerary...")
            budg_res = asyncio.run(budget_agent.run(dest_res, st.session_state.user_input))
            st.session_state.budget_result = budg_res
            
            if itin_res.get("status") == "success":
                st.write("Checking weather and preparing packing list...")
                pack_res = asyncio.run(packing_agent.run(itin_res, st.session_state.user_input, dest_res))
                st.session_state.packing_result = pack_res
                
            status.update(label="Trip Planned Successfully!", state="complete", expanded=False)
        else:
            status.update(label="Invalid Destination", state="error", expanded=True)
    
    st.rerun()
