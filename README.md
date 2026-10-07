# Gen-AI-Powered-Smart-Track-Assistant
The GenAI-Powered Smart Traffic Assistant is an AI-based travel decision-support system that helps users evaluate journey conditions before travelling. It combines traffic analysis, route information, weather conditions, road conditions, and road-safety knowledge into a single dashboard.

After submitting a trip, the dashboard fetches a driving route, distance, and estimated duration from the public OSRM routing service and displays the route on an OpenStreetMap map. An internet connection is required. This provides current road-route geometry, not live traffic conditions or incident data.

The source, destination, and weather selectors include 34 distinct capital locations representing all 28 Indian states and 8 union territories (some states share a capital). This is capital-city coverage, not a list of every town. Island locations may not have a road route. Current weather for the selected weather location and destination is retrieved from Open-Meteo without an API key and cached for up to 15 minutes. Weather may represent the nearest model grid point; an internet connection is required.
