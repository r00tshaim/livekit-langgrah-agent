"""
Real Estate Marketing Voice Agent

A LangGraph-powered voice agent for real estate outreach,
helping clients discover and schedule visits to properties in Ahmedabad and Himmatnagar, Gujarat.
"""

from agent.graph import build_graph
from agent.tools import (
    search_properties,
    schedule_visit,
    get_property_highlights,
    ask_property_preference,
    get_area_info,
)
from agent.property_data import get_vectorstore, search_properties_by_query, PROPERTIES

__all__ = [
    "build_graph",
    "search_properties",
    "schedule_visit",
    "get_property_highlights",
    "ask_property_preference",
    "get_area_info",
    "get_vectorstore",
    "search_properties_by_query",
    "PROPERTIES",
]
