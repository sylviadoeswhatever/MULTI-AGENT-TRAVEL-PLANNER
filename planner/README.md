# Multi-Agent AI Travel Intelligence Platform

![App Preview](https://via.placeholder.com/1000x500.png?text=Preview+Image+Placeholder)

## Overview
* **Architected an asynchronous, multi-agent LLM pipeline** (leveraging Llama-3 via Groq) to autonomously generate validated travel destinations, dynamically-seeded itineraries, itemized financial budgets, and weather-aware logistics.
* **Engineered robust orchestration & API integration**, implementing smart exponential backoff mechanisms to gracefully handle LLM token rate limits alongside real-time data fetching (Wikipedia API) for dynamic image sourcing.
* **Developed a modern, state-driven frontend dashboard** using Streamlit and Python, bypassing native UI constraints with custom CSS injections to deliver a highly responsive, premium user experience with live processing feedback.

## Main Tech Stack
* **Language:** Python
* **Frontend/Framework:** Streamlit (with Custom CSS injections for Vintage Safari Aesthetic)
* **AI & LLM:** Groq API, Meta Llama-3 (8B-Instant)
* **Backend Architecture:** Asynchronous Orchestration (`asyncio`), Multi-Agent Pipeline
* **External APIs:** Wikipedia REST API (for dynamic image fetching)

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ai-travel-planner.git
   cd ai-travel-planner
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables:**
   Rename `.env.example` to `.env` and add your free Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```
   Open your browser and navigate to `http://localhost:8501`.

## Architecture Highlights
- **Rate Limit Handling:** Features dynamic regex-parsing exponential backoff to handle free-tier API rate limits securely.
- **Sequential Context Passing:** Output from the Itinerary agent dynamically feeds the Budget and Packing agents for strict contextual accuracy.
## Features
- **Intelligent Validation:** Prevents hallucinated destinations and fetches real-world images from Wikipedia.
- **Dynamic Itineraries:** Creates sequential, day-by-day schedules with meal breaks.
- **Contextual Budgeting:** Extracts exact activities from your itinerary to generate hyper-realistic cost estimates.
- **Weather-Aware Packing:** Predicts local climate and tailors your packing list to your specific activities.

## Usage
1. Open the application in your browser.
2. Enter your destination (e.g., "Tokyo, Japan").
3. Set your trip duration (Days/Nights) and Maximum Budget.
4. (Optional) Select a Travel Style (e.g., "Adventure", "Relaxing").
5. Click **Plan My Trip**.
6. The AI agents will sequentially process your request. Once complete, navigate through the **DESTINATION**, **ITINERARY**, **FINANCIALS**, and **LOGISTICS** tabs to view your customized plan.

## Future Improvements
- [ ] Integration with live weather APIs (e.g., OpenWeatherMap) for real-time climate data.
- [ ] Export functionality to allow users to download their itinerary as a PDF or sync to Google Calendar.
- [ ] Direct integration with flight/hotel booking APIs (e.g., Amadeus or Skyscanner).
- [ ] User authentication and cloud database to save past trips.
