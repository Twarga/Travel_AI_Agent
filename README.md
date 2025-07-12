# AI Travel Planner v7

<p align="center">
  <img src="https://img.shields.io/badge/Streamlit-1.35.0-green" alt="Streamlit Version" />
  <img src="https://img.shields.io/badge/OpenAI-1.30.0-blue" alt="OpenAI Version" />
  <img src="https://img.shields.io/badge/HTTPX-0.27.0-lightgrey" alt="HTTPX Version" />
  <img src="https://img.shields.io/badge/BeautifulSoup-4.12.3-orange" alt="BeautifulSoup Version" />
  <img src="https://img.shields.io/badge/DuckDuckGo-6.1.4-yellow" alt="DuckDuckGo Version" />
  <img src="https://img.shields.io/badge/DiskCache-5.6.3-red" alt="DiskCache Version" />
  <img src="https://img.shields.io/badge/Geopy-2.4.1-blueviolet" alt="Geopy Version" />
  <img src="https://img.shields.io/badge/Plotly-5.17.0-purple" alt="Plotly Version" />
</p>

An advanced AI-powered travel planning application built with Streamlit, designed to generate comprehensive, personalized travel itineraries with rich details, budget analysis, and modern UI features.

---

## Features

<ul>
<li><strong>Structured JSON Output</strong>: Generates detailed itineraries in a structured JSON format for easy parsing and integration.</li>
<li><strong>Modern User Interface</strong>: Interactive UI with tabs, expanders, columns, and metrics for a rich user experience.</li>
<li><strong>Real-Time Web Search & Scraping</strong>: Integrates real-time web search and webpage scraping to provide up-to-date travel information.</li>
<li><strong>Budget Analysis</strong>: Provides realistic cost breakdowns including accommodation, food, activities, transportation, and miscellaneous expenses.</li>
<li><strong>Pro Tips & Justifications</strong>: Includes actionable traveler tips and explanations for each recommendation.</li>
<li><strong>Multiple Export Formats</strong>: Export itineraries as JSON or readable text files.</li>
<li><strong>Save Favorite Destinations</strong>: Quickly save and select favorite destinations for faster itinerary generation.</li>
<li><strong>Flexible AI Model Selection</strong>: Choose between fast and capable AI models for itinerary generation.</li>
</ul>

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- API keys for OpenAI and optionally Brave Search (for enhanced search results)

### Installation

```bash
git clone https://github.com/yourusername/ai-travel-planner-v7.git
cd ai-travel-planner-v7
pip install -r requirements.txt
```

### Configuration

Create a `.streamlit/secrets.toml` file in your project directory and add your API keys:

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

<ul>
<li>Enter your origin and destination cities with helpful location suggestions.</li>
<li>Select trip dates, budget, interests, and trip pace.</li>
<li>Choose the AI model for itinerary generation.</li>
<li>Generate a personalized travel itinerary with detailed daily plans, budget analysis, essential info, and alternative options.</li>
<li>Save favorite destinations for quick access in future sessions.</li>
<li>Export your itinerary as JSON or text files.</li>
</ul>

---

## Project Structure

<ul>
<li><code>app.py</code>: Main application file containing UI, AI integration, and business logic.</li>
<li><code>.streamlit/secrets.toml</code>: Configuration file for API keys (not included in repo).</li>
<li><code>requirements.txt</code>: Python dependencies.</li>
</ul>

---

## Technologies Used

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue" alt="Python Version" />
  <img src="https://img.shields.io/badge/Streamlit-1.35.0-green" alt="Streamlit Version" />
  <img src="https://img.shields.io/badge/OpenAI-1.30.0-blue" alt="OpenAI Version" />
  <img src="https://img.shields.io/badge/HTTPX-0.27.0-lightgrey" alt="HTTPX Version" />
  <img src="https://img.shields.io/badge/BeautifulSoup-4.12.3-orange" alt="BeautifulSoup Version" />
  <img src="https://img.shields.io/badge/DuckDuckGo-6.1.4-yellow" alt="DuckDuckGo Version" />
  <img src="https://img.shields.io/badge/DiskCache-5.6.3-red" alt="DiskCache Version" />
  <img src="https://img.shields.io/badge/Geopy-2.4.1-blueviolet" alt="Geopy Version" />
  <img src="https://img.shields.io/badge/Plotly-5.17.0-purple" alt="Plotly Version" />
</p>

---

## Future Improvements

<ul>
<li>Add weather forecast integration for trip dates.</li>
<li>Implement packing checklist generator based on destination and weather.</li>
<li>Include local events and currency converter widgets.</li>
<li>Enhance UI with user authentication and persistent storage.</li>
</ul>

---

## License

This project is open source and available under the MIT License.

---

## Contact

For questions or contributions, please contact [Your Name] at [your.email@example.com].

---

## Demo Video

_Add a link or embed your project demo video here to showcase the app in action._

---

*This project showcases advanced AI integration and modern UI design, making it an excellent portfolio piece for job and university applications.*
