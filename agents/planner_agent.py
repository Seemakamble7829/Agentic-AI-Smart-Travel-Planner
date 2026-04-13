"""Planner Agent

Creates a multi-day itinerary and orders stops per day using a simple
nearest-neighbour heuristic. The planner is lightweight and deterministic
for demo/testing purposes.
"""
from typing import Dict, List
from datetime import datetime, timedelta
from math import ceil
from utils import get_coords, nearest_neighbor_order


class PlannerAgent:
    @staticmethod
    def _slot_time(base: datetime, day_index: int, slot_index: int) -> str:
        # each slot is 3 hours apart; day offset by 24h
        t = base + timedelta(days=day_index, hours=slot_index * 3 + 8)
        return t.strftime("%Y-%m-%d %H:%M")

    @classmethod
    def run(cls, input_data: Dict) -> Dict:
        # input_data should include: destination, interests, budget, attractions (list), foods (list), weather, days
        dest = input_data.get("destination")
        interest_input = input_data.get("interests") or ""
        if isinstance(interest_input, str):
            interests = set([i.strip() for i in interest_input.split() if i.strip()])
        else:
            interests = set(interest_input)

        attractions = input_data.get("attractions") or []
        foods = input_data.get("foods") or []
        budget = float(input_data.get("budget") or 0)
        weather = input_data.get("weather") or {}
        days = int(input_data.get("days") or 1)

        reasoning: List[str] = []

        # 1) Score attractions by interest relevance and basic heuristics
        scored: List[Dict] = []
        for a in attractions:
            score = 1
            name = (a.get("name") or "").lower()
            tags = set((a.get("tags") or []))
            desc = (a.get("description") or "").lower()
            # interest match
            if any(i.lower() in name for i in interests):
                score += 3
            if any(i.lower() in desc for i in interests):
                score += 2
            if tags & set(i.lower() for i in interests):
                score += 1
            # mark outdoor heuristics
            outdoor_kw = ["beach", "park", "garden", "fort", "promenade", "view", "hill", "outdoor"]
            outdoor = any(k in name or k in desc for k in outdoor_kw)
            scored.append({"score": score, "place": a, "outdoor": outdoor})

        # Sort by score desc
        scored.sort(key=lambda x: x["score"], reverse=True)

        places = [s["place"] for s in scored]

        # 2) If rainy, try to avoid outdoor places
        cond = (weather.get("condition") or "").lower()
        is_rainy = any(k in cond for k in ("rain", "shower", "storm"))
        if is_rainy:
            reasoning.append("Detected rainy weather — indoor options prioritized.")
            # prefer non-outdoor places by re-sorting: push outdoor ones to end
            non_outdoor = [s for s in scored if not s.get("outdoor")]
            outdoor = [s for s in scored if s.get("outdoor")]
            scored = non_outdoor + outdoor
            places = [s["place"] for s in scored]

        # 3) Order places globally using NN and split across days
        ordered = nearest_neighbor_order(places)
        per_day = max(1, ceil(len(ordered) / days))

        base = datetime.now()
        itinerary: List[Dict] = []

        for day_idx in range(days):
            day_slice = ordered[day_idx * per_day:(day_idx + 1) * per_day]
            day_ordered = nearest_neighbor_order(day_slice)
            for slot_idx, place in enumerate(day_ordered):
                lat, lon = get_coords(place)
                itinerary.append({
                    "day": day_idx + 1,
                    "slot": ["Morning", "Afternoon", "Evening"][slot_idx % 3],
                    "time": cls._slot_time(base, day_idx, slot_idx),
                    "name": place.get("name"),
                    "lat": lat,
                    "lon": lon,
                    "notes": place.get("description") or "",
                    "expected_cost": float(place.get("cost_estimate", 0) or 0),
                })

        # 4) Include multiple restaurants if user prioritized food
        food_pref = any("food" in i.lower() for i in interests)
        if food_pref and foods:
            reasoning.append("User expressed interest in food — adding additional restaurant recommendations.")
            # Add up to one restaurant per day, without repeats
            added = 0
            used_names = set()
            for f in foods:
                name = f.get("name")
                if name in used_names:
                    continue
                lat, lon = get_coords(f)
                itinerary.append({
                    "day": min(days, added + 1),
                    "slot": "Evening Meal",
                    "time": cls._slot_time(base, min(days - 1, added), 3),
                    "name": name,
                    "lat": lat,
                    "lon": lon,
                    "notes": f.get("description", ""),
                    "expected_cost": float(f.get("price", f.get("rating", 15) * 10) or 15),
                })
                used_names.add(name)
                added += 1
                if added >= days:
                    break

        # 5) Budget trimming: remove lowest-score / highest-cost items until within budget
        total_estimated = sum(it.get("expected_cost", 0) for it in itinerary)
        if budget and total_estimated > float(budget):
            reasoning.append(f"Initial estimated cost {total_estimated} exceeds budget {budget} — trimming activities.")
            # Try to remove items that are high cost but low in the original scored ranking
            # Build a simple priority: cost / (1 + score)
            # Map names to score
            score_map = {s["place"].get("name"): s["score"] for s in scored}
            # Sort removable items (exclude restaurant evening meals first)
            removable = [it for it in itinerary if it.get("slot") != "Evening Meal"]
            # sort by cost desc then score asc
            removable.sort(key=lambda x: (x.get("expected_cost", 0) / (1 + score_map.get(x.get("name"), 0))), reverse=True)
            # remove until under budget; keep at least one item overall
            for rem in removable:
                if total_estimated <= float(budget):
                    break
                # Allow emptying a specific day if needed, but never remove the last remaining item
                if len(itinerary) <= 1:
                    # don't remove the last item
                    continue
                itinerary.remove(rem)
                total_estimated -= rem.get("expected_cost", 0)
                reasoning.append(f"Removed {rem.get('name')} to reduce cost (saved {rem.get('expected_cost',0)}).")

        budget_ok = (not budget) or total_estimated <= float(budget)

        return {
            "itinerary": itinerary,
            "total_estimated": total_estimated,
            "budget_ok": budget_ok,
            "reasoning": reasoning,
        }
