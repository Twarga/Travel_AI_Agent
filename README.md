# 🌍 Travel Planner AI Agent

## 🚀 Overview

Travel Planner AI Agent is an advanced travel itinerary generator that leverages AI and web scraping to create personalized travel plans. Built with Streamlit and powered by Together AI's DeepSeek-R1 model, this application creates detailed day-by-day itineraries with verified information on hotels, activities, restaurants, and transportation options.

## ✨ Features

- **🤖 AI-Powered Itinerary Creation**: Generate comprehensive travel plans tailored to your preferences
- **🔎 Intelligent Web Scraping**: Gather real-time information from travel websites
- **📍 OpenStreetMap Integration**: Get location links for all suggested places
- **💰 Budget Management**: Set and allocate your travel budget across different categories
- **👥 Traveler Advice**: Incorporate tips and experiences from previous travelers
- **🏨 Accommodation Preferences**: Specify hotel types, star ratings, and amenities
- **🍽️ Dining Options**: Filter restaurants by cuisine type and dining style
- **🚗 Transportation Planning**: Include local transportation options with cost estimates

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI Models**: Together AI (DeepSeek-R1)
- **Web Scraping**: Crawl4AI, DuckDuckGo Search
- **Geocoding**: GeoPy (Nominatim)
- **Web Processing**: Playwright

## 📋 Prerequisites

- **Python 3.11**
- A Together AI API key (replace the placeholder in app.py with your actual key)

## 🔧 Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/travel-planner-ai-agent.git
cd travel-planner-ai-agent
```

2. **Set up the development environment**

```bash
make setup
```

3. **Install Playwright**

```bash
source .venv/bin/activate
playwright install
```

4. **Update the Together API key**

Edit `app.py` and replace the API key placeholder with your actual Together API key.

## 🚀 Running the Application

```bash
make run
```

Navigate to the URL displayed in your terminal (typically http://localhost:8501).

## 🧰 Available Commands

| Command | Description |
|---------|-------------|
| `make setup` | Set up the development environment |
| `make run` | Run the application |
| `make check` | Run Ruff code checks |
| `make fix` | Fix auto-fixable linting issues |
| `make clean` | Clean temporary files |
| `make help` | Display all available commands |

## 💻 Usage Guide

1. **Enter travel details** in the sidebar form:
   - Destination and origin
   - Travel dates and duration
   - Budget and currency
   
2. **Customize your preferences**:
   - Travel style and interests
   - Accommodation preferences
   - Restaurant and cuisine preferences
   - Transportation options
   - Budget allocation across categories

3. **Generate your itinerary** by clicking "Generate Itinerary"

4. **View and save** your personalized day-by-day travel plan

## 🌟 Key Features Explained

### Intelligent Web Searching

The application uses targeted searches on travel websites to gather information about:
- Hotels from Booking.com
- Activities from TripAdvisor
- Restaurants from TripAdvisor
- Transportation options from Rome2Rio
- General travel advice from web searches

### OpenStreetMap Integration

All locations in the itinerary include OpenStreetMap links, making it easy to:
- Navigate to your destinations
- Understand the proximity between activities
- Plan efficient daily routes

### Budget Management

The budget feature allows you to:
- Set a total trip budget
- Allocate percentages to different categories
- Get cost estimates for each day and activity
- Enable "Budget-Conscious Mode" for more affordable suggestions

### Traveler Advice

The application scrapes and incorporates advice from previous travelers about:
- Local customs and etiquette
- Safety tips
- Best times to visit attractions
- Hidden gems and less touristy spots
- Transportation tips
- Food recommendations
- Budget-saving strategies

## 🔄 Data Flow

1. User inputs travel details and preferences
2. Application generates category-specific search queries
3. Web scraping gathers relevant information
4. Geocoding adds location data for all points of interest
5. AI model processes all data to create a personalized itinerary
6. Results are presented in a structured, day-by-day format

## 🛡️ Privacy Notice

This application performs web searches based on your travel preferences. No personal data is stored or shared with third parties.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Together AI for providing the DeepSeek-R1 model
- OpenStreetMap for location data
- Various travel websites for providing searchable content
