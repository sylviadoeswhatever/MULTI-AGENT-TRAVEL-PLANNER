import asyncio
import streamlit as st
from agents.destination_agent import destination_agent
from agents.itinerary_agent import itinerary_agent
from agents.budget_agent import budget_agent
from agents.packing_agent import packing_agent
from state.schema import AgentStatus
from utils.logger import logger

class CoordinatorAgent:
    name = "coordinator"

    def set_status(self, status: AgentStatus) -> None:
        st.session_state.agent_status[self.name] = status

    async def run_pipeline(self):
        self.set_status(AgentStatus.RUNNING)
        st.session_state.pipeline_phase = "destination"
        user_input = st.session_state.user_input

        # 1. Run Destination Agent
        dest_res = await destination_agent.run(user_input)
        st.session_state.destination_result = dest_res
        
        if dest_res["status"] != "success":
            self.set_status(AgentStatus.ERROR)
            st.session_state.pipeline_phase = "error"
            return

        # 2. Run Itinerary and Budget in parallel
        st.session_state.pipeline_phase = "parallel"
        itin_task = asyncio.create_task(itinerary_agent.run(dest_res, user_input))
        budg_task = asyncio.create_task(budget_agent.run(dest_res, user_input))

        itin_res, budg_res = await asyncio.gather(itin_task, budg_task)
        
        st.session_state.itinerary_result = itin_res
        st.session_state.budget_result = budg_res

        if itin_res["status"] != "success":
            self.set_status(AgentStatus.ERROR)
            st.session_state.pipeline_phase = "error"
            return

        # 3. Run Packing Agent
        st.session_state.pipeline_phase = "packing"
        pack_res = await packing_agent.run(itin_res, user_input, dest_res)
        st.session_state.packing_result = pack_res

        self.set_status(AgentStatus.DONE)
        st.session_state.pipeline_phase = "complete"

coordinator_agent = CoordinatorAgent()
