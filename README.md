# Agentic AI Smart Travel Planner

This repository contains the Agentic AI Smart Travel Planner — a Streamlit app with modular agents (recommendation, planner, weather, routing, budget) plus scripts that generate smoke outputs (map HTML and a sample plan JSON) saved under `logs/`.

This project includes a GitHub Actions workflow that will deploy the contents of `logs/` to GitHub Pages (served from the `docs/` folder) when you push to `main`/`master`.

Steps to push to GitHub and deploy:

1. Create a new empty repository on GitHub (via the website).

2. Locally, add a remote and push (replace <your-remote-url>):

```powershell
git remote add origin <your-remote-url>
git branch -M main
git push -u origin main
```

3. Once pushed, GitHub Actions will run the `deploy_pages.yml` workflow and copy anything in `logs/` into `docs/`, then publish it via GitHub Pages.

Notes and tips
- If you want the full Streamlit app to be hosted, consider deploying to Streamlit Community Cloud (https://share.streamlit.io/) or to a platform like Render / Heroku. Streamlit Community Cloud connects to your GitHub repo and will run the app directly.
- The workflow above publishes static files (e.g., `logs/map_smoke_Goa.html`, `logs/smoke_plan_Goa.json`). If you want dynamic hosting for the app itself, choose Streamlit Cloud and point it to this repository.
- The repository's `requirements.txt` lists common dependencies. GitHub Pages only hosts static files; Pages won't run Streamlit.

If you'd like, I can:

- Create the remote and push for you (you will need to provide the repository URL or grant access token), or
- Prepare a separate GitHub Actions workflow to auto-deploy the Streamlit app to a chosen host (Render, Heroku) if you want an automated app deployment.
# Agentic AI Smart Travel Planner

> A beginner-friendly but production-structured demo travel planner that uses modular agents to generate personalized travel plans. Built with Python and Streamlit.

## Project overview

This project demonstrates an "agentic" architecture: small focused agents (Destination, Food, Weather, Budget and Itinerary) are coordinated by a Controller to produce a user-friendly travel plan.

Note: The in-app admin/editor UI was removed in this build. To edit or extend the demo dataset, update the JSON files under `data/` (for example `data/destinations.json` and `data/food.json`) or use the helper functions in `data_loader.py` from a separate script or REPL.

Features:
- Enter destination, number of days, budget and interests
- Weather (simulated or live via OpenWeather)
- Top attractions and food recommendations (demo dataset)
- Estimated budget breakdown (hotel, food, transport, activities)
- Day-by-day travel itinerary
- Modern Streamlit UI with custom styling

## Architecture

- agents/
  - destination_agent.py — returns attractions for supported cities
  - food_agent.py — returns food recommendations
  - weather_agent.py — fetches or simulates weather
  - budget_agent.py — estimates costs
  - itinerary_agent.py — creates day-by-day plans
- app.py — Streamlit app + Controller that coordinates agents
- config.py — small configuration and dotenv loader
- requirements.txt — Python dependencies

## Technologies used

- Python 3.8+
- Streamlit
- requests
- python-dotenv

## Installation

1. Clone or download this repository into a folder. The project root contains `app.py`.
2. (Recommended) Create and activate a virtual environment:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. (Optional) For live weather, create a `.env` file in the project root and add:

```
OPENWEATHER_API_KEY=your_openweather_api_key
```

Optional: Map support

The app can display attraction markers on a map when the optional map libraries are installed. If you want map visualization, install these packages in your environment:

```powershell
pip install folium streamlit-folium
```

When installed, maps will automatically render for destinations that include latitude/longitude in the `data/` JSON files. Maps are optional — the app runs fine without them.

## How to run (VS Code / PowerShell)

1. Open the project folder in VS Code.
2. Open a PowerShell terminal.
3. (Optional) Activate your virtual environment as shown above.
4. Run Streamlit:

```powershell
streamlit run app.py
```

5. Streamlit will open a browser tab (or show a local URL) where you can use the travel planner.

## Example user flow

- Destination: Mysore
- Days: 2
- Budget: 5000
- Interests: history food

Example output (demo):

- Weather: Cloudy 24°C
- Top Attractions: Mysore Palace, Chamundi Hills, Brindavan Gardens
- Food: RRR Restaurant, Mylari Hotel
- Itinerary: Day-by-day plan with visits and lunch suggestions
- Estimated Budget: ₹4500 (sample)

## 📸 Project Screenshots

Below are curated screenshots showing the main UX surfaces of the app.

### 1. User Interface — 🖥️
Clear, conversational UI for entering trip preferences and generating a plan.

![User Interface](assets/ui.png)
*Figure: Main Streamlit interface with chat input, form controls and result cards.*

---

### 2. Map Visualization — 🗺️
Interactive Folium map showing selected attractions and per-day route polylines.

![Map Visualization](assets/map.png)
*Figure: Map view with itinerary markers and day-by-day route polylines.*

---

### 3. Budget Breakdown — 💸
AI-driven budget evaluation and visual breakdown with alerts for over-budget scenarios.

![Budget Breakdown](assets/budget.png)
*Figure: Detailed budget card with itemized costs and a bar chart for quick comparison.*

---

### 4. Travel Itinerary — 🧭
Day-by-day, time-slotted itinerary with notes, expected costs and restaurant suggestions.

![Travel Itinerary](assets/itinerary.png)
*Figure: Generated multi-day itinerary with time slots and planner reasoning.*


## Future improvements

- Integrate real attraction and restaurant APIs (Google Places / Foursquare)
- Improve budget model with real price data and multi-currency support
- Add user preferences, booking links and maps
- Add unit tests and CI pipeline

## Added features in this version

- JSON dataset loader: project now includes `data/destinations.json` and `data/food.json` and a small `data_loader.py`. Agents will prefer these datasets if present and fall back to built-in demo data. This makes it easy to extend the demo by editing the JSON files.
- JSON dataset loader: project includes `data/destinations.json` and `data/food.json` with richer fields (coordinates, short descriptions, cuisine, ratings). A `data_loader.py` reads these. Agents prefer these datasets if present and fall back to built-in demo data. The agents expose names-only lists for compatibility while the raw rich data is available in `data/` for future features.
- GitHub Actions CI: a workflow (`.github/workflows/ci.yml`) runs `pytest` on pushes and pull requests to `main`/`master`.

## License & Credits

This is a demo project intended for learning and portfolio use.
