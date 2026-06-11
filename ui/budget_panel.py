import streamlit as st
from state.schema import AgentStatus

def render_budget_panel():
    st.header("Budget")
    status = st.session_state.agent_status["budget"]
    
    if status == AgentStatus.RUNNING:
        st.info("Calculating your trip costs...")
        st.spinner()
        return
        
    res = st.session_state.budget_result
    
    if status == AgentStatus.ERROR or res.get("status") == "error":
        st.error(f"Error: {res.get('error_msg', 'Failed to calculate budget.')}")
        return

    st.subheader("Your Budget Summary")
    budget_rs = st.session_state.user_input.get('budget_rs', 0)
    est = res.get('total_estimated_rs', 0)
    rem = res.get('remaining_budget_rs', 0)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Maximum Budget", f"₹{budget_rs:,.2f}")
    col2.metric("Estimated Total", f"₹{est:,.2f}", delta="Within Budget" if res.get('is_within_budget') else "Over Budget", delta_color="normal" if res.get('is_within_budget') else "inverse")
    col3.metric("Remaining Funds", f"₹{rem:,.2f}")
    
    st.markdown("---")
    st.subheader("Financial Breakdown")
    
    b_col1, b_col2 = st.columns(2)
    b_col1.metric("Travel & Transport", f"₹{res.get('travel_cost_rs', 0):,.2f}")
    b_col2.metric("Accommodation", f"₹{res.get('accommodation_cost_rs', 0):,.2f}")
    
    st.markdown("#### Itemized Expenses")
    for item in res.get("items", []):
        st.write(f"**{item.get('name')}** ({item.get('category')}): ₹{item.get('estimated_cost_rs', 0):,.2f}")
        if item.get("notes"):
            st.caption(item.get("notes"))
