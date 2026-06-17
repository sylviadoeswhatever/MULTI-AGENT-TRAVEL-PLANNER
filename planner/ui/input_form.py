import streamlit as st
import asyncio
from state.validation import validate_user_input
from state.schema import TravelStyle
from agents.coordinator_agent import coordinator_agent
from state.init import DEFAULT_AGENT_STATUS

def render_input_form():
    # Initialize form errors in session state if they don't exist
    if "form_errors" not in st.session_state:
        st.session_state.form_errors = {}
        
    errors = st.session_state.form_errors

    with st.form("travel_form"):
        dest = st.text_input("Destination City/Country :red[*]")
        if "destination" in errors:
            st.markdown(f'<p class="error-text">{errors["destination"]}</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            days = st.number_input("Duration (Days) :red[*]", min_value=1, value=None, placeholder="e.g. 5")
            if "days" in errors:
                st.markdown(f'<p class="error-text">{errors["days"]}</p>', unsafe_allow_html=True)
        with col2:
            nights = st.number_input("Duration (Nights) :red[*]", min_value=0, value=None, placeholder="e.g. 4")
            if "nights" in errors:
                st.markdown(f'<p class="error-text">{errors["nights"]}</p>', unsafe_allow_html=True)
            
        budget = st.number_input("Maximum Budget (₹ INR) :red[*]", min_value=1.0, value=None, step=1000.0, placeholder="e.g. 50000")
        if "budget_rs" in errors:
            st.markdown(f'<p class="error-text">{errors["budget_rs"]}</p>', unsafe_allow_html=True)
            
        margin = st.slider("Margin of flexibility (± ₹)", min_value=1, max_value=100000, value=5000, step=1000)
        st.caption("Note: Any changes in budgets would be applied in case of inadequate funds.")
        
        style = st.selectbox(
            "Travel Style (Optional)", 
            ["", TravelStyle.ADVENTURE.value, TravelStyle.CALM_PEACEFUL_SIGHTINGS.value, TravelStyle.LOCAL_TRAVELLER.value, TravelStyle.CORPORATE.value],
            format_func=lambda x: "Select..." if x == "" else x.replace('_', ' ').title()
        )
        
        submit = st.form_submit_button("Plan My Trip")

    if submit:
        inputs = {
            "destination": dest,
            "days": int(days) if days is not None else 0,
            "nights": int(nights) if nights is not None else -1,
            "budget_rs": float(budget) if budget is not None else 0.0,
            "budget_margin": float(margin) if margin is not None else 0.0,
            "travel_style": style if style else None
        }
        
        is_valid, err_dict = validate_user_input(inputs)
        if not is_valid:
            st.session_state.form_errors = err_dict
            st.markdown("""
                <script>
                    const main = window.parent.document.querySelector('.main');
                    if(main) {
                        main.classList.add('shake-error');
                        setTimeout(() => main.classList.remove('shake-error'), 500);
                    }
                </script>
            """, unsafe_allow_html=True)
            st.rerun()
        else:
            st.session_state.form_errors = {}
            st.session_state.user_input = inputs
            # Reset states
            st.session_state.agent_status = DEFAULT_AGENT_STATUS.copy()
            st.session_state.pipeline_phase = "start"
            st.rerun()
