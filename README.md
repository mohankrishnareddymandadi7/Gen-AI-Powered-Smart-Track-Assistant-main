# Gen-AI-Powered-Smart-Track-Assistant

The GenAI-Powered Smart Traffic Assistant is an India-focused trip-planning dashboard. It combines route geometry, travel-time weather forecasts, optional live traffic incidents, an interactive map, and source-linked road-safety guidance. Its heuristic risk index is a planning aid, not a live traffic score or a safety guarantee.

## Run locally

Install the packages in `requirements.txt`, then run:

```powershell
streamlit run app.py
```

An internet connection is needed for routing, weather, map tiles, and optional incident data.

## Routes and district locations

The source, destination, and weather selectors include a bundled snapshot of 784 district entries across all 28 states and 8 union territories. The district list is based on the Government of India [IGOD directory](https://igod.gov.in/sg/district/states), via the [published dataset and scraper](https://github.com/KTBsomen/Indian-state-district-json). Names and administrative boundaries can change; verify the list against the official directory when accuracy is time-sensitive.

`data/india_district_coordinates.json` bundles 617 approximate representative points from geoBoundaries India ADM2 polygons. The source boundaries represent 2021, were updated in January 2023, and are distributed under the [Open Data Commons Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/). The source is Pathways Data Pvt. Ltd. / lgdirectory.gov.in, distributed by [geoBoundaries](https://www.geoboundaries.org); the source commit and data-method notes are recorded in the JSON file. This database has attribution and share-alike requirements; retain this provenance and review the ODbL before redistributing derived data. Coordinates are polygon representative points, not necessarily district headquarters, road access points, or exact current boundaries.

The geoBoundaries snapshot does not match 167 entries in the newer district selector; those locations continue to use state-checked [OpenStreetMap Nominatim](https://nominatim.openstreetmap.org/) lookup, cached for 30 days. Nominatim requests identify the application and are limited to at most one per second; its [usage policy](https://operations.osmfoundation.org/policies/nominatim/) applies. Existing capital coordinates remain as a fallback. Unmatched districts may still fail if the lookup provider has no reliable match. Routes and driving distance come from OSRM; island districts may not have a road route.

## Weather forecasts

Current observations and hourly forecasts are retrieved from [Open-Meteo](https://open-meteo.com/) without an API key and cached for up to 15 minutes. The app requests up to the provider's 16-day forecast horizon and selects the nearest available hourly forecast on the chosen departure date/time. It also estimates an arrival time from the OSRM duration and requests destination weather for that time. If either requested time is outside the data returned by Open-Meteo, the dashboard and trip brief say so explicitly; current conditions are shown separately and are never substituted for an unavailable travel-date forecast. Forecasts are for the nearest model grid point, not every part of the route.

## Live traffic incidents and device location

Live route incidents use the [TomTom Traffic Incidents API v5](https://docs.tomtom.com/traffic-api/documentation/tomtom-maps/v1/traffic-incidents/incident-details), filtered to currently present incidents. Because TomTom limits each bounding box to 10,000 km², the route corridor is queried in smaller areas. Results are cached for five minutes and displayed with the provider name and retrieval time; returned incidents may be incomplete or delayed. A no-results response does not mean a route is incident-free. The heuristic risk line is visually separate and is never presented as a confirmed incident.

TomTom requires an API key. Configure it as either an environment variable or a local Streamlit secret; the key is not stored in source code:

```powershell
$env:TOMTOM_API_KEY = "your-api-key"
streamlit run app.py
```

Alternatively, create `.streamlit/secrets.toml` (ignored by git) with:

```toml
TOMTOM_API_KEY = "your-api-key"
```

Without a key, the dashboard clearly reports that live incident data is unavailable.

The map also offers an optional **Start live location** control. The browser prompts for permission; while enabled, the device marker updates on the map only. The app does not transmit or store this GPS position. Location access requires a secure browser context and permission.

## Safety guidance and trip brief

`data/safety_guidance.json` is a small curated set of driving advice with a source citation for every item. The app retrieves relevant entries by matching the selected road condition, forecast categories, traffic level, and departure time. This is deterministic, tag-based local retrieval—not a generative model or an unsupported claim of vector-search RAG.

Trip results include a Google Maps driving-directions link pre-filled with the selected district and state names, current-weather context, travel-time forecasts, selected challenges and precautions, a safety checklist, and a downloadable plain-text trip brief (`.txt`). The brief includes incident availability/results and the sources for retrieved safety guidance. The dashboard uses a light, high-contrast planning workspace, animated route illustration, and responsive three-step trip form.
