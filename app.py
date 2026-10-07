import streamlit as st
from datetime import datetime
import json
import math
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import streamlit.components.v1 as components

st.set_page_config(page_title="GenAI Smart Traffic Assistant", page_icon="🚦", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --bg: #071825;
        --panel: #0d1f2e;
        --panel-2: #0f2236;
        --panel-3: #132a3f;
        --line: rgba(148, 163, 184, 0.22);
        --text: #edf6ff;
        --muted: #9db5d0;
        --yellow: #f5c86a;
        --green: #2ce0a6;
        --red: #ff6b6b;
        --blue: #4aa3ff;
    }
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg, #071825 0%, #061724 100%);
        color: var(--text);
        font-family: "Segoe UI", Arial, sans-serif;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-left: 1.2rem;
        padding-right: 1.2rem;
        max-width: 1200px;
    }
    .header-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 18px;
        margin: 8px 0 14px 0;
    }
    .traffic-light {
        width: 22px;
        height: 52px;
        border-radius: 12px;
        background: linear-gradient(180deg, #ff6b6b 0%, #f8d75a 34%, #3ee2a9 68%, #3ee2a9 100%);
        box-shadow: 0 0 18px rgba(76, 201, 240, 0.35);
        position: relative;
    }
    .traffic-light::before {
        content: "";
        position: absolute;
        inset: 0;
        border-radius: 12px;
        background: linear-gradient(180deg, rgba(255,255,255,0.2), rgba(255,255,255,0));
    }
    h1 {
        font-size: 3rem !important;
        font-weight: 800 !important;
        letter-spacing: -0.04em;
        margin: 0 !important;
        color: #edf6ff !important;
        text-align: center;
    }
    .subtitle {
        text-align: center;
        color: #a9bfd6;
        font-size: 1.08rem;
        margin-bottom: 1.2rem;
        font-weight: 500;
    }
    .form-panel {
        background: rgba(11, 24, 37, 0.9);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 1.2rem 1.2rem 0.9rem;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
        margin-top: 0.7rem;
    }
    .section-title {
        color: #ebf5ff;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        margin: 0 0 0.9rem 0 !important;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .section-title .icon {
        width: 12px;
        height: 12px;
        border-radius: 3px;
        background: linear-gradient(180deg, var(--blue), #5ec9ff);
        display: inline-block;
        box-shadow: 0 0 12px rgba(62, 145, 255, 0.5);
    }
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input,
    .stTimeInput > div > div > input,
    .stSelectbox > div > div > select {
        background: rgba(11, 26, 39, 0.9) !important;
        color: var(--text) !important;
        border: 1px solid rgba(120, 150, 180, 0.32) !important;
        border-radius: 10px !important;
        height: 54px !important;
        padding: 0 14px !important;
        font-size: 1.06rem !important;
    }
    .stSelectbox label,
    .stNumberInput label,
    .stTextInput label,
    .stDateInput label,
    .stTimeInput label {
        color: #d9eaf7 !important;
        font-size: 0.98rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.45rem !important;
    }
    .stButton > button {
        height: 54px;
        border-radius: 12px;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        background: linear-gradient(180deg, #1d8fe9, #0f6ecf) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 8px 18px rgba(29, 143, 233, 0.38);
    }
    .stButton > button:hover {
        filter: brightness(1.04);
    }
    .result-banner {
        margin-top: 1.2rem;
        background: rgba(92, 63, 13, 0.6);
        border: 1px solid rgba(245, 200, 106, 0.5);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        color: #f5d6a0;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.05);
    }
    .result-banner strong {
        display: inline-block;
        font-size: 0.82rem;
        letter-spacing: 0.13em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }
    .result-banner h3 {
        margin: 0;
        font-size: clamp(1.8rem, 2vw, 2.3rem);
        color: #f0d28d !important;
    }
    .result-banner p {
        margin: 0.5rem 0 0 0;
        color: #e8d7b2;
        line-height: 1.5;
    }
    .card {
        background: rgba(13, 28, 42, 0.8);
        border: 1px solid rgba(116, 145, 176, 0.22);
        border-radius: 14px;
        padding: 1rem 1.15rem 0.9rem;
        margin-top: 1rem;
        min-height: 200px;
    }
    .card h4 {
        color: #eaf6ff;
        font-size: 1.05rem;
        margin: 0 0 0.7rem 0 !important;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .card h5 {
        margin: 0 0 0.5rem 0 !important;
        color: #dfeefc;
        font-size: 0.96rem;
    }
    .badge {
        display: inline-block;
        background: rgba(24, 201, 124, 0.18);
        color: #6fe8ba;
        border: 1px solid rgba(24, 201, 124, 0.35);
        border-radius: 8px;
        padding: 0.28rem 0.6rem;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .metric {
        color: #edf5ff;
        font-size: 1.08rem;
        margin-bottom: 0.45rem;
    }
    .muted {
        color: #a7bed7;
        font-size: 0.96rem;
    }
    .knowledge-list {
        display: flex;
        flex-direction: column;
        gap: 0.9rem;
        margin-top: 0.45rem;
    }
    .knowledge-item {
        background: rgba(12, 27, 44, 0.78);
        border: 1px solid rgba(120, 150, 180, 0.22);
        border-radius: 12px;
        padding: 1rem 1.1rem;
        color: #eaf5ff;
        line-height: 1.6;
    }
    @media (max-width: 980px) {
        h1 { font-size: 2.3rem !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

CITIES = {
    "Hyderabad": {"weather": "Rain", "temp": 28.3, "feels_like": 27.3, "humidity": 78, "wind_speed": 5.14, "description": "Moderate rain"},
    "Mumbai": {"weather": "Rain", "temp": 29.9, "feels_like": 36.9, "humidity": 79, "wind_speed": 6.17, "description": "Light rain"},
    "Delhi": {"weather": "Dry", "temp": 31.2, "feels_like": 32.5, "humidity": 42, "wind_speed": 4.3, "description": "Warm and dry"},
    "Bengaluru": {"weather": "Cloudy", "temp": 24.8, "feels_like": 25.5, "humidity": 66, "wind_speed": 3.4, "description": "Cloudy skies"},
    "Chennai": {"weather": "Humid", "temp": 30.8, "feels_like": 33.1, "humidity": 74, "wind_speed": 7.1, "description": "Humid conditions"},
}

CITY_COORDINATES = {
    "Hyderabad": (78.4867, 17.3850),
    "Mumbai": (72.8777, 19.0760),
    "Delhi": (77.2090, 28.6139),
    "Bengaluru": (77.5946, 12.9716),
    "Chennai": (80.2707, 13.0827),
}


class RouteLookupError(Exception):
    pass


def get_live_route(source, destination):
    start_lon, start_lat = CITY_COORDINATES[source]
    end_lon, end_lat = CITY_COORDINATES[destination]
    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}"
        "?overview=full&geometries=geojson"
    )
    request = Request(url, headers={"User-Agent": "GenAI-Smart-Traffic-Assistant"})

    try:
        with urlopen(request, timeout=15) as response:
            route_response = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RouteLookupError(f"Unable to contact the routing service: {error}") from error

    routes = route_response.get("routes")
    if route_response.get("code") != "Ok" or not routes:
        raise RouteLookupError(
            f"The routing service could not find a driving route ({route_response.get('code', 'unknown error')})."
        )

    route = routes[0]
    coordinates = route.get("geometry", {}).get("coordinates")
    if not isinstance(coordinates, list) or len(coordinates) < 2:
        raise RouteLookupError("The routing service returned no usable route geometry.")
    if any(
        not isinstance(point, list)
        or len(point) < 2
        or not all(
            isinstance(value, (int, float)) and math.isfinite(value)
            for value in point[:2]
        )
        for point in coordinates
    ):
        raise RouteLookupError("The routing service returned invalid route coordinates.")

    return {
        "distance_km": route["distance"] / 1000,
        "duration_hours": route["duration"] / 3600,
        "coordinates": coordinates,
    }


def build_route_map(route, source, destination):
    coordinates = json.dumps(route["coordinates"], separators=(",", ":"))
    source_label = json.dumps(source)
    destination_label = json.dumps(destination)
    return f"""
        <!doctype html>
        <html>
          <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
            <style>
              html, body, #map {{ height: 100%; margin: 0; }}
              .leaflet-container {{ background: #0d1f2e; }}
            </style>
          </head>
          <body>
            <div id="map"></div>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <script>
              const coordinates = {coordinates};
              const map = L.map("map");
              L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
                maxZoom: 19,
                attribution: "&copy; OpenStreetMap contributors"
              }}).addTo(map);
              const route = L.polyline(
                coordinates.map(([longitude, latitude]) => [latitude, longitude]),
                {{ color: "#1687e8", weight: 6, opacity: 0.9 }}
              ).addTo(map);
              L.marker([coordinates[0][1], coordinates[0][0]])
                .addTo(map).bindPopup({source_label});
              L.marker([coordinates[coordinates.length - 1][1], coordinates[coordinates.length - 1][0]])
                .addTo(map).bindPopup({destination_label});
              map.fitBounds(route.getBounds(), {{ padding: [24, 24] }});
            </script>
          </body>
        </html>
    """


def build_knowledge_items():
    return [
        "In severe weather emergencies, road closures may be necessary if conditions make travel unsafe.",
        "Evacuation routes should remain clear of congestion; non-essential traffic should be diverted during emergency operations.",
        "Congestion combined with adverse weather requires increased monitoring and may require manual traffic control at key junctions."
    ]


def analyze_trip(source, destination, vehicle_count, avg_speed, traffic_density, road_condition, weather_city):
    route = get_live_route(source, destination)
    weather = CITIES.get(weather_city, CITIES["Hyderabad"])
    risk_score = 0

    if traffic_density == "High":
        risk_score += 30
    elif traffic_density == "Medium":
        risk_score += 18

    if avg_speed < 50:
        risk_score += 18
    elif avg_speed < 70:
        risk_score += 10

    if vehicle_count > 150:
        risk_score += 16
    elif vehicle_count > 80:
        risk_score += 8

    condition = road_condition.lower()
    if condition in {"rain", "wet", "fog", "flooded"}:
        risk_score += 20 if condition != "wet" else 12

    if weather["weather"].lower() in {"rain", "cloudy"}:
        risk_score += 8

    if risk_score >= 60:
        status = "Travel with caution"
        message = "Current conditions show elevated travel risk. Allow additional time, maintain a safe following distance and drive carefully."
        tone = "warning"
    elif risk_score >= 35:
        status = "Proceed with attention"
        message = "Overall route conditions are manageable, but intermittent congestion and weather changes may affect comfort and safety."
        tone = "notice"
    else:
        status = "Travel is smooth"
        message = "Roads and weather remain favorable for a steady trip. Expect smooth travel with minor delays only."
        tone = "good"

    return {
        "route": route,
        "weather": weather,
        "risk": risk_score,
        "status": status,
        "message": message,
        "tone": tone,
        "source": source,
        "destination": destination,
        "traffic_density": traffic_density,
        "road_condition": road_condition,
        "vehicle_count": vehicle_count,
        "avg_speed": avg_speed,
    }


with st.container():
    st.markdown('<div class="header-wrap"><div class="traffic-light"></div><h1>GenAI-Powered Smart Traffic Assistant</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Intelligent route, traffic, weather and road safety analysis</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="form-panel">', unsafe_allow_html=True)
        st.markdown('<div class="section-title"><span class="icon"></span>Trip Details</div>', unsafe_allow_html=True)

        with st.form("trip_form"):
            col1, col2 = st.columns(2)
            with col1:
                source = st.selectbox("Source", ["Hyderabad", "Mumbai", "Delhi", "Bengaluru", "Chennai"], index=0)
                travel_date = st.date_input("Travel Date", value=datetime(2026, 8, 24), min_value=datetime(2024, 1, 1).date(), max_value=datetime(2030, 12, 31).date())
                vehicle_count = st.number_input("Vehicle Count", min_value=10, max_value=500, value=100, step=10)
                traffic_density = st.selectbox("Traffic Density", ["Low", "Medium", "High"], index=0)
                weather_city = st.selectbox("Weather City", ["Hyderabad", "Mumbai", "Delhi", "Bengaluru", "Chennai"], index=0)

            with col2:
                destination = st.selectbox("Destination", ["Mumbai", "Hyderabad", "Delhi", "Bengaluru", "Chennai"], index=0)
                departure_time = st.time_input("Departure Time", value=datetime.strptime("08:00", "%H:%M").time())
                avg_speed = st.number_input("Average Speed (km/h)", min_value=0, max_value=200, value=80, step=5)
                road_condition = st.selectbox("Road Condition", ["Dry", "Wet", "Rain", "Fog", "Flooded"], index=0)

            submit = st.form_submit_button("Analyze My Trip", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    if submit:
        try:
            result = analyze_trip(source, destination, vehicle_count, avg_speed, traffic_density, road_condition, weather_city)
        except RouteLookupError as error:
            st.error(f"Could not load the live driving route. {error}")
            st.stop()

        status_color = {"Travel with caution": "#f5c86a", "Proceed with attention": "#f0b56d", "Travel is smooth": "#7ae0ba"}

        st.markdown(
            f"""
            <div class="result-banner">
                <strong style="color:{status_color[result['status']]};">{result['status'].upper()}</strong>
                <h3>{result['status']}</h3>
                <p>{result['message']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(
                f"""
                <div class="card">
                    <h4><span class='icon' style='background: linear-gradient(180deg, #3ad1a3, #57d3ff); width: 12px; height: 12px; border-radius: 3px; display:inline-block;'></span>Route Information</h4>
                    <div class='metric'>Source: <span class='muted'>{source}</span></div>
                    <div class='metric'>Destination: <span class='muted'>{destination}</span></div>
                    <div class='metric'>Distance: <span class='muted'>{result['route']['distance_km']:.1f} km</span></div>
                    <div class='metric'>Estimated Duration: <span class='muted'>{result['route']['duration_hours']:.1f} hours</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_b:
            st.markdown(
                f"""
                <div class="card">
                    <h4><span class='icon' style='background: linear-gradient(180deg, #4ad38d, #6ce2c5); width: 12px; height: 12px; border-radius: 3px; display:inline-block;'></span>Traffic Analysis</h4>
                    <div class='badge'>{result['traffic_density'].upper()}</div>
                    <div class='metric'>Vehicles: <span class='muted'>{result['vehicle_count']}</span></div>
                    <div class='metric'>Average Speed: <span class='muted'>{result['avg_speed']} km/h</span></div>
                    <div class='metric'>Density: <span class='muted'>{result['traffic_density']}</span></div>
                    <div class='muted'>Condition: Traffic flowing smoothly; reduced visibility/travel due to rain.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-title" style="margin-top: 1.2rem"><span class="icon"></span>Live Road Route</div>', unsafe_allow_html=True)
        st.caption("Route and distance are fetched from OpenStreetMap-based routing. Live traffic conditions are not included.")
        components.html(build_route_map(result["route"], source, destination), height=480, scrolling=False)

        col_c, col_d = st.columns(2)
        with col_c:
            st.markdown(
                f"""
                <div class="card">
                    <h4><span class='icon' style='background: linear-gradient(180deg, #5fb1ff, #7ecaff); width: 12px; height: 12px; border-radius: 3px; display:inline-block;'></span>Source Weather</h4>
                    <div class='badge'>{result['weather']['weather']}</div>
                    <div class='metric'>Location: {source}</div>
                    <div class='metric'>Description: {result['weather']['description']}</div>
                    <div class='metric'>Temperature: {result['weather']['temp']:.1f} °C</div>
                    <div class='metric'>Feels Like: {result['weather']['feels_like']:.1f} °C</div>
                    <div class='metric'>Humidity: {result['weather']['humidity']}%</div>
                    <div class='metric'>Wind Speed: {result['weather']['wind_speed']:.2f} m/s</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_d:
            st.markdown(
                f"""
                <div class="card">
                    <h4><span class='icon' style='background: linear-gradient(180deg, #5fb1ff, #7ecaff); width: 12px; height: 12px; border-radius: 3px; display:inline-block;'></span>Destination Weather</h4>
                    <div class='badge'>{CITIES.get(destination, CITIES['Mumbai'])['weather']}</div>
                    <div class='metric'>Location: {destination}</div>
                    <div class='metric'>Description: {CITIES.get(destination, CITIES['Mumbai'])['description']}</div>
                    <div class='metric'>Temperature: {CITIES.get(destination, CITIES['Mumbai'])['temp']:.1f} °C</div>
                    <div class='metric'>Feels Like: {CITIES.get(destination, CITIES['Mumbai'])['feels_like']:.1f} °C</div>
                    <div class='metric'>Humidity: {CITIES.get(destination, CITIES['Mumbai'])['humidity']}%</div>
                    <div class='metric'>Wind Speed: {CITIES.get(destination, CITIES['Mumbai'])['wind_speed']:.2f} m/s</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        col_e, col_f = st.columns(2)
        with col_e:
            st.markdown(
                f"""
                <div class="card">
                    <h4><span class='icon' style='background: linear-gradient(180deg, #ffc75f, #ffbd59); width: 12px; height: 12px; border-radius: 3px; display:inline-block;'></span>Road Condition</h4>
                    <div class='badge'>{result['road_condition']}</div>
                    <div class='muted'>Road quality remains manageable with moderate caution.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with col_f:
            st.markdown(
                """
                <div class="card">
                    <h4><span class='icon' style='background: linear-gradient(180deg, #3ad1a3, #57d3ff); width: 12px; height: 12px; border-radius: 3px; display:inline-block;'></span>AI Recommendation</h4>
                    <div class='muted'>Here is your safe and practical travel decision-support recommendation.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-title" style="margin-top: 1.2rem"><span class="icon"></span>Safety Knowledge Retrieved by RAG</div>', unsafe_allow_html=True)
        knowledge_items = build_knowledge_items()
        st.markdown('<div class="knowledge-list">', unsafe_allow_html=True)
        for item in knowledge_items:
            st.markdown(f'<div class="knowledge-item">{item}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.caption("Enter trip details and click Analyze My Trip to view the recommendation dashboard.")
