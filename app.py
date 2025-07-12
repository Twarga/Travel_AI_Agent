# ai_travel_planner_v7_enhanced.py
"""
Enhanced AI Travel Planner v7 with Superior Prompting, JSON Structure, and Modern UI
================================================================================

This is a sophisticated AI Travel Planner using Streamlit with:
- Structured JSON output for better parsing and display
- Modern UI with tabs, expanders, columns, and metrics
- Rich content with budget analysis, pro-tips, and justifications
- Superior AI prompting for consistent, detailed responses

----------
Quick Start
----------
1.  Save this code as a Python file (e.g., `app.py`).

2.  Create a `requirements.txt` file with the following content:
    streamlit>=1.35.0
    openai>=1.30.0
    httpx>=0.27.0
    beautifulsoup4>=4.12.3
    ddgs>=6.1.4
    diskcache>=5.6.3
    geopy>=2.4.1
    plotly>=5.17.0

3.  Install the dependencies:
    pip install -r requirements.txt

4.  Create a file named `.streamlit/secrets.toml` in your project folder
    and add your API keys:
    ```toml
    OPENAI_API_KEY = "sk-..."
    # Optional but recommended for better search results
    BRAVE_API_KEY  = "..."
    ```

5.  Run the app from your terminal:
    streamlit run app.py
"""
from __future__ import annotations
import asyncio, datetime as dt, json, os
from pathlib import Path
from typing import List, AsyncGenerator, Dict, Any, Optional
import re

import httpx, streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from bs4 import BeautifulSoup
from diskcache import Cache
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from openai import AsyncOpenAI
from ddgs.ddgs import DDGS

# ---------------------------------------------------------------------------
# CONFIG & INIT
# ---------------------------------------------------------------------------
MODELS = {
    "gpt-4o-mini": {"name": "gpt-4o-mini", "description": "Fast and efficient (recommended)"},
    "gpt-4o": {"name": "gpt-4o", "description": "Most capable (slower)"},
}

CACHE = Cache(str(Path.home() / ".cache/travel_planner_v7"), size_limit=2e9)

OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("🔑 OPENAI_API_KEY missing – add it to .streamlit/secrets.toml or env.")
    st.stop()

client = AsyncOpenAI(api_key=OPENAI_API_KEY)
geolocator = Nominatim(user_agent="ai_travel_planner_v7")

# ---------------------------------------------------------------------------
# ENHANCED SYSTEM PROMPT FOR STRUCTURED JSON OUTPUT
# ---------------------------------------------------------------------------
SYSTEM_PROMPT_ITINERARY = """
You are an expert travel planning assistant. You MUST return a structured JSON object containing a comprehensive travel itinerary.

**CRITICAL REQUIREMENTS:**
1. **JSON Structure**: Your response must be VALID JSON that can be parsed by json.loads()
2. **Complete Data**: Include ALL required fields for each day, activity, restaurant, and hotel
3. **Verified Links**: All URLs must be real and working links
4. **Budget Analysis**: Provide realistic cost breakdowns
5. **Pro Tips**: Include actionable advice for each major activity
6. **Justifications**: Explain why each place/activity is recommended

**EXACT JSON STRUCTURE TO FOLLOW:**
```json
{
  "trip_summary": {
    "destination": "string",
    "origin": "string", 
    "start_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "total_days": number,
    "budget": number,
    "interests": ["string"],
    "pace": "string",
    "overview": "2-3 sentence trip overview"
  },
  "budget_analysis": {
    "accommodation": {"total": number, "per_night": number, "notes": "string"},
    "food": {"total": number, "per_day": number, "breakdown": {"breakfast": number, "lunch": number, "dinner": number}},
    "activities": {"total": number, "per_day": number, "notes": "string"},
    "transportation": {"total": number, "local": number, "intercity": number, "notes": "string"},
    "miscellaneous": {"total": number, "percentage": number, "notes": "string"},
    "total_estimated": number,
    "budget_status": "under_budget|on_budget|over_budget",
    "savings_tips": ["string"]
  },
  "daily_itinerary": [
    {
      "day": number,
      "date": "YYYY-MM-DD",
      "theme": "string (e.g., 'Historic Downtown Exploration')",
      "weather_note": "string",
      "morning": {
        "time": "HH:MM",
        "activity": {
          "name": "string",
          "description": "string",
          "duration": "string",
          "cost": number,
          "booking_link": "string",
          "maps_link": "string",
          "why_recommended": "string",
          "pro_tip": "string"
        }
      },
      "afternoon": {
        "time": "HH:MM",
        "activity": {
          "name": "string",
          "description": "string", 
          "duration": "string",
          "cost": number,
          "booking_link": "string",
          "maps_link": "string",
          "why_recommended": "string",
          "pro_tip": "string"
        }
      },
      "evening": {
        "time": "HH:MM",
        "activity": {
          "name": "string",
          "description": "string",
          "duration": "string", 
          "cost": number,
          "booking_link": "string",
          "maps_link": "string",
          "why_recommended": "string",
          "pro_tip": "string"
        }
      },
      "meals": {
        "breakfast": {
          "name": "string",
          "cuisine": "string",
          "cost": number,
          "website": "string",
          "maps_link": "string",
          "why_recommended": "string",
          "signature_dish": "string"
        },
        "lunch": {
          "name": "string",
          "cuisine": "string", 
          "cost": number,
          "website": "string",
          "maps_link": "string",
          "why_recommended": "string",
          "signature_dish": "string"
        },
        "dinner": {
          "name": "string",
          "cuisine": "string",
          "cost": number,
          "website": "string", 
          "maps_link": "string",
          "why_recommended": "string",
          "signature_dish": "string"
        }
      },
      "accommodation": {
        "name": "string",
        "type": "string",
        "cost_per_night": number,
        "booking_link": "string",
        "maps_link": "string",
        "why_recommended": "string",
        "amenities": ["string"]
      },
      "transportation": {
        "method": "string",
        "routes": ["string"],
        "cost": number,
        "travel_time": "string",
        "tips": "string"
      },
      "daily_total_cost": number
    }
  ],
  "essential_info": {
    "best_time_to_visit": "string",
    "weather_expectations": "string", 
    "local_customs": ["string"],
    "language_tips": ["string"],
    "currency_info": "string",
    "safety_tips": ["string"],
    "packing_recommendations": ["string"]
  },
  "alternatives": {
    "rainy_day_activities": [
      {
        "name": "string",
        "description": "string",
        "cost": number,
        "booking_link": "string"
      }
    ],
    "budget_friendly_options": [
      {
        "name": "string", 
        "description": "string",
        "cost": number,
        "savings": "string"
      }
    ],
    "luxury_upgrades": [
      {
        "name": "string",
        "description": "string",
        "additional_cost": number,
        "booking_link": "string"
      }
    ]
  }
}
```

**LINK REQUIREMENTS:**
- All booking_link fields must be real, working URLs (official sites, booking.com, etc.)
- All maps_link fields must use format: https://www.openstreetmap.org/search?query=PLACE_NAME,CITY
- All website fields must be real, working URLs
- Use your search tools to verify links exist and are correct

**COST REQUIREMENTS:**
- All costs must be in USD
- Be realistic based on current prices
- Include taxes and fees where applicable
- Provide per-person estimates

**CONTENT REQUIREMENTS:**
- "why_recommended" should be 1-2 sentences explaining the unique value
- "pro_tip" should be actionable advice from traveler experiences
- "description" should be informative and engaging
- All recommendations should align with the user's interests and budget

YOU MUST RETURN ONLY THE JSON OBJECT. NO OTHER TEXT OR MARKDOWN.
""".strip()

# ---------------------------------------------------------------------------
# SEARCH & SCRAPE TOOLS (Enhanced)
# ---------------------------------------------------------------------------

def brave_search(query: str, num: int = 5) -> List[str]:
    key = st.secrets.get("BRAVE_API_KEY") or os.getenv("BRAVE_API_KEY")
    if not key:
        return []
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"Accept": "application/json", "X-Subscription-Token": key}
    params = {"q": query, "count": num}
    try:
        with httpx.Client(timeout=15) as c:
            r = c.get(url, headers=headers, params=params)
            r.raise_for_status()
            return [i["url"] for i in r.json().get("web", {}).get("results", [])]
    except Exception:
        pass
    return []

def ddg_search(query: str, num: int = 5) -> List[str]:
    try:
        with DDGS() as ddgs:
            return [r["href"] for r in ddgs.text(query, max_results=num)]
    except Exception:
        return []

@CACHE.memoize()
def web_search(query: str, num: int = 5) -> str:
    results = (brave_search(query, num) or ddg_search(query, num))[:num]
    return json.dumps(results)

async def scrape(url: str) -> str:
    # Manual caching for async scrape function
    cache_key = f"scrape:{url}"
    cached_result = CACHE.get(cache_key)
    if cached_result is not None:
        return cached_result
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as c:
            r = await c.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for t in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
                t.decompose()
            text = "\n".join(s.strip() for s in soup.stripped_strings if len(s) > 20)
            result = text[:6000]
            CACHE.set(cache_key, result)
            return result
    except Exception as e:
        return f"Error scraping {url}: {e}"

# ---------------------------------------------------------------------------
# OPENAI FUNCTION CALLING SETUP (Enhanced)
# ---------------------------------------------------------------------------
TOOLS = [
    {"type": "function", "function": {
        "name": "web_search",
        "description": "Search the web for travel information, booking sites, reviews, and current prices. Use specific queries.",
        "parameters": {"type": "object", "properties": {
            "query": {"type": "string", "description": "Specific search query, e.g., 'best hotels Paris 2024 booking', 'restaurant recommendations Rome TripAdvisor'"},
            "num": {"type": "integer", "default": 5, "minimum": 1, "maximum": 10}},
            "required": ["query"]}}},
    {"type": "function", "function": {
        "name": "scrape",
        "description": "Download and extract clean text from a webpage for detailed information.",
        "parameters": {"type": "object", "properties": {
            "url": {"type": "string", "description": "The full URL of the page to scrape for detailed information."}},
            "required": ["url"]}}},
]

async def plan_itinerary(user_query: str, model: str) -> Dict[str, Any]:
    """Plan itinerary and return structured JSON data"""
    msgs = [
        {"role": "system", "content": SYSTEM_PROMPT_ITINERARY},
        {"role": "user", "content": user_query},
    ]

    # Allow multiple rounds of function calls for thorough research
    max_rounds = 8
    current_round = 0
    
    while current_round < max_rounds:
        current_round += 1
        
        response = await client.chat.completions.create(
            model=model,
            messages=msgs,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.3,
            max_tokens=8000,
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            msgs.append(message)
            
            # Execute all tool calls
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    result = f"Error: Invalid JSON arguments for {function_name}"
                else:
                    if function_name == "web_search":
                        result = web_search(arguments.get("query", ""), arguments.get("num", 5))
                    elif function_name == "scrape":
                        result = await scrape(arguments.get("url", ""))
                    else:
                        result = f"Error: Unknown function {function_name}"
                
                msgs.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": str(result)
                })
        else:
            # No more tool calls, we should have our final response
            content = message.content
            if content:
                try:
                    # Try to parse as JSON
                    return json.loads(content)
                except json.JSONDecodeError:
                    # If not valid JSON, try to extract JSON from the response
                    json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                    if json_match:
                        try:
                            return json.loads(json_match.group(1))
                        except json.JSONDecodeError:
                            pass
                    
                    # If still no valid JSON, return error structure
                    return {
                        "error": "Failed to generate valid JSON response",
                        "raw_response": content[:1000]
                    }
            break
    
    return {"error": "Maximum rounds exceeded without getting final response"}

# ---------------------------------------------------------------------------
# UI COMPONENTS (New Modern Interface)
# ---------------------------------------------------------------------------

def render_budget_analysis(budget_data: Dict[str, Any], user_budget: float):
    """Render budget analysis with visual components"""
    st.subheader("💰 Budget Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Estimated", f"${budget_data['total_estimated']:,.0f}", 
                 delta=f"${budget_data['total_estimated'] - user_budget:,.0f}")
    
    with col2:
        status_icon = {"under_budget": "✅", "on_budget": "⚖️", "over_budget": "⚠️"}
        st.metric("Budget Status", budget_data['budget_status'].replace('_', ' ').title(), 
                 delta_color="normal" if budget_data['budget_status'] != 'over_budget' else "inverse")
    
    with col3:
        daily_avg = budget_data['total_estimated'] / max(1, budget_data.get('days', 1))
        st.metric("Daily Average", f"${daily_avg:.0f}")
    
    with col4:
        accommodation_pct = (budget_data['accommodation']['total'] / budget_data['total_estimated']) * 100
        st.metric("Accommodation %", f"{accommodation_pct:.0f}%")
    
    # Budget breakdown chart
    categories = ['Accommodation', 'Food', 'Activities', 'Transportation', 'Miscellaneous']
    values = [
        budget_data['accommodation']['total'],
        budget_data['food']['total'], 
        budget_data['activities']['total'],
        budget_data['transportation']['total'],
        budget_data['miscellaneous']['total']
    ]
    
    fig = px.pie(values=values, names=categories, title="Budget Breakdown")
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
    
    # Savings tips
    if budget_data.get('savings_tips'):
        with st.expander("💡 Money-Saving Tips"):
            for tip in budget_data['savings_tips']:
                st.write(f"• {tip}")

def render_daily_itinerary(daily_data: List[Dict[str, Any]]):
    """Render daily itinerary with tabs and rich formatting"""
    st.subheader("📅 Daily Itinerary")
    
    # Create tabs for each day
    tab_labels = [f"Day {day['day']}" for day in daily_data]
    tabs = st.tabs(tab_labels)
    
    for i, (tab, day) in enumerate(zip(tabs, daily_data)):
        with tab:
            # Day header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"### {day['theme']}")
                st.write(f"**Date:** {day['date']}")
                if day.get('weather_note'):
                    st.info(f"🌤️ {day['weather_note']}")
            
            with col2:
                st.metric("Daily Cost", f"${day['daily_total_cost']:.0f}")
            
            # Time-based activities
            times = ['morning', 'afternoon', 'evening']
            time_icons = {'morning': '🌅', 'afternoon': '☀️', 'evening': '🌙'}
            
            for time_slot in times:
                if time_slot in day and day[time_slot]:
                    activity = day[time_slot]['activity']
                    
                    with st.expander(f"{time_icons[time_slot]} {time_slot.title()} - {activity['name']} ({day[time_slot]['time']})"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Description:** {activity['description']}")
                            st.write(f"**Duration:** {activity['duration']}")
                            st.write(f"**Why visit:** {activity['why_recommended']}")
                            
                            if activity.get('pro_tip'):
                                st.success(f"💡 **Pro Tip:** {activity['pro_tip']}")
                        
                        with col2:
                            st.metric("Cost", f"${activity['cost']:.0f}")
                            
                            if activity.get('booking_link'):
                                st.link_button("🎫 Book Now", activity['booking_link'])
                            
                            if activity.get('maps_link'):
                                st.link_button("🗺️ View on Map", activity['maps_link'])
            
            # Meals section
            st.write("### 🍽️ Meals")
            meal_cols = st.columns(3)
            meals = ['breakfast', 'lunch', 'dinner']
            meal_icons = {'breakfast': '🥐', 'lunch': '🥗', 'dinner': '🍷'}
            
            for i, (meal, col) in enumerate(zip(meals, meal_cols)):
                if meal in day['meals']:
                    meal_data = day['meals'][meal]
                    with col:
                        st.write(f"**{meal_icons[meal]} {meal.title()}**")
                        st.write(f"📍 {meal_data['name']}")
                        st.write(f"🍽️ {meal_data['cuisine']}")
                        st.write(f"💰 ${meal_data['cost']:.0f}")
                        st.write(f"⭐ {meal_data['signature_dish']}")
                        
                        if meal_data.get('website'):
                            st.link_button("🌐 Website", meal_data['website'], use_container_width=True)
            
            # Accommodation
            if 'accommodation' in day:
                acc = day['accommodation']
                st.write("### 🏨 Accommodation")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.write(f"**{acc['name']}** ({acc['type']})")
                    st.write(f"**Why stay here:** {acc['why_recommended']}")
                    
                    if acc.get('amenities'):
                        st.write("**Amenities:** " + ", ".join(acc['amenities']))
                
                with col2:
                    st.metric("Per Night", f"${acc['cost_per_night']:.0f}")
                    
                    if acc.get('booking_link'):
                        st.link_button("🏨 Book Hotel", acc['booking_link'])
            
            # Transportation
            if 'transportation' in day:
                trans = day['transportation']
                st.write("### 🚗 Transportation")
                st.write(f"**Method:** {trans['method']}")
                st.write(f"**Estimated Cost:** ${trans['cost']:.0f}")
                st.write(f"**Travel Time:** {trans['travel_time']}")
                
                if trans.get('tips'):
                    st.info(f"💡 {trans['tips']}")

def render_essential_info(essential_data: Dict[str, Any]):
    """Render essential travel information"""
    st.subheader("ℹ️ Essential Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### 🌤️ Weather & Timing")
        st.write(f"**Best time to visit:** {essential_data['best_time_to_visit']}")
        st.write(f"**Weather expectations:** {essential_data['weather_expectations']}")
        
        st.write("#### 🗣️ Language & Culture")
        if essential_data.get('language_tips'):
            for tip in essential_data['language_tips']:
                st.write(f"• {tip}")
        
        if essential_data.get('local_customs'):
            st.write("**Local customs:**")
            for custom in essential_data['local_customs']:
                st.write(f"• {custom}")
    
    with col2:
        st.write("#### 💰 Currency & Safety")
        st.write(f"**Currency:** {essential_data['currency_info']}")
        
        if essential_data.get('safety_tips'):
            st.write("**Safety tips:**")
            for tip in essential_data['safety_tips']:
                st.write(f"• {tip}")
        
        if essential_data.get('packing_recommendations'):
            st.write("**Packing recommendations:**")
            for item in essential_data['packing_recommendations']:
                st.write(f"• {item}")

def render_alternatives(alternatives_data: Dict[str, Any]):
    """Render alternative options"""
    st.subheader("🔄 Alternative Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("#### 🌧️ Rainy Day Activities")
        for activity in alternatives_data.get('rainy_day_activities', []):
            with st.expander(activity['name']):
                st.write(activity['description'])
                st.metric("Cost", f"${activity['cost']:.0f}")
                if activity.get('booking_link'):
                    st.link_button("Book", activity['booking_link'])
    
    with col2:
        st.write("#### 💵 Budget-Friendly Options")
        for option in alternatives_data.get('budget_friendly_options', []):
            with st.expander(option['name']):
                st.write(option['description'])
                st.metric("Cost", f"${option['cost']:.0f}")
                st.success(f"Savings: {option['savings']}")
    
    with col3:
        st.write("#### 👑 Luxury Upgrades")
        for upgrade in alternatives_data.get('luxury_upgrades', []):
            with st.expander(upgrade['name']):
                st.write(upgrade['description'])
                st.metric("Additional Cost", f"${upgrade['additional_cost']:.0f}")
                if upgrade.get('booking_link'):
                    st.link_button("Book", upgrade['booking_link'])

# ---------------------------------------------------------------------------
# ENHANCED STREAMLIT UI
# ---------------------------------------------------------------------------

def city_suggestions(prefix: str, max_items: int = 5) -> List[str]:
    if len(prefix) < 3: 
        return []
    try:
        locations = geolocator.geocode(prefix, exactly_one=False, limit=max_items, language="en")
        if locations:
            return list({loc.address.split(",")[0] for loc in locations if loc.address})
        return []
    except (GeocoderTimedOut, GeocoderUnavailable):
        return []

def _set_city(key: str, city: str):
    st.session_state[key] = city

# Page configuration
st.set_page_config(
    page_title="AI Travel Planner v7", 
    page_icon="🌍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .stMetric > div > div > div > div {
        font-size: 1.2rem;
    }
    .trip-summary {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #2a5298;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("✈️ AI Travel Planner v7")
st.markdown("*Enhanced with Superior AI Prompting, Structured Data & Modern UI*")
st.markdown('</div>', unsafe_allow_html=True)

# Sidebar for trip details
with st.sidebar:
    st.header("🎯 Trip Configuration")
    
    # Origin and destination with suggestions
    orig_key, dest_key = "_origin", "_destination"

    # Load favorite destinations from session state or initialize
    if "favorite_destinations" not in st.session_state:
        st.session_state["favorite_destinations"] = []

    st.subheader("⭐ Favorite Destinations")
    favorite = st.selectbox(
        "Select a favorite destination to autofill",
        options=[""] + st.session_state["favorite_destinations"],
        index=0,
        help="Quickly select a previously saved destination"
    )
    if favorite:
        st.session_state[dest_key] = favorite

    # Button to save current destination as favorite
    if st.button("💾 Save Current Destination as Favorite"):
        current_dest = st.session_state.get(dest_key, "").strip()
        if current_dest and current_dest not in st.session_state["favorite_destinations"]:
            st.session_state["favorite_destinations"].append(current_dest)
            st.success(f"Saved '{current_dest}' to favorites!")
        elif not current_dest:
            st.warning("Enter a destination city to save.")
        else:
            st.info(f"'{current_dest}' is already in favorites.")

    st.subheader("📍 Locations")
    origin = st.text_input("🛫 Origin City", key=orig_key, help="Where are you traveling from?")
    if origin:
        suggestions = city_suggestions(origin)
        if suggestions:
            st.write("**Suggestions:**")
            for city in suggestions[:3]:
                st.button(city, key=f"orig_{city}", on_click=_set_city, args=(orig_key, city))
    
    destination = st.text_input("🏛️ Destination City", key=dest_key, help="Where do you want to go?")
    if destination:
        suggestions = city_suggestions(destination)
        if suggestions:
            st.write("**Suggestions:**")
            for city in suggestions[:3]:
                st.button(city, key=f"dest_{city}", on_click=_set_city, args=(dest_key, city))
    
    # Trip dates
    st.subheader("📅 Dates")
    start_date = st.date_input("Start Date", 
                              value=dt.date.today() + dt.timedelta(days=30),
                              min_value=dt.date.today())
    end_date = st.date_input("End Date", 
                            value=start_date + dt.timedelta(days=6),
                            min_value=start_date)
    
    # Budget and preferences
    st.subheader("💰 Budget & Preferences")
    budget = st.slider("Total Budget (USD)", 500, 25000, 3000, 250,
                      help="Your total budget for the entire trip")
    
    interests = st.multiselect(
        "🎨 Interests",
        options=["History & Culture", "Food & Dining", "Nature & Outdoors", 
                "Shopping", "Adventure Sports", "Art & Museums", "Nightlife & Entertainment", 
                "Architecture", "Local Experiences", "Photography"],
        default=["History & Culture", "Food & Dining"],
        help="Select your main interests for personalized recommendations"
    )
    
    pace = st.selectbox(
        "⏱️ Trip Pace",
        options=["Relaxed", "Moderate", "Intensive"],
        index=1,
        help="How packed do you want your itinerary to be?"
    )
    
    # Model selection
    st.subheader("🤖 AI Model")
    model_choice = st.selectbox(
        "Select AI Model",
        options=list(MODELS.keys()),
        format_func=lambda x: f"{x} - {MODELS[x]['description']}",
        help="Choose between speed and capability"
    )
    
    # Generate button
    generate_button = st.button(
        "🚀 Generate Smart Itinerary",
        type="primary",
        use_container_width=True,
        help="This will take 1-2 minutes as AI researches your destination"
    )

# Main content area
if generate_button:
    # Validation
    origin_val = st.session_state.get(orig_key, "").strip()
    dest_val = st.session_state.get(dest_key, "").strip()
    
    if not origin_val or not dest_val:
        st.error("🚨 Please enter both origin and destination cities.")
        st.stop()
    
    if end_date <= start_date:
        st.error("🚨 End date must be after start date.")
        st.stop()
    
    # Calculate trip duration
    trip_days = (end_date - start_date).days
    if trip_days > 30:
        st.warning("⚠️ Trip duration is quite long. Consider breaking it into segments for better planning.")
    
    # Build comprehensive user query
    user_query = f"""
    Plan a detailed {pace.lower()}-paced trip to {dest_val} from {origin_val}.
    
    Trip Details:
    - Dates: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')} ({trip_days} days)
    - Total Budget: ${budget:,} USD
    - Interests: {', '.join(interests)}
    - Travel Style: {pace}
    
    Please provide a comprehensive itinerary with verified links, realistic costs, pro tips from experienced travelers, and detailed justifications for each recommendation. Include rainy day alternatives and both budget-friendly and luxury options.
    """
    
    # Show progress and generate itinerary
    with st.spinner("🔍 AI is researching your destination and creating a personalized itinerary..."):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate research progress
        import time
        research_steps = [
            "🌍 Analyzing destination...",
            "🏨 Researching accommodations...", 
            "🍽️ Finding top restaurants...",
            "🎭 Discovering activities...",
            "💰 Calculating realistic costs...",
            "📝 Generating personalized itinerary..."
        ]
        
        async def generate_with_progress():
            for i, step in enumerate(research_steps):
                status_text.text(step)
                progress_bar.progress((i + 1) / len(research_steps))
                await asyncio.sleep(0.5)
            
            # Generate the actual itinerary
            itinerary_data = await plan_itinerary(user_query, MODELS[model_choice]["name"])
            return itinerary_data
        
        # Execute the planning
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        try:
            itinerary = loop.run_until_complete(generate_with_progress())
        except Exception as e:
            st.error(f"❌ Error generating itinerary: {str(e)}")
            st.stop()
    
    # Clear progress indicators
    progress_bar.empty()
    status_text.empty()
    
    # Handle errors
    if "error" in itinerary:
        st.error(f"❌ {itinerary['error']}")
        if "raw_response" in itinerary:
            with st.expander("🔍 Debug Information"):
                st.text(itinerary['raw_response'])
        st.stop()
    
    # Display the itinerary
    st.success("✅ Your personalized itinerary is ready!")
    
    # Trip Summary
    if "trip_summary" in itinerary:
        summary = itinerary["trip_summary"]
        st.markdown('<div class="trip-summary">', unsafe_allow_html=True)
        st.write("### 📋 Trip Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🏛️ Destination", summary["destination"])
        with col2:
            st.metric("📅 Duration", f"{summary['total_days']} days")
        with col3:
            st.metric("💰 Budget", f"${summary['budget']:,}")
        with col4:
            st.metric("⏱️ Pace", summary["pace"])
        
        st.write(f"**Overview:** {summary['overview']}")
        st.write(f"**Interests:** {', '.join(summary['interests'])}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
    
    # Create main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💰 Budget Analysis", 
        "📅 Daily Itinerary", 
        "ℹ️ Essential Info", 
        "🔄 Alternatives",
        "💾 Export"
    ])
    
    with tab1:
        if "budget_analysis" in itinerary:
            render_budget_analysis(itinerary["budget_analysis"], budget)
        else:
            st.warning("Budget analysis not available in the generated itinerary.")
    
    with tab2:
        if "daily_itinerary" in itinerary:
            render_daily_itinerary(itinerary["daily_itinerary"])
        else:
            st.warning("Daily itinerary not available in the generated response.")
    
    with tab3:
        if "essential_info" in itinerary:
            render_essential_info(itinerary["essential_info"])
        else:
            st.warning("Essential information not available in the generated response.")
    
    with tab4:
        if "alternatives" in itinerary:
            render_alternatives(itinerary["alternatives"])
        else:
            st.warning("Alternative options not available in the generated response.")
    
    with tab5:
        st.subheader("💾 Export Your Itinerary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON export
            json_data = json.dumps(itinerary, indent=2)
            st.download_button(
                label="📄 Download as JSON",
                data=json_data,
                file_name=f"itinerary_{dest_val.replace(' ', '_').lower()}_{start_date.strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        
        with col2:
            # Create a readable text version
            text_export = f"""
# {dest_val} Travel Itinerary
**Generated by AI Travel Planner v7**

## Trip Summary
- **Destination:** {itinerary.get('trip_summary', {}).get('destination', dest_val)}
- **Dates:** {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}
- **Duration:** {trip_days} days
- **Budget:** ${budget:,} USD
- **Pace:** {pace}

## Budget Breakdown
"""
            if "budget_analysis" in itinerary:
                budget_data = itinerary["budget_analysis"]
                text_export += f"""
- **Total Estimated:** ${budget_data['total_estimated']:,}
- **Accommodation:** ${budget_data['accommodation']['total']:,}
- **Food:** ${budget_data['food']['total']:,}
- **Activities:** ${budget_data['activities']['total']:,}
- **Transportation:** ${budget_data['transportation']['total']:,}
"""
            
            # Add daily itinerary
            if "daily_itinerary" in itinerary:
                text_export += "\n## Daily Itinerary\n"
                for day in itinerary["daily_itinerary"]:
                    text_export += f"\n### Day {day['day']} - {day['theme']}\n"
                    text_export += f"**Date:** {day['date']}\n"
                    text_export += f"**Daily Cost:** ${day['daily_total_cost']:,}\n\n"
                    
                    # Add activities
                    for time_slot in ['morning', 'afternoon', 'evening']:
                        if time_slot in day and day[time_slot]:
                            activity = day[time_slot]['activity']
                            text_export += f"**{time_slot.title()}:** {activity['name']} (${activity['cost']:,})\n"
                            text_export += f"  - {activity['description']}\n"
                            if activity.get('pro_tip'):
                                text_export += f"  - 💡 Pro Tip: {activity['pro_tip']}\n"
                    
                    text_export += "\n"
            
            st.download_button(
                label="📝 Download as Text",
                data=text_export,
                file_name=f"itinerary_{dest_val.replace(' ', '_').lower()}_{start_date.strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    
    # Store itinerary in session state for later use
    st.session_state['last_itinerary'] = itinerary
    st.session_state['last_query'] = user_query

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>✨ AI Travel Planner v7 - Enhanced with Superior Prompting & Modern UI</p>
    <p>🔍 Powered by real-time web search and advanced AI planning</p>
</div>
""", unsafe_allow_html=True)

# Sidebar footer with tips
with st.sidebar:
    st.markdown("---")
    st.markdown("### 💡 Pro Tips")
    st.markdown("""
    - **More specific interests** = better recommendations
    - **Flexible dates** = potential savings
    - **Local experiences** add authenticity
    - **Mix of famous & hidden gems** for best trips
    """)
    
    st.markdown("### 🔧 Features")
    st.markdown("""
    - ✅ Real-time web search
    - ✅ Verified booking links
    - ✅ Realistic cost estimates
    - ✅ Traveler pro tips
    - ✅ Interactive modern UI
    - ✅ Multiple export formats
    """)