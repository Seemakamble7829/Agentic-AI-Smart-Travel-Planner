"""Configuration and helpers for the Agentic Travel Planner project."""
import os
from dotenv import load_dotenv


load_dotenv()

# Currency symbol used in the demo
CURRENCY = os.getenv("CURRENCY", "₹")

# App metadata
APP_NAME = "Agentic AI Smart Travel Planner"
APP_DESCRIPTION = "Generate personalized travel plans using modular AI agents (demo)."
