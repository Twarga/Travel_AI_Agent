"""
LLM Travel Itinerary Creator with Niche Website Scraping, OpenStreetMap Geocoding & Traveler Advice from Reddit/Web using Together API
"""

import asyncio
import os
import re
import tempfile
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin

import streamlit as st
from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig
from crawl4ai.content_filter_strategy import BM25ContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.models import CrawlResult
from duckduckgo_search import DDGS # Still imported, but not used for transportation anymore
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# from groq import Groq  # Import Groq client # REMOVE GROQ IMPORT
import time # Import time for delays
from together import Together # IMPORT TOGETHER API
from geopy.geocoders import Nominatim # Import Nominatim geocoder

# Initialize Together client # CHANGE CLIENT INITIALIZATION
client = Together(api_key="87954ab2159fc36e7b13b6dfcaf79228e8ad99e75e7cc0026452aa451ed6ab4c") # Replace "YOUR_TOGETHER_API_KEY" with your actual Together API key

# Initialize Nominatim geocoder
geolocator = Nominatim(user_agent="travel_itinerary_app") # Replace "travel_itinerary_app" with a descriptive user agent

# --- Updated System Prompt - EMPHASIS ON TRAVELER ADVICE ---
SYSTEM_PROMPT_ITINERARY = """
You are an expert travel planning assistant. Your ABSOLUTE TOP PRIORITY is to create a detailed, day-by-day itinerary with **VERIFIED, WORKING HYPERLINKS** for hotels, activities, and restaurants, **OPENSTREETMAP LINKS FOR ALL LOCATIONS**, and **incorporating travel advice and experiences from previous travelers**. Be informative, engaging, and provide a realistic and enjoyable schedule, including transportation. Prioritize popular and highly-rated options within budget, and consider advice from travelers. Use emojis for readability.

**Incorporate travel advice and tips from previous travelers** into the itinerary. This advice can include tips on:
* Local customs and etiquette
* Safety tips
* Best times to visit certain attractions (avoiding crowds)
* Hidden gems or less touristy but worthwhile places
* Transportation tips within the destination
* Food and drink recommendations beyond typical tourist spots
* Budget-saving tips

**YOUR #1 TASK IS TO INCLUDE REAL, FUNCTIONAL HYPERLINKS, OPENSTREETMAP LINKS, AND RELEVANT TRAVELER ADVICE.**  These links MUST be to actual booking pages or official websites, **OPENSTREETMAP LOCATION LINKS** for **hotels, activities, and restaurants**, and traveler advice should be based on real user experiences found on the internet. **UNDER NO CIRCUMSTANCES should you use placeholder links like example.com or generate fake URLs, or invent travel advice.**

**LOCATION LINKS ARE MANDATORY FOR EVERY HOTEL, ACTIVITY, AND RESTAURANT.**  You **MUST** include an OpenStreetMap link for each location.

**LINK VERIFICATION IS CRITICAL.** Before including a link in the itinerary, you must **CONFIRM** that it is a valid, working URL that directly leads to the intended page. **For all locations (hotels, activities, restaurants), ALWAYS include an OPENSTREETMAP link** to the exact location if possible. If a direct OpenStreetMap link is not readily available from the scraped data, attempt to generate one using the location name and destination. If generating an OpenStreetMap link is not possible, provide the location name as plain text, BUT MAKE SURE TO INCLUDE AS MANY LOCATION DETAILS AS POSSIBLE so the user can easily search for it.

Estimate flight and public transportation costs. If exact prices are missing, use typical costs for the destination and budget.

Information will be structured as:
* User Prompt: [Original user request]
* Flight Information: [if available]
* Hotel Options: [List of hotels with names, prices, descriptions, and URLs if found, **OPENSTREETMAP LINK**]
* Restaurant Options: [List of restaurants with names, cuisine, price ranges, and URLs if found, **OPENSTREETMAP LINK**]
* Activity Options: [List of activities with names, descriptions, and URLs if found, **OPENSTREETMAP LINK**]
* Traveler Advice: [Summarized advice and tips from previous travelers, with source if possible]
* Budget: [Total budget]
* Budget Breakdown: [Category-wise budget allocation if provided]

Format your output as a day-by-day itinerary:

**Day 1: [Date]** 📅
* Morning: [Activity/Description] 🌅 **(ONLY create a Markdown link [Activity Name](VERIFIED_URL) if you have a CONFIRMED, WORKING, and RELEVANT URL. Otherwise, use plain text Activity Name.)**  📍 **[OPENSTREETMAP LINK (or plain text location if no link)]**
* Afternoon: [Activity/Description] 🏞️ **(Same link verification rule)** 📍 **[OPENSTREETMAP LINK (or plain text location if no link)]**
* Evening: [Activity/Description] 🌃 **(Same link verification rule)** 📍 **[OPENSTREETMAP LINK (or plain text location if no link)]**
* Hotel: [Hotel Name] 🏨 **(ONLY create a Markdown link [Hotel Name](VERIFIED_URL) if you have a CONFIRMED, WORKING, and DIRECT URL to a booking page or official hotel website. Otherwise, use plain text Hotel Name.)** 📍 **[OPENSTREETMAP LINK (or plain text location if no link)]**
* Estimated Daily Transportation Cost: [Cost] 🚕
* Estimated Cost (excluding flights & hotel): [Cost] 💰

**Day 2: [Date]** 📅
... (and so on) ...

**Traveler Advice & Tips:**
* [Tip 1, potentially with source]
* [Tip 2, potentially with source]
* ... (and so on) ...

**Estimated Flight Cost:** [Estimated round-trip flight cost] ✈️ **(Provide a clear estimate. Use flight info from context if available; else, give a reasonable general estimate for origin-destination flights.)**
**Total Estimated Daily Transportation Cost:** [Sum of daily transport costs] 🚕
**Total Estimated Cost (excluding flights & hotel):** [Sum of daily costs excluding hotel] 💰
**Grand Total Estimated Cost:** [Sum of all costs] 🌟

**BUDGET CONSIDERATION:** Please consider the user's budget and budget breakdown when generating the itinerary. Prioritize options that fit within their allocated budget categories. If "Budget-Conscious Mode" is enabled, focus on free or low-cost activities and affordable options.

**OPENSTREETMAP INTEGRATION:**  Utilize OpenStreetMap links for **ALL LOCATIONS (hotels, activities, restaurants)**. If direct OpenStreetMap links are not found during scraping, attempt to generate them using location names and geocoding services.

**TRAVELER ADVICE INTEGRATION:**  Incorporate summarized and relevant travel advice and tips into the itinerary, drawing from scraped content from Reddit and general internet sources.

**ABSOLUTE RULE FOR LINKS:**
* **ONLY include links that you have ACTIVELY VERIFIED to be working, relevant, and high-quality booking/official website links.**
* **If in DOUBT about a link's validity or relevance, DO NOT INCLUDE IT. Output plain text instead.**
* **Broken links and fake links are completely unacceptable.**

If information is missing, make reasonable assumptions but clearly indicate them.
"""

# --- LLM Call Function using Together API --- # CHANGE LLM CALL FUNCTION
def call_llm(prompt: str, with_context: bool = True, context: str | None = None):
    """
    Call the Together API with the itinerary prompt and context.
    """
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT_ITINERARY},
        {"role": "user", "content": f"User Preferences: {prompt}\n\nContext: {context}"}, # Include user preferences in the prompt
    ]
    if not with_context:
        messages.pop(0)
        messages[0]["content"] = prompt

    response = client.chat.completions.create(
    model="deepseek-ai/DeepSeek-R1",
    messages=messages, # Use the constructed messages here
    max_tokens=15000, # Increased max tokens to accommodate more detail, including advice
    temperature=0.6,
    top_p=0.95,
    top_k=50,
    repetition_penalty=1,
    stop=["<｜end of sentence｜>"],
    stream=True
    )
    for token in response:
        if hasattr(token, 'choices'):
            yield token.choices[0].delta.content or "" # Access content in the same way


# --- URL Normalization ---
def normalize_url(url: str) -> str:
    normalized_url = (
        url.replace("https://", "")
           .replace("http://", "")
           .replace("www.", "")
           .replace("/", "_")
           .replace("-", "_")
           .replace(".", "_")
    )
    print("Normalized URL:", normalized_url)
    return normalized_url

# --- OpenStreetMap Function ---
def get_openstreetmap_link_from_query(query):
    """Generates an OpenStreetMap link from a text query using Nominatim geocoding."""
    try:
        location = geolocator.geocode(query)
        if location:
            return f"https://www.openstreetmap.org/?mlat={location.latitude}&mlon={location.longitude}&zoom=15" # Zoom level 15 is a good default
        else:
            return None # Location not found
    except Exception as e: # Catch geocoding errors
        print(f"Geocoding error for query '{query}': {e}")
        return None


# --- Niche Website URL Generation Functions (PLACEHOLDERS - **YOU NEED TO IMPLEMENT**) ---
def get_skyscanner_urls(query_params):
    origin = query_params["origin"]
    destination = query_params["destination"]
    start_date = query_params["start_date"]
    end_date = query_params["end_date"]
    budget = query_params["budget"]

    # **IMPLEMENT REAL SKYSCANNER URL GENERATION LOGIC HERE**
    # **RESEARCH SKYSCANNER URL STRUCTURE FOR FLIGHT SEARCHES**
    example_url = "https://www.skyscanner.net/" # Placeholder - replace with actual Skyscanner search URL
    print(f"Using Skyscanner Placeholder URL for: {query_params}") # Debugging
    return [example_url]

def get_bookingcom_urls(query_params):
    destination = query_params["destination"]
    budget = query_params["budget"]

    # **IMPLEMENT REAL BOOKING.COM URL GENERATION LOGIC HERE**
    # **RESEARCH BOOKING.COM URL STRUCTURE FOR HOTEL SEARCHES**
    example_url = "https://www.booking.com/" # Placeholder - replace with actual Booking.com search URL
    print(f"Using Booking.com Placeholder URL for: {query_params}") # Debugging
    return [example_url]

def get_tripadvisor_activity_urls(query_params):
    destination = query_params["destination"]
    activity_type = query_params["type"]

    # **IMPLEMENT REAL TRIPADVISOR URL GENERATION LOGIC HERE**
    # **RESEARCH TRIPADVISOR URL STRUCTURE FOR ACTIVITIES**
    example_url = "https://www.tripadvisor.com/" # Placeholder - replace with actual TripAdvisor activities URL
    print(f"Using TripAdvisor Activity Placeholder URL for: {query_params}") # Debugging
    return [example_url]

def get_tripadvisor_restaurant_urls(query_params):
    destination = query_params["destination"]
    cuisine_type = query_params["cuisine"]

    # **IMPLEMENT REAL TRIPADVISOR URL GENERATION LOGIC HERE**
    # **RESEARCH TRIPADVISOR URL STRUCTURE FOR RESTAURANTS**
    example_url = "https://www.tripadvisor.com/" # Placeholder - replace with actual TripAdvisor restaurants URL
    print(f"Using TripAdvisor Restaurant Placeholder URL for: {query_params}") # Debugging
    return [example_url]

def get_rome2rio_urls(query_params): # Example for Rome2Rio - you might need to adjust categories
    destination = query_params["destination"]
    origin = query_params["origin"] # Example - if origin is relevant for Rome2Rio

    # **IMPLEMENT REAL ROME2RIO URL GENERATION LOGIC HERE**
    # **RESEARCH ROME2RIO URL STRUCTURE FOR TRANSPORTATION**
    example_url = "https://www.rome2rio.com/" # Placeholder - replace with actual Rome2Rio URL
    print(f"Using Rome2Rio Placeholder URL for: {query_params}") # Debugging
    return [example_url]


def get_duckduckgo_urls(search_term, num_results=3) -> list[str]: # Increased num_results for traveler advice
    try:
        discard_urls = ["youtube.com", "britannica.com", "vimeo.com", "pinterest.com", "facebook.com", "instagram.com", "tiktok.com", "twitter.com"] # Added social media and visual platforms
        for url in discard_urls:
            search_term += f" -site:{url}"
        results = DDGS().text(search_term, max_results=num_results)
        time.sleep(3) # Delay - keep a delay
        results = [result["href"] for result in results]
        return check_robots_txt(results)
    except Exception as e:
        error_msg = f"❌ Failed to fetch results from the web: {e}"
        print(error_msg)
        st.write(error_msg)
        st.stop()
        return [] # Return empty list in case of error

# --- Web Crawling ---
async def crawl_webpages(urls: list[str], prompt: str) -> list[CrawlResult]:
    bm25_filter = BM25ContentFilter(user_query=prompt, bm25_threshold=1.0) # Slightly more relaxed BM25 for advice
    md_generator = DefaultMarkdownGenerator(content_filter=bm25_filter)
    crawler_config = CrawlerRunConfig(
        markdown_generator=md_generator,
        excluded_tags=["nav", "footer", "header", "form", "img", "a", "iframe", "script", "noscript", "aside", "ul", "li", "button", "input", "textarea", "select", "option", "style", "svg", "canvas", "video", "audio"], # Even more aggressive exclusion
        only_text=True,
        exclude_social_media_links=True,
        keep_data_attributes=False,
        cache_mode=CacheMode.BYPASS,
        remove_overlay_elements=True,
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/132.0.0.0 Safari/537.36",
        page_timeout=60000, # Increased page timeout
    )
    browser_config = BrowserConfig(headless=True, text_mode=True, light_mode=True)
    async with AsyncWebCrawler(config=browser_config) as crawler:
        results = await crawler.arun_many(urls, config=crawler_config)
        return results

# --- Robots.txt Check ---
def check_robots_txt(urls: list[str]) -> list[str]:
    allowed_urls = []
    for url in urls:
        try:
            robots_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}/robots.txt"
            rp = RobotFileParser(robots_url)
            rp.read()
            if rp.can_fetch("*", url):
                allowed_urls.append(url)
        except Exception:
            allowed_urls.append(url)
    return allowed_urls


# --- Travel Query Parsing ---
def parse_travel_query(details: dict) -> dict | None:
    """
    Basic parsing assuming the prompt format is:
    "I want to travel to [destination] for [duration] days from [origin] from [start_date] to [end_date], my budget is [amount]$"
    """
    return details # No parsing needed now as we get structured data from form

# --- Generate Category-Specific Search Queries - Niche Websites Defined ---
def generate_category_queries(details: dict) -> dict:
    destination = details.get("destination")
    origin = details.get("origin")
    start_date = details.get("start_date")
    end_date = details.get("end_date")
    budget = details.get("budget")
    return {
        "flights": {
            "site": "skyscanner", # Use Skyscanner for flights
            "query": {
                "origin": origin,
                "destination": destination,
                "start_date": start_date,
                "end_date": end_date,
                "budget": budget,
            }
        },
        "hotels": {
            "site": "bookingcom", # Use Booking.com for hotels
            "query": {
                "destination": destination,
                "budget": budget,
            }
        },
        "activities": {
            "site": "tripadvisor", # Use TripAdvisor for activities
            "query": {
                "destination": destination,
                "type": "things to do",
            }
        },
        "restaurants": {
            "site": "tripadvisor", # Use TripAdvisor for restaurants
            "query": {
                "destination": destination,
                "cuisine": "budget-friendly",
            }
        },
        "transportation": {
            "site": "rome2rio", # Use Rome2Rio for transportation
            "query": {
                "destination": destination, # Rome2Rio might use destination as main parameter
                "origin": origin # You might need origin too, depending on Rome2Rio URL structure
            }
        },
        "travel_advice": { # New category for travel advice
            "site": "duckduckgo",
            "query": {
                "destination": destination,
                "advice_type": "travel advice and tips" # More descriptive type
            }
        }
    }

# --- Generate Combined Travel Context from Web Searches ---
async def generate_travel_context(details: dict) -> tuple[str, str]: # Modified return type to tuple
    queries = generate_category_queries(details)
    category_contexts = {}
    travel_advice_context = "" # Initialize travel advice context

    hotel_locations = {} # Store hotel names and locations for directions
    activity_locations = {} # Store activity names and locations
    restaurant_locations = {} # Store restaurant names and locations

    for category, query_info in queries.items():
        site = query_info["site"]
        query_params = query_info["query"]

        st.write(f"Searching for {category} info on {site.upper()}: {query_params}")

        urls = []
        if site == "skyscanner":
            urls = get_skyscanner_urls(query_params)
        elif site == "bookingcom":
            urls = get_bookingcom_urls(query_params)
        elif site == "tripadvisor" and category in ["activities", "restaurants"]: # Group activities and restaurants
            if category == "activities":
                urls = get_tripadvisor_activity_urls(query_params)
            elif category == "restaurants":
                urls = get_tripadvisor_restaurant_urls(query_params)
        elif site == "rome2rio": # Use Rome2Rio URL function for transportation
            urls = get_rome2rio_urls(query_params)
        elif site == "duckduckgo" and category == "travel_advice": # Handle travel advice search
            search_term = f"{query_params['advice_type']} {query_params['destination']}" # Construct search query
            urls = get_duckduckgo_urls(search_term=search_term, num_results=5) # Get more results for advice
        else:
            st.warning(f"No URL function defined for site: {site}")
            category_contexts[category] = f"No info found for {category}."
            continue

        if urls:
            results = await crawl_webpages(urls=urls, prompt=str(query_params))
            context_text_list = []
            for result in results:
                if result.markdown_v2:
                    context_text_list.append(result.markdown_v2.fit_markdown)

                # Location extraction and OSM link generation (same logic as before, now for all location types)
                location_name = None
                if category == "hotels" and result.url:
                    hotel_name_match = re.search(r"/(.*?)/hotel-reviews/", result.url)
                    location_name = hotel_name_match.group(1).replace("-", " ").title() if hotel_name_match else "Hotel"
                elif category == "activities" and result.url:
                    activity_name_match = re.search(r"/(.*?)/Attractions-g", result.url) # Adjust regex if needed
                    location_name = activity_name_match.group(1).replace("-", " ").title() if activity_name_match else "Activity"
                elif category == "restaurants" and result.url:
                    restaurant_name_match = re.search(r"/(.*?)/Restaurants-g", result.url) # Adjust regex if needed
                    restaurant_name = restaurant_name_match.group(1).replace("-", " ").title() if restaurant_name_match else "Restaurant"

                if location_name:
                    location_query = f"{location_name}, {details['destination']}"
                    openstreetmap_link = get_openstreetmap_link_from_query(location_query)
                    if openstreetmap_link:
                        if category == "hotels":
                            hotel_locations[location_name] = openstreetmap_link
                        elif category == "activities":
                            activity_locations[location_name] = openstreetmap_link
                        elif category == "restaurants":
                            restaurant_locations[location_name] = openstreetmap_link
                    else:
                        if category == "hotels":
                            hotel_locations[location_name] = location_query
                        elif category == "activities":
                            activity_locations[location_name] = location_query
                        elif category == "restaurants":
                            restaurant_locations[location_name] = location_query
                elif category == "travel_advice": # Aggregate travel advice context
                    travel_advice_context += "\n".join(context_text_list) # Append all advice

            context_text = "\n".join(context_text_list)[:3000] # Limit context size if needed
            category_contexts[category] = context_text
        else:
            category_contexts[category] = f"No {category} info found on {site.upper()}."

    combined_context = ""
    for category, text in category_contexts.items():
        if category != "travel_advice": # Exclude raw travel advice context from main context
            combined_context += f"### {category.capitalize()}\n{text}\n\n"

    # Store locations and travel advice in details to pass to LLM and for itinerary generation
    details['hotel_locations'] = hotel_locations
    details['activity_locations'] = activity_locations
    details['restaurant_locations'] = restaurant_locations
    details['travel_advice_context'] = travel_advice_context # Store travel advice context


    return combined_context, travel_advice_context # Return both contexts

# --- Main App ---
async def run():
    st.set_page_config(page_title="Travel Plan Itinerary Creator")
    st.header("✈️ Travel Plan Itinerary Creator")

    with st.sidebar:
        st.header("Travel Details")
        with st.form(key='travel_form'):
            destination = st.text_input("Destination", placeholder="e.g., Bali, Thailand, Paris")
            duration = st.number_input("Duration (days)", min_value=1, value=15)
            origin = st.text_input("Origin", placeholder="e.g., Fes, New York, London")
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            budget = st.number_input("Total Budget ($)", min_value=100, value=3000)
            currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "JPY", "CAD", "AUD", "INR", "AED", "CHF", "CNY"]) # Currency selection
            is_web_search = st.checkbox("Enable web search for travel info", value=True)
            budget_conscious_mode = st.checkbox("Budget-Conscious Mode", value=False) # Budget-conscious mode

            st.subheader("Budget Allocation (Optional)") # Budget allocation section
            budget_flights_percent = st.slider("Flights (%)", 0, 100, 30)
            budget_accommodation_percent = st.slider("Accommodation (%)", 0, 100, 30)
            budget_activities_percent = st.slider("Activities/Entertainment (%)", 0, 100, 20)
            budget_food_percent = st.slider("Food/Dining (%)", 0, 100, 10)
            budget_transport_percent = st.slider("Local Transportation (%)", 0, 100, 5)
            budget_shopping_percent = st.slider("Shopping/Souvenirs (%)", 0, 100, 3)
            budget_misc_percent = st.slider("Miscellaneous/Buffer (%)", 0, 100, 2)

            st.subheader("Travel Style & Interests")
            travel_style = st.selectbox("Travel Style", ["Adventure", "Relaxation", "Luxury", "Budget-friendly", "Cultural", "Foodie", "Nature", "Nightlife", "Family-friendly", "Solo Traveler", "Romantic Getaway", "No Preference"])
            interests = st.multiselect("Interests", ["History", "Museums", "Beaches", "Hiking", "Shopping", "Live Music", "Art", "Wildlife", "Theme Parks", "Spas", "Yoga", "Photography", "Food Tours", "Wine Tasting", "Sports", "Architecture", "Gardens", "Festivals", "Local Markets"])
            pace_of_travel = st.select_slider("Pace of Travel", options=["Relaxed", "Moderate", "Packed"])

            st.subheader("Accommodation Preferences")
            hotel_star_rating = st.selectbox("Hotel Star Rating (Optional)", ["No Preference", "3-star", "4-star", "5-star"])
            hotel_type = st.multiselect("Hotel Type (Optional)", ["Boutique Hotel", "Resort", "Hostel", "Airbnb-like", "Apartment", "Guesthouse", "Luxury Hotel"])
            location_preference = st.multiselect("Location Preference (Optional)", ["City Center", "Beachfront", "Quiet Area", "Near Public Transport", "Countryside", "Mountain Area"])
            hotel_amenities = st.multiselect("Hotel Amenities (Optional)", ["Pool", "Gym", "Breakfast Included", "Pet-friendly", "Family Suites", "Spa", "Parking", "Free Wi-Fi", "Airport Shuttle"])

            st.subheader("Food & Restaurant Preferences")
            cuisine_types = st.multiselect("Cuisine Types (Optional)", ["Italian", "Japanese", "Local Cuisine", "Mexican", "Indian", "Chinese", "French", "American", "Thai", "Spanish", "Greek", "Vegetarian", "Vegan", "Seafood", "Steakhouse", "Fast Food"])
            dining_style = st.multiselect("Dining Style (Optional)", ["Fine Dining", "Casual", "Street Food", "Cafes", "Bars", "Pubs", "Food Trucks"])
            dietary_restrictions = st.text_input("Dietary Restrictions/Allergies (Optional)", placeholder="e.g., Gluten-free, Nut Allergy, Vegetarian")

            st.subheader("Transportation Preferences (Within Destination)")
            preferred_transport_modes = st.multiselect("Preferred Transportation Modes (Optional)", ["Public Transport", "Taxi/Ride-sharing", "Walking/Cycling", "Rental Car", "Train", "Bus", "Ferry", "Motorcycle/Scooter"])
            acceptable_travel_time = st.selectbox("Acceptable Travel Time Between Activities (Optional)", ["Short Distances", "Willing to Travel", "Minimize Travel Time", "No Preference"])

            st.subheader("Time of Day Preference")
            time_of_day_preference = st.selectbox("Preferred Time of Day for Activities (Optional)", ["No Preference", "Morning Person", "Evening Person"])


            go = st.form_submit_button("⚡️ Generate Itinerary")

        if go:
            if not destination or not origin:
                st.error("Please enter both Destination and Origin.")
                st.stop()

            budget_breakdown = { # Calculate budget breakdown amounts
                "flights": budget * (budget_flights_percent / 100),
                "accommodation": budget * (budget_accommodation_percent / 100),
                "activities": budget * (budget_activities_percent / 100),
                "food": budget * (budget_food_percent / 100),
                "transportation": budget * (budget_transport_percent / 100),
                "shopping": budget * (budget_shopping_percent / 100),
                "miscellaneous": budget * (budget_misc_percent / 100),
            }

            details = {
                "destination": destination,
                "duration": duration,
                "origin": origin,
                "start_date": start_date.strftime("%d %b %Y"), # Format date for query
                "end_date": end_date.strftime("%d %b %Y"),     # Format date for query
                "budget": budget,
                "currency": currency, # Include currency
                "is_budget_conscious": budget_conscious_mode, # Include budget conscious mode
                "budget_breakdown": budget_breakdown, # Include budget breakdown
                "travel_style": travel_style,
                "interests": interests,
                "pace_of_travel": pace_of_travel,
                "hotel_star_rating": hotel_star_rating,
                "hotel_type": hotel_type,
                "location_preference": location_preference,
                "hotel_amenities": hotel_amenities,
                "cuisine_types": cuisine_types,
                "dining_style": dining_style,
                "dietary_restrictions": dietary_restrictions,
                "preferred_transport_modes": preferred_transport_modes,
                "acceptable_travel_time": acceptable_travel_time,
                "time_of_day_preference": time_of_day_preference,
                "travel_advice_context": "", # Initialize here, will be updated after web search but before LLM call # Initialize travel advice context
            }

            st.write("Parsed Travel Details:", details) # Display parsed details in sidebar

            if is_web_search:
                travel_context, travel_advice_context = await generate_travel_context(details) # Capture both return values
                details["travel_advice_context"] = travel_advice_context # Update details with travel advice context
                # st.write("### Web Context", travel_context) # Commented out raw context display
                st.info("Generating Itinerary... Please wait.") # Added info message
                llm_response = call_llm(context=travel_context, prompt=str(details), with_context=True) # Pass details as prompt
                st.session_state.itinerary_output = llm_response # Store output in session state
            else:
                st.info("Generating Itinerary... Please wait.") # Added info message
                llm_response = call_llm(prompt=str(details), with_context=False) # Pass details as prompt
                st.session_state.itinerary_output = llm_response # Store output in session state
        else:
             st.session_state.itinerary_output = None # Clear output if form not submitted


    if st.session_state.itinerary_output: # Display itinerary in the main area if generated
        itinerary_text = ""
        for part in st.session_state.itinerary_output:
            itinerary_text += part

        st.header("✨ Itinerary:")
        # --- Process and Display Itinerary with OpenStreetMap Links and Traveler Advice ---
        itinerary_lines = itinerary_text.splitlines()
        advice_started = False # Flag to track advice section

        for line in itinerary_lines:
            if line.startswith("**Day"): # Day Header
                st.subheader(line)
                advice_started = False # Reset advice flag for each day
            elif line.startswith("* Morning:") or line.startswith("* Afternoon:") or line.startswith("* Evening:") or line.startswith("* Restaurant:") : # Activity/Restaurant Line
                parts = line.split("📍")
                location_text = parts[0] # Activity/Restaurant description and link
                st.markdown(location_text)

                if len(parts) > 1: # OpenStreetMap link is present
                    openstreetmap_url = parts[1].strip()
                    if openstreetmap_url.startswith("http"): # Check if it's a valid URL
                        st.markdown(f"    📍 [OpenStreetMap]({openstreetmap_url})")
                    else:
                        st.write(f"    📍 {openstreetmap_url}") # Plain text location

            elif line.startswith("* Hotel:"): # Hotel Line
                parts = line.split("📍")
                hotel_text = parts[0]
                st.markdown(hotel_text)

                if len(parts) > 1: # OpenStreetMap link is present
                    openstreetmap_url = parts[1].strip()
                    if openstreetmap_url.startswith("http"): # Check if it's a valid URL
                        st.markdown(f"    🏨 [OpenStreetMap]({openstreetmap_url})")
                    else:
                        st.write(f"    🏨 {openstreetmap_url}") # Plain text location

            elif line.startswith("Estimated Flight Cost:") or line.startswith("Total Estimated Daily Transportation Cost:") or line.startswith("Total Estimated Cost") or line.startswith("Grand Total Estimated Cost:"): # Budget Lines
                 st.markdown(line)
            elif line.startswith("Traveler Advice & Tips:") or advice_started: # Traveler Advice Section
                if line.startswith("Traveler Advice & Tips:"):
                    st.subheader("Traveler Advice & Tips:") # Subheader for advice
                    advice_started = True # Set flag
                elif advice_started and line.strip(): # Display advice lines if flag is set and line is not empty
                    st.markdown(f"* {line.strip()}") # Markdown list for advice
            else: # Other lines (like daily cost estimates)
                st.write(line)


    elif go: # Show message if button is pressed but no output yet (e.g., loading)
        st.info("Generating itinerary... Please wait in sidebar for details and here for final output.")
    else: # Default message when app loads
        st.info("⬅️ Enter your travel details in the sidebar to generate an itinerary.")


if __name__ == "__main__":
    import urllib
    asyncio.run(run())