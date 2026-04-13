"""Streamlit app for the Agentic AI Smart Travel Planner (upgraded UI & features).

This file upgrades the UI, adds an auth sidebar, an admin panel for adding
cities/places/restaurants (saved to JSON via DataLoader), improves budget
estimation, and integrates a Folium map (if available).

Run with:
    python -m streamlit run app.py
"""
from typing import List

import streamlit as st
import pandas as pd
import auth
from datetime import datetime
from pathlib import Path
import json
import re
import io

from config import APP_NAME, APP_DESCRIPTION, CURRENCY
from agents.destination_agent import DestinationAgent
from agents.food_agent import FoodAgent
from agents.weather_agent import WeatherAgent
from agents.budget_agent import BudgetAgent
from agents.itinerary_agent import ItineraryAgent
from agents.recommendation_agent import RecommendationAgent
from agents.planner_agent import PlannerAgent
from agents.route_agent import RouteAgent
from data_loader import DataLoader

# Optional map integration
try:
    import folium
    from streamlit_folium import st_folium
    FOLIUM_AVAILABLE = True
except Exception:
    FOLIUM_AVAILABLE = False


class Controller:
    """Coordinates all agents to build a complete travel plan.

    This reuses the existing agents but keeps the coordination logic here so
    higher-level features (UI, budget) remain separate.
    """

    def __init__(self):
        self.destination_agent = DestinationAgent
        self.food_agent = FoodAgent
        self.weather_agent = WeatherAgent
        self.budget_agent = BudgetAgent
        self.itinerary_agent = ItineraryAgent

    def build_plan(self, destination: str, days: int, budget: int, interests: str) -> dict:
        # 1) Get recommendations (attractions + foods)
        recs = RecommendationAgent.run({"destination": destination, "interests": interests})

        # 2) Weather signal (use run() for agentic interface)
        weather = self.weather_agent.run({"destination": destination})

        # 3) Planner composes a time-slotted itinerary using recs + weather + budget
        planner_input = {
            "destination": destination,
            "interests": interests,
            "budget": budget,
            "days": days,
            "attractions": recs.get("attractions", []),
            "foods": recs.get("foods", []),
            "weather": weather,
        }
        planner_out = PlannerAgent.run(planner_input)

        # 4) Routing between planned stops
        route_out = RouteAgent.run({"itinerary": planner_out.get("itinerary", [])})
        # Evaluate budget against produced itinerary
        budget_eval = self.budget_agent.run({
            "destination": destination,
            "days": days,
            "itinerary": planner_out.get("itinerary", []),
            "budget": budget,
        })

        # Keep original rough estimate for comparison
        budget_estimate = self.budget_agent.estimate(destination, days)

        return {
            "destination": destination,
            "days": days,
            "interests": interests,
            "attractions": recs.get("attractions", []),
            "food_places": recs.get("foods", []),
            "weather": weather,
            "budget_estimate": budget_estimate,
            "budget_eval": budget_eval,
            "itinerary": planner_out.get("itinerary", []),
            "planner": planner_out,
            "route": route_out,
            "requested_budget": budget,
        }


def _local_css() -> None:
    st.markdown(
        """
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
        <style>
        :root{
          --bg-0: #0f172a;
          --bg-1: linear-gradient(135deg,#0ea5e9 0%, #7c3aed 100%);
          --card-bg: rgba(255,255,255,0.98);
          --muted: #6b7280;
          --shadow-lg: 0 12px 40px rgba(2,6,23,0.12);
        }
        *{font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;}
        html, body, [data-testid='stAppViewContainer'] > div:first-child {
          background: radial-gradient(1200px 600px at 10% 10%, rgba(124,58,237,0.12), transparent 10%), radial-gradient(1000px 400px at 90% 90%, rgba(6,182,212,0.08), transparent 10%), #f6f9fc;
        }
        .stApp { color: #0b1220; }
        .card { background: var(--card-bg); border-radius: 16px; padding: 18px; box-shadow: var(--shadow-lg); }
        .hero { padding: 26px; border-radius: 16px; color: white; background: var(--bg-1); box-shadow: var(--shadow-lg); }
        .app-title { font-size: 34px; font-weight:800; margin:0; line-height:1.05 }
        .app-sub { font-size:14px; color: rgba(255,255,255,0.92); margin-top:6px }
        .muted { color: var(--muted); }
        .result-title { font-size:16px; font-weight:700; margin-bottom:8px; }
        .btn-primary { background: linear-gradient(90deg,#06b6d4,#7c3aed); color: white; padding:8px 18px; border-radius: 12px; border: none; box-shadow:0 6px 18px rgba(99,102,241,0.18); }
        .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div>select, .stTextArea>div>div>textarea { border-radius:10px; padding:10px; border:1px solid #e6eef6; }
        .card-grid { display:grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
        @media (max-width: 900px) { .card-grid { grid-template-columns: 1fr; } .app-title { font-size:28px } }
        pre { background:transparent; border-left:4px solid rgba(124,58,237,0.18); padding:8px 12px; border-radius:6px }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(page_title=APP_NAME, layout="wide")
    _local_css()

    # Sidebar: use auth helper for login (keeps behavior consistent)
    user = auth.login_sidebar() or st.session_state.get("user", "Guest")

    # Initialize persistent session keys (used to keep results across reruns)
    st.session_state.setdefault("travel_plan", None)
    st.session_state.setdefault("last_generated", None)

    # Header / Hero
    st.markdown(
        f"""
        <div class='hero'>
          <div style='display:flex;align-items:center;justify-content:space-between'>
            <div>
              <h1 class='app-title'>🧭 {APP_NAME}</h1>
              <div class='app-sub'>{APP_DESCRIPTION}</div>
            </div>
                        <div style='text-align:right'>
                            <div style='background:rgba(255,255,255,0.12);padding:8px 12px;border-radius:12px;font-weight:600'>Welcome, {st.session_state.get('user','Guest')}</div>
                        </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    controller = Controller()

    # Chat / natural language quick input. We parse simple phrases like
    # "3 day food trip to Goa with 5000 budget" and prefill the form.
    st.session_state.setdefault("parsed_destination", None)
    st.session_state.setdefault("parsed_days", None)
    st.session_state.setdefault("parsed_budget", None)
    st.session_state.setdefault("parsed_interests", None)

    def parse_chat_input(text: str):
        if not text:
            return
        dests = list((DataLoader.load_destinations() or {}).keys())
        text_l = text.lower()
        # days
        m = re.search(r"(\d+)\s*(?:day|days)\b", text_l)
        if m:
            st.session_state["parsed_days"] = int(m.group(1))

        # budget (₹ or digits)
        m2 = re.search(r"(?:₹|rs\.?|inr)?\s*([0-9,]{3,})", text_l)
        if m2:
            b = m2.group(1).replace(",", "")
            try:
                st.session_state["parsed_budget"] = int(b)
            except Exception:
                pass

        # destination: match any known city name
        for d in dests:
            if d.lower() in text_l:
                st.session_state["parsed_destination"] = d
                break

        # interests: simple keyword extraction
        keywords = ["food", "history", "beach", "hiking", "nature", "temple", "shopping", "culture", "relax", "adventure"]
        found = [k for k in keywords if k in text_l]
        if found:
            st.session_state["parsed_interests"] = " ".join(found)

    chat_text = st.chat_input("Describe your trip in plain language (optional)")
    if chat_text:
        parse_chat_input(chat_text)

    # Admin panel (only visible to admin user)
    if user == "admin":
        st.sidebar.markdown("### ⚙️ Admin Panel")
        with st.sidebar.expander("Add a new city"):
            new_city = st.text_input("City name (title case)", key="new_city_admin")
            if st.button("Add city", key="btn_add_city") and new_city:
                ok = DataLoader.add_city(new_city)
                if ok:
                    st.sidebar.success(f"City '{new_city}' added")
                else:
                    st.sidebar.error("City exists or error saving")

        with st.sidebar.expander("Add attraction / place"):
            city_for_place = st.text_input("City for place", key="city_for_place_admin")
            place_name = st.text_input("Place name", key="place_name_admin")
            place_lat = st.text_input("Latitude (optional)", key="place_lat_admin")
            place_lng = st.text_input("Longitude (optional)", key="place_lng_admin")
            place_desc = st.text_area("Short description", key="place_desc_admin")
            if st.button("Add place", key="btn_add_place") and city_for_place and place_name:
                try:
                    place = {"name": place_name}
                    if place_lat:
                        place["lat"] = float(place_lat)
                    if place_lng:
                        place["lng"] = float(place_lng)
                    place["description"] = place_desc
                    ok = DataLoader.add_place(city_for_place, place)
                    if ok:
                        st.sidebar.success(f"Added place '{place_name}' to {city_for_place}")
                    else:
                        st.sidebar.error("Failed to save place")
                except ValueError:
                    st.sidebar.error("Latitude/Longitude must be numeric")

        with st.sidebar.expander("Add restaurant / food"):
            city_for_food = st.text_input("City for food", key="city_for_food_admin")
            food_name = st.text_input("Food place name", key="food_name_admin")
            cuisine = st.text_input("Cuisine", key="cuisine_admin")
            rating = st.number_input("Rating", min_value=0.0, max_value=5.0, value=4.0, key="rating_admin")
            if st.button("Add food", key="btn_add_food") and city_for_food and food_name:
                food = {"name": food_name, "cuisine": cuisine, "rating": float(rating)}
                ok = DataLoader.add_food(city_for_food, food)
                if ok:
                    st.sidebar.success(f"Added food '{food_name}' to {city_for_food}")
                else:
                    st.sidebar.error("Failed to save food")

    # Main input panel inside a form so the app only runs when user submits
    with st.container():
        with st.form("travel_form"):
            left, right = st.columns([2, 1])
            with left:
                dest_data = DataLoader.load_destinations()
                supported = sorted(list(dest_data.keys())) if dest_data else ["Mysore", "Goa", "Bangalore", "Delhi", "Jaipur", "Ooty"]
                # If chat parsing found a destination, preselect it
                parsed_dest = st.session_state.get("parsed_destination")
                try:
                    default_index = supported.index(parsed_dest) if parsed_dest in supported else 0
                except Exception:
                    default_index = 0
                destination = st.selectbox("Destination", options=supported, index=default_index)
                days_default = st.session_state.get("parsed_days") or 2
                days = st.slider("Number of travel days", min_value=1, max_value=30, value=int(days_default))
                budget_default = st.session_state.get("parsed_budget") or 5000
                budget_input = st.number_input("Budget (INR)", min_value=500, value=int(budget_default), step=500)
                interests_default = st.session_state.get("parsed_interests") or "history food"
                interests = st.text_input("Travel interests (comma separated)", value=interests_default)

            with right:
                st.markdown("""
                <div class='card'>
                <div class='result-title'>Quick tips</div>
                <ul class='muted'>
                <li>Try different interests to change suggestions</li>
                <li>Adjust number of days or budget for different itineraries</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)

            submit = st.form_submit_button("Generate travel plan")

            if submit:
                # Build plan and persist in session_state so it survives reruns
                with st.spinner("Generating your travel plan..."):
                    result = Controller().build_plan(destination, int(days), int(budget_input), interests)
                    st.session_state["travel_plan"] = result
                    st.session_state["last_generated"] = destination

                    # Write a small debug log to logs/actions.log so the user can
                    # paste it if the UI behaves unexpectedly. This helps capture
                    # runtime details even when terminal access is inconvenient.
                    try:
                        logs_dir = Path(__file__).resolve().parent / "logs"
                        logs_dir.mkdir(parents=True, exist_ok=True)
                        log_file = logs_dir / "actions.log"
                        entry = {
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                            "user": st.session_state.get("user"),
                            "destination": destination,
                            "days": days,
                            "budget_input": budget_input,
                            "interests": interests,
                            "result_keys": list(result.keys()) if isinstance(result, dict) else None,
                        }
                        with open(log_file, "a", encoding="utf-8") as f:
                            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                    except Exception:
                        # Don't break the app for logging failures
                        pass

    # Render results from session_state (persistent until next generate)
    plan = st.session_state.get("travel_plan")
    if not plan:
        st.info("Generate a travel plan using the form above.")
        # Footer
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='muted'>This demo is modular and beginner-friendly.</div>", unsafe_allow_html=True)
        return

    result = plan

    # Top row: Weather / Attractions / Food
    cols = st.columns([1, 1, 1])
    with cols[0]:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='result-title'>Weather</div>", unsafe_allow_html=True)
        w = result["weather"]
        st.markdown(f"**{w.get('condition','-')}**, {w.get('temperature_c','-')}°C")
        st.markdown("</div>", unsafe_allow_html=True)

    with cols[1]:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='result-title'>Top Attractions</div>", unsafe_allow_html=True)
        # Prefer rich dataset entry if present
        rich_places = DataLoader.load_destinations() or {}
        key = (result.get("destination") or "").title()
        items = rich_places.get(key, [])
        if items:
            for it in items:
                if isinstance(it, dict):
                    name = it.get("name", "")
                    desc = it.get("description", "")
                    rating = it.get("rating")
                    rating_text = f" — ⭐ {rating}" if rating else ""
                    st.markdown(f"<div style='margin-bottom:10px'><b>{name}</b>{rating_text}<div class='muted'>{desc}</div></div>", unsafe_allow_html=True)
                else:
                    st.write(f"- {it}")
        else:
            # Fall back to recommendation results
            for a in result.get("attractions", []):
                if isinstance(a, dict):
                    st.markdown(f"<div style='margin-bottom:10px'><b>{a.get('name')}</b><div class='muted'>{a.get('description','')}</div></div>", unsafe_allow_html=True)
                else:
                    st.write(f"- {a}")
        st.markdown("</div>", unsafe_allow_html=True)

    with cols[2]:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='result-title'>Food Recommendations</div>", unsafe_allow_html=True)
        # Prefer recommendation results (these are already deduped)
        foods = result.get("food_places", [])
        if foods:
            for fd in foods:
                if isinstance(fd, dict):
                    name = fd.get("name", "")
                    cuisine = fd.get("cuisine", "")
                    rating = fd.get("rating")
                    desc = fd.get("description", "")
                    rating_text = f" — ⭐ {rating}" if rating else ""
                    cuisine_text = f"<span class='muted'>{cuisine}</span>" if cuisine else ""
                    st.markdown(f"<div style='margin-bottom:10px'><b>{name}</b> {rating_text}<div>{cuisine_text}</div><div class='muted'>{desc}</div></div>", unsafe_allow_html=True)
                else:
                    st.write(f"- {fd}")
        else:
            # fallback to data file
            rich_foods = DataLoader.load_foods() or {}
            foods2 = rich_foods.get(key, [])
            for fd in foods2:
                if isinstance(fd, dict):
                    st.markdown(f"<div style='margin-bottom:10px'><b>{fd.get('name')}</b><div class='muted'>{fd.get('description','')}</div></div>", unsafe_allow_html=True)
                else:
                    st.write(f"- {fd}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Itinerary and budget
    left_col, right_col = st.columns([2, 1])
    with left_col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='result-title'>Travel Itinerary</div>", unsafe_allow_html=True)
        for d in result["itinerary"]:
            st.markdown(f"<pre style='font-family:inherit'>{d}</pre>", unsafe_allow_html=True)

        # Planner reasoning / AI explanation
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='result-title'>Why these choices?</div>", unsafe_allow_html=True)
        reasoning = result.get("planner", {}).get("reasoning", [])
        if reasoning:
            for r in reasoning:
                st.write(f"• {r}")
        else:
            st.write("Standard recommendations based on interests and availability.")

        # Provide download buttons for the generated plan
        try:
            json_bytes = json.dumps(result, ensure_ascii=False, indent=2).encode("utf-8")
            st.download_button("Download plan (JSON)", data=json_bytes, file_name=f"plan_{result.get('destination','plan')}.json", mime="application/json")

            # Plain-text summary
            lines = []
            lines.append(f"Trip plan for {result.get('destination')}")
            lines.append("")
            for item in result.get("itinerary", []):
                day = item.get("day")
                time = item.get("time")
                name = item.get("name")
                lines.append(f"Day {day} {time} - {name}")
            text_bytes = "\n".join(lines).encode("utf-8")
            st.download_button("Download plan (text)", data=text_bytes, file_name=f"plan_{result.get('destination','plan')}.txt", mime="text/plain")
        except Exception:
            # don't break UI for download failures
            pass
        st.markdown("</div>", unsafe_allow_html=True)

        # Map (folium) - show planner itinerary markers + restaurants
        if FOLIUM_AVAILABLE:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<div class='result-title'>Map - Selected Places</div>", unsafe_allow_html=True)
            markers = []
            center = [20.5937, 78.9629]

            # Add planner itinerary markers
            for item in result.get("itinerary", []):
                lat = item.get("lat")
                lon = item.get("lon") or item.get("lng")
                if lat is None or lon is None:
                    # fallback to rich dataset
                    rich = DataLoader.load_destinations() or {}
                    for city, places in rich.items():
                        for p in places:
                            if isinstance(p, dict) and p.get("name") == item.get("name"):
                                lat = lat or p.get("lat")
                                lon = lon or p.get("lon") or p.get("lng")
                if lat is not None and lon is not None:
                    markers.append((item.get("name"), float(lat), float(lon), item.get("notes", ""), item.get("day"), item.get("slot")))

            # Add restaurant markers (ensure no duplicates)
            seen = set(m[0] for m in markers)
            for fd in result.get("food_places", []):
                name = fd.get("name") if isinstance(fd, dict) else str(fd)
                if name in seen:
                    continue
                lat = fd.get("lat")
                lon = fd.get("lon") or fd.get("lng")
                if lat is None or lon is None:
                    # try data file lookup
                    rich_foods = DataLoader.load_foods() or {}
                    for city, places in rich_foods.items():
                        for p in places:
                            if isinstance(p, dict) and p.get("name") == name:
                                lat = lat or p.get("lat")
                                lon = lon or p.get("lon") or p.get("lng")
                if lat is not None and lon is not None:
                    markers.append((name, float(lat), float(lon), fd.get("description", ""), None, "Restaurant"))
                    seen.add(name)

            if markers:
                center = [markers[0][1], markers[0][2]]
                m = folium.Map(location=center, zoom_start=12)

                # draw markers and collect per-day polylines
                coords_by_day = {}
                for name, lat, lon, desc, day, slot in markers:
                    popup = f"<b>{name}</b><br>{desc}<br><i>{slot}</i>"
                    folium.Marker(location=[lat, lon], popup=popup).add_to(m)
                    if day is not None:
                        coords_by_day.setdefault(day, []).append([lat, lon])

                # draw polylines per day
                for day, coords in coords_by_day.items():
                    if len(coords) > 1:
                        folium.PolyLine(locations=coords, color="blue", weight=3, opacity=0.6).add_to(m)

                st_folium(m, width=700, height=400)
            else:
                st.info("No geocoded attractions available for this destination to show on the map.")

            st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<div class='result-title'>Estimated Budget</div>", unsafe_allow_html=True)
        be = result.get("budget_estimate") or {}
        st.write(f"Hotel: {CURRENCY}{be.get('hotel','-')}")
        st.write(f"Food: {CURRENCY}{be.get('food','-')}")
        st.write(f"Transport: {CURRENCY}{be.get('transport','-')}")
        st.write(f"Activities: {CURRENCY}{be.get('activities','-')}")
        st.markdown(f"**Rough total estimate: {CURRENCY}{be.get('total','-')}**")

        # Show agent budget evaluation (includes itinerary costs)
        budget_eval = result.get('budget_eval') or {}
        breakdown = budget_eval.get('breakdown') or {}
        if breakdown:
            st.markdown("<hr>", unsafe_allow_html=True)
            # Budget heading with a compact info icon and native tooltip
            st.markdown(
                "<div style='display:flex;align-items:center;gap:8px'>"
                "<div class='result-title' style='margin:0;padding:0'>Budget (detailed)</div>"
                "<div title='AI-driven breakdown: shows hotel, food, transport and activities estimates. Highlights when requested budget is exceeded.' "
                "style='font-size:14px;color:#6b7280;cursor:help'>ℹ️</div>"
                "</div>",
                unsafe_allow_html=True,
            )
            # show breakdown items
            for k in ("hotel", "food", "transport", "activities", "total"):
                if k in breakdown:
                    st.write(f"{k.title()}: {CURRENCY}{breakdown[k]}")

            # Warning if exceeded
            requested = result.get('requested_budget')
            if requested and not budget_eval.get('budget_ok', True):
                over = int(breakdown.get('total', 0) - int(requested))
                st.error(f"⚠️ Budget exceeded by {CURRENCY}{over}. Consider reducing activities or increasing budget.")
            else:
                if requested:
                    st.success(f"✅ Within requested budget ({CURRENCY}{requested})")

        # Budget bar chart
        try:
            chart_df = pd.DataFrame.from_dict(be, orient='index', columns=['amount'])
            st.bar_chart(chart_df)
        except Exception:
            # Fallback: simple key/value listing
            for k, v in be.items():
                st.write(f"{k}: {v}")

        st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>This demo is modular and beginner-friendly.</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
