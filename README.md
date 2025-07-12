# AI Travel Planner v7

An advanced AI-powered travel planning application built with Streamlit, designed to generate comprehensive, personalized travel itineraries with rich details, budget analysis, and modern UI features.

---

## Features

- **Structured JSON Output**: Generates detailed itineraries in a structured JSON format for easy parsing and integration.
- **Modern User Interface**: Interactive UI with tabs, expanders, columns, and metrics for a rich user experience.
- **Real-Time Web Search & Scraping**: Integrates real-time web search and webpage scraping to provide up-to-date travel information.
- **Budget Analysis**: Provides realistic cost breakdowns including accommodation, food, activities, transportation, and miscellaneous expenses.
- **Pro Tips & Justifications**: Includes actionable traveler tips and explanations for each recommendation.
- **Multiple Export Formats**: Export itineraries as JSON or readable text files.
- **Save Favorite Destinations**: Quickly save and select favorite destinations for faster itinerary generation.
- **Flexible AI Model Selection**: Choose between fast and capable AI models for itinerary generation.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- API keys for OpenAI and optionally Brave Search (for enhanced search results)

### Installation

1. Clone the repository or download the `app.py` file.

2. Create a `requirements.txt` file with the following dependencies:

```
streamlit>=1.35.0
openai>=1.30.0
httpx>=0.27.0
beautifulsoup4>=4.12.3
ddgs>=6.1.4
diskcache>=5.6.3
geopy>=2.4.1
plotly>=5.17.0
```

3. Install the dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.streamlit/secrets.toml` file in your project directory and add your API keys:

```toml
OPENAI_API_KEY = "your_openai_api_key_here"
# Optional but recommended for better search results
BRAVE_API_KEY = "your_brave_api_key_here"
```

### Running the App

Run the Streamlit app from your terminal:

```bash
streamlit run app.py
```

---

## Usage

- Enter your origin and destination cities with helpful location suggestions.
- Select trip dates, budget, interests, and trip pace.
- Choose the AI model for itinerary generation.
- Generate a personalized travel itinerary with detailed daily plans, budget analysis, essential info, and alternative options.
- Save favorite destinations for quick access in future sessions.
- Export your itinerary as JSON or text files.

---

## Project Structure

- `app.py`: Main application file containing UI, AI integration, and business logic.
- `.streamlit/secrets.toml`: Configuration file for API keys (not included in repo).
- `requirements.txt`: Python dependencies.

---

## Technologies Used

- Python 3.8+
- Streamlit for UI
- OpenAI API for AI-powered itinerary generation
- HTTPX and BeautifulSoup for web scraping
- DiskCache for caching
- Geopy for geolocation services
- Plotly for interactive charts
- DuckDuckGo and Brave Search APIs for web search

---

## Future Improvements

- Add weather forecast integration for trip dates.
- Implement packing checklist generator based on destination and weather.
- Include local events and currency converter widgets.
- Enhance UI with user authentication and persistent storage.

---

## License

This project is open source and available under the MIT License.

---

## Contact

For questions or contributions, please contact [Your Name] at [your.email@example.com].

---

*This project showcases advanced AI integration and modern UI design, making it an excellent portfolio piece for job and university applications.*
