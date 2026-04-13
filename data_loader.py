"""Simple dataset loader for JSON/CSV datasets used by agents.

This loader reads from the `data/` folder in the project root. Agents will try
to use these datasets first and fall back to built-in dictionaries if the
files aren't present.
"""
from pathlib import Path
import json
from typing import Dict


class DataLoader:
    ROOT = Path(__file__).resolve().parent
    DATA_DIR = ROOT / "data"

    @classmethod
    def load_json(cls, name: str) -> Dict:
        path = cls.DATA_DIR / f"{name}.json"
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    @staticmethod
    def _normalize_places(data: Dict[str, list]) -> Dict[str, list]:
        """Return a copy of destinations/foods data where each place dict has
        normalized 'lat' and 'lon' keys (floats). Converts 'lng' -> 'lon'.
        """
        if not data:
            return {}
        out = {}
        for city, places in data.items():
            out_places = []
            for p in places:
                if not isinstance(p, dict):
                    out_places.append(p)
                    continue
                np = dict(p)
                # normalize latitude
                lat = np.get("lat")
                if lat is not None:
                    try:
                        np["lat"] = float(lat)
                    except Exception:
                        np["lat"] = None
                # normalize longitude: accept 'lon' or 'lng'
                lon = np.get("lon") if np.get("lon") is not None else np.get("lng")
                if lon is not None:
                    try:
                        np["lon"] = float(lon)
                    except Exception:
                        np["lon"] = None
                # ensure no lingering 'lng' to avoid confusion
                if "lng" in np and "lon" in np:
                    # prefer lon, remove lng
                    np.pop("lng", None)
                out_places.append(np)
            out[city] = out_places
        return out

    @classmethod
    def load_destinations(cls) -> Dict[str, list]:
        return cls._normalize_places(cls.load_json("destinations"))

    @classmethod
    def load_foods(cls) -> Dict[str, list]:
        return cls._normalize_places(cls.load_json("food"))

    @classmethod
    def save_json(cls, name: str, data: Dict) -> bool:
        """Save a JSON file under the data directory. Returns True on success."""
        path = cls.DATA_DIR / f"{name}.json"
        try:
            # Ensure data dir exists
            cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    @classmethod
    def save_destinations(cls, data: Dict) -> bool:
        return cls.save_json("destinations", data)

    @classmethod
    def save_foods(cls, data: Dict) -> bool:
        return cls.save_json("food", data)

    @classmethod
    def add_city(cls, city: str) -> bool:
        city = city.strip().title()
        data = cls.load_destinations()
        if city in data:
            return False
        data[city] = []
        return cls.save_destinations(data)

    @classmethod
    def add_place(cls, city: str, place: Dict) -> bool:
        city = city.strip().title()
        data = cls.load_destinations()
        if city not in data:
            data[city] = []
        data[city].append(place)
        return cls.save_destinations(data)

    @classmethod
    def add_food(cls, city: str, food: Dict) -> bool:
        city = city.strip().title()
        data = cls.load_foods()
        if city not in data:
            data[city] = []
        data[city].append(food)
        return cls.save_foods(data)


if __name__ == "__main__":
    print(DataLoader.load_destinations())
