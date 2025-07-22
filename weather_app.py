import streamlit as st
import requests
import os
from dotenv import load_dotenv
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from streamlit_folium import folium_static
import folium
# import pyttsx3
import threading
import pandas as pd
from gtts import gTTS
from io import BytesIO

# Load environment variables
load_dotenv()
api_key = os.getenv("API_KEY")
openweather_api_key = os.getenv("OPENWEATHER_API_KEY")  


# Page configuration
st.set_page_config(
    page_title="AirAware",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Custom CSS for beautiful styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    .main {
        padding: 0rem 1rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Poppins', sans-serif;
    }
    
    .weather-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        color: white;
        text-align: center;
        transition: transform 0.3s ease;      
    }
    .weather-card:hover {
        transform: translateY(-5px);
    }
            
    
    .metric-card {
        background: linear-gradient(145deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 16px 0 rgba(31, 38, 135, 0.2);
        color: white;
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
    }
    
    .forecast-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        text-align: center;
        min-height: 150px;
    }
    
    .comparison-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
    }
    
    .suggestion-card {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.2), rgba(139, 195, 74, 0.2));
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(76, 175, 80, 0.3);
        color: white;
    }
    
    .warning-card {
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.2), rgba(255, 152, 0, 0.2));
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(244, 67, 54, 0.3);
        color: white;
    }
    
    .title-container {
        text-align: center;
        padding: 2rem 0;
        color: white;
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #fff, #f0f0f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
    }
    
    .weather-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .temperature {
        font-size: 3rem;
        font-weight: 600;
        margin: 1rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .aqi-excellent { background: linear-gradient(135deg, #4CAF50, #45a049); }
    .aqi-good { background: linear-gradient(135deg, #8BC34A, #7CB342); }
    .aqi-moderate { background: linear-gradient(135deg, #FFC107, #FF9800); }
    .aqi-unhealthy-sensitive { background: linear-gradient(135deg, #FF9800, #F57C00); }
    .aqi-unhealthy { background: linear-gradient(135deg, #F44336, #D32F2F); }
    .aqi-very-unhealthy { background: linear-gradient(135deg, #9C27B0, #7B1FA2); }
    .aqi-hazardous { background: linear-gradient(135deg, #795548, #5D4037); }
    
    .date-display {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        text-align: center;
        color: white;
        font-size: 1.1rem;
    }
    
    .voice-button {
        background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        border: none;
        border-radius: 50px;
        padding: 10px 20px;
        color: white;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    
    .voice-button:hover {
        transform: scale(1.05);
    }
</style>
""", unsafe_allow_html=True)

# Initialize TTS engine
# Updated TTS implementation
# @st.cache_resource
# def get_tts_engine():
#     try:
#         engine = pyttsx3.init()
#         engine.setProperty('rate', 150)
#         engine.setProperty('volume', 0.9)
#         return engine
#     except Exception as e:
#         st.error(f"TTS initialization failed: {e}")
#         return None

# def speak_weather(text):
#     """Speak weather information using TTS"""
#     try:
#         engine = get_tts_engine()
#         if not engine:
#             return False
            
#         # Stop any existing speech
#         engine.stop()
        
#         # Run in a thread with proper cleanup
#         def _speak():
#             try:
#                 engine.say(text)
#                 engine.runAndWait()
#             except RuntimeError:
#                 # Handle case where engine can't be reused
#                 new_engine = pyttsx3.init()
#                 new_engine.setProperty('rate', 150)
#                 new_engine.say(text)
#                 new_engine.runAndWait()
#                 new_engine.stop()
                
#         thread = threading.Thread(target=_speak)
#         thread.start()
#         return True
        
#     except Exception as e:
#         st.error(f"Voice output error: {e}")
#         return False

def speak_weather(text):
    """Speak weather information using gTTS (compatible with Streamlit Cloud)"""
    try:
        tts = gTTS(text)
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        st.audio(mp3_fp, format="audio/mp3")
        return True
    except Exception as e:
        st.error(f"Voice output error: {e}")
        return False

# Title section

st.markdown("""
<div class="title-container">        
    <h1 class="main-title">🌤️ AirAware </h1>
    <p class="subtitle">Real-time Weather, Forecasts, Comparisons & Smart Suggestions</p>
 <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; backdrop-filter: blur(10px);">
            🔊 Voice Output
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; backdrop-filter: blur(10px);">
            📅 5-Day Forecast
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; backdrop-filter: blur(10px);">
            🏙️ City Comparison
        </div>
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; backdrop-filter: blur(10px);">
            🧠 Smart Suggestions
        </div>
</div>
""", unsafe_allow_html=True)



def get_weather_icon(temperature, humidity, condition="clear"):
    """Return appropriate weather icon based on conditions"""
    if "rain" in condition.lower():
        return "🌧️"
    elif "snow" in condition.lower():
        return "❄️"
    elif "cloud" in condition.lower():
        return "☁️"
    elif temperature > 25:
        return "☀️" if humidity < 60 else "🌤️"
    elif temperature > 15:
        return "⛅" if humidity < 70 else "🌦️"
    else:
        return "❄️" if humidity < 80 else "🌧️"

def get_aqi_info(aqi_value):
    """Return AQI category and color class"""
    if aqi_value <= 50:
        return "Excellent", "aqi-excellent", "😊"
    elif aqi_value <= 100:
        return "Good", "aqi-good", "🙂"
    elif aqi_value <= 150:
        return "Moderate", "aqi-moderate", "😐"
    elif aqi_value <= 200:
        return "Unhealthy for Sensitive", "aqi-unhealthy-sensitive", "😷"
    elif aqi_value <= 300:
        return "Unhealthy", "aqi-unhealthy", "🤢"
    elif aqi_value <= 500:
        return "Very Unhealthy", "aqi-very-unhealthy", "🤢"
    else:
        return "Hazardous", "aqi-hazardous", "☠️"

def get_smart_suggestions(temperature, humidity, aqi_value, weather_condition="clear"):
    """Generate smart suggestions based on weather conditions"""
    suggestions = []
    
    # Temperature-based suggestions
    if temperature > 30:
        suggestions.append("🌡️ It's quite hot! Stay hydrated and seek shade.")
        suggestions.append("🏊‍♀️ Perfect weather for swimming or water activities!")
    elif temperature > 20:
        suggestions.append("☀️ Beautiful weather for outdoor activities!")
        suggestions.append("🚶‍♀️ Great day for a walk in the park.")
    elif temperature > 10:
        suggestions.append("🧥 Mild weather - consider wearing a light jacket.")
        suggestions.append("☕ Perfect temperature for outdoor dining.")
    else:
        suggestions.append("🧣 Bundle up! It's quite cold outside.")
        suggestions.append("🏠 Good day to stay cozy indoors.")
    
    # Humidity-based suggestions
    if humidity > 80:
        suggestions.append("💧 High humidity - you might feel sticky!")
    elif humidity < 30:
        suggestions.append("🌵 Low humidity - stay moisturized!")
    
    # AQI-based suggestions
    if aqi_value > 150:
        suggestions.append("😷 High pollution - wear a mask and limit outdoor activities.")
        suggestions.append("🏠 Consider staying indoors today.")
    elif aqi_value > 100:
        suggestions.append("⚠️ Moderate pollution - sensitive individuals should be cautious.")
    else:
        suggestions.append("🌱 Good air quality - perfect for outdoor exercise!")
    
    # Weather condition suggestions
    if "rain" in weather_condition.lower():
        suggestions.append("☔ Don't forget your umbrella!")
        suggestions.append("🏠 Great day for indoor activities.")
    elif "snow" in weather_condition.lower():
        suggestions.append("⛄ Snow day! Perfect for winter sports.")
        suggestions.append("🚗 Drive carefully - roads may be slippery.")
    
    return suggestions

@st.cache_data
def get_weather_forecast(city_name, days=5):
    """Get weather forecast using OpenWeatherMap API"""
    if not openweather_api_key:
        return None
    
    try:
        # Get coordinates first
        geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={openweather_api_key}"
        geo_response = requests.get(geocoding_url).json()
        
        if not geo_response:
            return None
        
        lat, lon = geo_response[0]['lat'], geo_response[0]['lon']
        
        # Get forecast
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={openweather_api_key}&units=metric"
        forecast_response = requests.get(forecast_url).json()
        
        if forecast_response.get('cod') != '200':
            return None
        
        # Process forecast data
        forecast_data = []
        for item in forecast_response['list'][:days*8]:  # 8 forecasts per day (3-hour intervals)
            forecast_data.append({
                'datetime': datetime.fromtimestamp(item['dt']),
                'temperature': item['main']['temp'],
                'humidity': item['main']['humidity'],
                'description': item['weather'][0]['description'],
                'icon': item['weather'][0]['icon']
            })
        
        return forecast_data
    except Exception as e:
        st.error(f"Forecast error: {e}")
        return None

def create_forecast_chart(forecast_data):
    """Create temperature forecast chart"""
    if not forecast_data:
        return None
    
    df = pd.DataFrame(forecast_data)
    df['date'] = df['datetime'].dt.strftime('%m/%d %H:%M')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['temperature'],
        mode='lines+markers',
        name='Temperature (°C)',
        line=dict(color='#FF6B6B', width=3),
        marker=dict(size=8, color='#FF6B6B')
    ))
    
    fig.update_layout(
        title='5-Day Temperature Forecast',
        xaxis_title='Date & Time',
        yaxis_title='Temperature (°C)',
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Poppins"},
        height=400
    )
    
    return fig

def display_forecast(city_name):
    """Display weather forecast"""
    st.markdown("### 📅 5-Day Weather Forecast")
    
    forecast_data = get_weather_forecast(city_name)
    
    if forecast_data:
        # Chart
        chart = create_forecast_chart(forecast_data)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        
        # Daily forecast cards
        st.markdown("#### Daily Overview")
        
        # Group by day
        daily_data = {}
        for item in forecast_data:
            day = item['datetime'].strftime('%Y-%m-%d')
            if day not in daily_data:
                daily_data[day] = []
            daily_data[day].append(item)
        
        cols = st.columns(min(5, len(daily_data)))
        
        for i, (day, day_data) in enumerate(list(daily_data.items())[:5]):
            with cols[i]:
                avg_temp = sum(item['temperature'] for item in day_data) / len(day_data)
                avg_humidity = sum(item['humidity'] for item in day_data) / len(day_data)
                main_condition = day_data[0]['description']
                
                day_name = datetime.strptime(day, '%Y-%m-%d').strftime('%a')
                day_date = datetime.strptime(day, '%Y-%m-%d').strftime('%m/%d')
                
                icon = get_weather_icon(avg_temp, avg_humidity, main_condition)
                
                st.markdown(f"""
                <div class="forecast-card">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
                    <div style="font-weight: 600; margin-bottom: 0.5rem;">{day_name}</div>
                    <div style="font-size: 0.9rem; margin-bottom: 0.5rem;">{day_date}</div>
                    <div style="font-size: 1.2rem; font-weight: 600;">{avg_temp:.1f}°C</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">{avg_humidity:.0f}% humidity</div>
                    <div style="font-size: 0.8rem; margin-top: 0.5rem;">{main_condition.title()}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Forecast data not available. Please add OPENWEATHER_API_KEY to your .env file.")

def create_temperature_gauge(temperature):
    """Create a beautiful temperature gauge"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = temperature,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Temperature (°C)", 'font': {'color': 'white', 'size': 16}},
        delta = {'reference': 20},
        gauge = {
            'axis': {'range': [None, 50], 'tickcolor': 'white'},
            'bar': {'color': "rgba(255,255,255,0.8)"},
            'steps': [
                {'range': [0, 10], 'color': "lightblue"},
                {'range': [10, 25], 'color': "lightgreen"},
                {'range': [25, 35], 'color': "yellow"},
                {'range': [35, 50], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 40
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={'color': "white", 'family': "Poppins"},
        height=300
    )
    return fig


@st.cache_data
def map_creator(latitude, longitude, city_name="Location"):
    """Create a beautiful map with custom styling"""
    m = folium.Map(
        location=[latitude, longitude], 
        zoom_start=12,
        tiles='CartoDB dark_matter'
    )
    
    # Add a custom marker
    folium.Marker(
        [latitude, longitude], 
        popup=f"📍 {city_name}",
        tooltip=f"Weather Station: {city_name}",
        icon=folium.Icon(color='red', icon='cloud', prefix='fa')
    ).add_to(m)
    
    # Add a circle around the location
    folium.Circle(
        location=[latitude, longitude],
        radius=5000,
        popup=f"5km radius around {city_name}",
        color='#ff6b6b',
        fill=True,
        fillOpacity=0.1
    ).add_to(m)
    
    folium_static(m, width=1500, height=400)

@st.cache_data
def generate_list_of_countries():
    countries_url = f"https://api.airvisual.com/v2/countries?key={api_key}"
    countries_dict = requests.get(countries_url).json()
    return countries_dict

@st.cache_data
def generate_list_of_states(country_selected):
    states_url = f"https://api.airvisual.com/v2/states?country={country_selected}&key={api_key}"
    states_dict = requests.get(states_url).json()
    return states_dict

@st.cache_data
def generate_list_of_cities(state_selected, country_selected):
    cities_url = f"https://api.airvisual.com/v2/cities?state={state_selected}&country={country_selected}&key={api_key}"
    cities_dict = requests.get(cities_url).json()
    return cities_dict

def get_weather_data_by_city(city, state, country):
    """Get weather data for a specific city"""
    aqi_data_url = f"https://api.airvisual.com/v2/city?city={city}&state={state}&country={country}&key={api_key}"
    response = requests.get(aqi_data_url).json()
    return response

def display_weather_data(aqi_data_dict, location_name):
    """Display weather data in beautiful cards"""
    data = aqi_data_dict["data"]
    weather = data["current"]["weather"]
    pollution = data["current"]["pollution"]
    
    # Date display
    st.markdown(f"""
    <div class="date-display">
        📅 Today is {date.today().strftime("%B %d, %Y")} | 🕐 {datetime.now().strftime("%H:%M")}
    </div>
    """, unsafe_allow_html=True)
    
    # Main weather card
    temperature_c = weather["tp"]
    temperature_f = round((temperature_c * 9/5) + 32, 1)
    humidity = weather["hu"]
    aqi_value = pollution["aqius"]
    
    weather_icon = get_weather_icon(temperature_c, humidity)
    aqi_category, aqi_class, aqi_emoji = get_aqi_info(aqi_value)
    
    # Voice output section
    weather_text = f"Current weather in {location_name}: Temperature is {temperature_c} degrees Celsius, humidity is {humidity} percent, and air quality index is {aqi_value} which is {aqi_category}."
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div class="weather-card">
            <div class="weather-icon">{weather_icon}</div>
            <h2 style="margin-bottom: 0.5rem;">📍 {location_name}</h2>
            <div class="temperature">{temperature_c}°C / {temperature_f}°F</div>
            <p style="font-size: 1.1rem; opacity: 0.9;">Current weather conditions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🔊 Voice Output")
        if st.button("🎤 Read Weather Aloud", key="voice_button"):
            if speak_weather(weather_text):
                st.success("🔊 Speaking weather information...")
            else:
                st.error("❌ Voice output not available")

        # st.plotly_chart(create_temperature_gauge(temperature_c), use_container_width=True)
        
        
    
    # Create columns for layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Map
        if "coordinates" in data["location"]:
            coords = data["location"]["coordinates"]
            map_creator(coords[1], coords[0], location_name)
    
    with col2:
        # Temperature gauge
        st.plotly_chart(create_temperature_gauge(temperature_c), use_container_width=True)
    
    # Metrics row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💧</div>
            <div class="metric-value">{humidity}%</div>
            <div class="metric-label">Humidity</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card {aqi_class}">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{aqi_emoji}</div>
            <div class="metric-value">{aqi_value}</div>
            <div class="metric-label">AQI - {aqi_category}</div>
        </div>
        """, unsafe_allow_html=True)
    

    # Smart Suggestions
    suggestions = get_smart_suggestions(temperature_c, humidity, aqi_value)
    
    st.markdown("### 🧠 Smart Suggestions")
    
    for i, suggestion in enumerate(suggestions[:4]):  # Show top 4 suggestions
        card_class = "suggestion-card" if aqi_value <= 100 else "warning-card"
        st.markdown(f"""
        <div class="{card_class}">
            <p style="margin: 0; font-size: 1.1rem;">{suggestion}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Weather Forecast
    city_for_forecast = location_name.split(',')[0]  # Extract city name
    display_forecast(city_for_forecast)
    
    return {
        'temperature': temperature_c,
        'humidity': humidity,
        'aqi': aqi_value,
        'location': location_name
    }

def display_city_comparison():
    """Display city comparison feature"""
    st.markdown("## 🏙️ City Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### City 1")
        countries_dict = generate_list_of_countries()
        if countries_dict["status"] == "success":
            countries_list = [""] + [i["country"] for i in countries_dict["data"]]
            country1 = st.selectbox("Country 1", options=countries_list, key="country1")
            
            if country1:
                states_response = generate_list_of_states(country1)
                if states_response["status"] == "success":
                    states_list = [""] + [i["state"] for i in states_response["data"]]
                    state1 = st.selectbox("State 1", options=states_list, key="state1")
                    
                    if state1:
                        cities_response = generate_list_of_cities(state1, country1)
                        if cities_response["status"] == "success":
                            cities_list = [""] + [i["city"] for i in cities_response["data"]]
                            city1 = st.selectbox("City 1", options=cities_list, key="city1")
    
    with col2:
        st.markdown("### City 2")
        if countries_dict["status"] == "success":
            country2 = st.selectbox("Country 2", options=countries_list, key="country2")
            
            if country2:
                states_response = generate_list_of_states(country2)
                if states_response["status"] == "success":
                    states_list = [""] + [i["state"] for i in states_response["data"]]
                    state2 = st.selectbox("State 2", options=states_list, key="state2")
                    
                    if state2:
                        cities_response = generate_list_of_cities(state2, country2)
                        if cities_response["status"] == "success":
                            cities_list = [""] + [i["city"] for i in cities_response["data"]]
                            city2 = st.selectbox("City 2", options=cities_list, key="city2")
    
    # Compare cities if both are selected
    if 'city1' in locals() and 'city2' in locals() and city1 and city2:
        if st.button("🔍 Compare Cities", type="primary"):
            col1, col2 = st.columns(2)
            
            # Get data for both cities
            try:
                data1 = get_weather_data_by_city(city1, state1, country1)
                data2 = get_weather_data_by_city(city2, state2, country2)
                
                if data1["status"] == "success" and data2["status"] == "success":
                    weather1 = data1["data"]["current"]["weather"]
                    pollution1 = data1["data"]["current"]["pollution"]
                    weather2 = data2["data"]["current"]["weather"]
                    pollution2 = data2["data"]["current"]["pollution"]
                    
                    with col1:
                        st.markdown(f"""
                        <div class="comparison-card">
                            <h3>📍 {city1}, {state1}</h3>
                            <div style="font-size: 2rem; margin: 1rem 0;">{get_weather_icon(weather1['tp'], weather1['hu'])}</div>
                            <p><strong>Temperature:</strong> {weather1['tp']}°C</p>
                            <p><strong>Humidity:</strong> {weather1['hu']}%</p>
                            <p><strong>AQI:</strong> {pollution1['aqius']} ({get_aqi_info(pollution1['aqius'])[0]})</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div class="comparison-card">
                            <h3>📍 {city2}, {state2}</h3>
                            <div style="font-size: 2rem; margin: 1rem 0;">{get_weather_icon(weather2['tp'], weather2['hu'])}</div>
                            <p><strong>Temperature:</strong> {weather2['tp']}°C</p>
                            <p><strong>Humidity:</strong> {weather2['hu']}%</p>
                            <p><strong>AQI:</strong> {pollution2['aqius']} ({get_aqi_info(pollution2['aqius'])[0]})</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Comparison chart
                    comparison_data = {
                        'City': [f"{city1}, {state1}", f"{city2}, {state2}"],
                        'Temperature (°C)': [weather1['tp'], weather2['tp']],
                        'Humidity (%)': [weather1['hu'], weather2['hu']],
                        'AQI': [pollution1['aqius'], pollution2['aqius']]
                    }
                    
                    df = pd.DataFrame(comparison_data)
                    
                    # Create comparison charts
                    fig = go.Figure()
                    
                    fig.add_trace(go.Bar(
                        name='Temperature (°C)',
                        x=df['City'],
                        y=df['Temperature (°C)'],
                        marker_color='#FF6B6B'
                    ))
                    
                    fig.add_trace(go.Bar(
                        name='Humidity (%)',
                        x=df['City'],
                        y=df['Humidity (%)'],
                        marker_color='#4ECDC4'
                    ))
                    
                    fig.add_trace(go.Bar(
                        name='AQI',
                        x=df['City'],
                        y=df['AQI'],
                        marker_color='#45B7D1'
                    ))
                    
                    fig.update_layout(
                        title='City Comparison',
                        barmode='group',
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font={'color': "white", 'family': "Poppins"},
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Comparison insights
                    temp_diff = abs(weather1['tp'] - weather2['tp'])
                    humidity_diff = abs(weather1['hu'] - weather2['hu'])
                    aqi_diff = abs(pollution1['aqius'] - pollution2['aqius'])
                    
                    st.markdown("### 📊 Comparison Insights")
                    
                    insights = []
                    if temp_diff > 5:
                        warmer_city = city1 if weather1['tp'] > weather2['tp'] else city2
                        insights.append(f"🌡️ {warmer_city} is significantly warmer ({temp_diff:.1f}°C difference)")
                    
                    if humidity_diff > 20:
                        humid_city = city1 if weather1['hu'] > weather2['hu'] else city2
                        insights.append(f"💧 {humid_city} is much more humid ({humidity_diff:.0f}% difference)")
                    
                    if aqi_diff > 50:
                        cleaner_city = city1 if pollution1['aqius'] < pollution2['aqius'] else city2
                        insights.append(f"🌱 {cleaner_city} has significantly better air quality ({aqi_diff} AQI difference)")
                    
                    for insight in insights:
                        st.markdown(f"""
                        <div class="suggestion-card">
                            <p style="margin: 0; font-size: 1.1rem;">{insight}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                else:
                    st.error("❌ Could not fetch data for one or both cities.")
            
            except Exception as e:
                st.error(f"❌ Error comparing cities: {e}")

# Sidebar with navigation
with st.sidebar:
    st.markdown("## 🎛️ Navigation")
    
    page = st.radio(
        "Choose a feature:",
        ["🌤️ Current Weather", "🏙️ City Comparison"],
        help="Select what you want to explore"
    )
    
    if page == "🌤️ Current Weather":
        st.markdown("### 📍 Location Settings")
        category = st.selectbox(
            "Data source:",
            options=[
                "By City, State, and Country",
                "By Nearest City (IP Address)", 
                "By Latitude and Longitude"
            ],
            help="Select how you want to get weather data"
        )

# Main content based on page selection
if page == "🏙️ City Comparison":
    display_city_comparison()

elif page == "🌤️ Current Weather":
    # Main content based on category selection
    if category == "By City, State, and Country":
        countries_dict = generate_list_of_countries()
        if countries_dict["status"] == "success":
            countries_list = [""] + [i["country"] for i in countries_dict["data"]]
            
            country_selected = st.sidebar.selectbox("🌍 Select a country", options=countries_list)
            
            if country_selected:
                states_list_response = generate_list_of_states(country_selected)
                if states_list_response["status"] == "success":
                    states_list = [""] + [i["state"] for i in states_list_response["data"]]
                    state_selected = st.sidebar.selectbox("🏛️ Select a state", options=states_list)
                    
                    if state_selected:
                        cities_list_response = generate_list_of_cities(state_selected, country_selected)
                        if cities_list_response["status"] == "success":
                            cities_list = [""] + [i["city"] for i in cities_list_response["data"]]
                            city_selected = st.sidebar.selectbox("🏙️ Select a city", options=cities_list)
                            
                            if city_selected:
                                aqi_data_dict = get_weather_data_by_city(city_selected, state_selected, country_selected)
                                
                                if aqi_data_dict["status"] == "success":
                                    display_weather_data(aqi_data_dict, f"{city_selected}, {state_selected}")
                                else:
                                    st.error("❌ No data available for this location.")
                        else:
                            st.warning("⚠️ No cities available, please select another state.")
                else:
                    st.warning("⚠️ No states available, please select another country.")
        else:
            st.error("🚫 Too many requests. Wait for a few minutes before your next API call.")

    elif category == "By Nearest City (IP Address)":
        url = f"https://api.airvisual.com/v2/nearest_city?key={api_key}"
        aqi_data_dict = requests.get(url).json()
        
        if aqi_data_dict["status"] == "success":
            city_name = aqi_data_dict["data"]["city"]
            country_name = aqi_data_dict["data"]["country"]
            display_weather_data(aqi_data_dict, f"{city_name}, {country_name}")
        else:
            st.error("❌ No data available for your location.")

    elif category == "By Latitude and Longitude":
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.text_input("🌐 Enter latitude", placeholder="e.g., 25.7617")
        with col2:
            longitude = st.text_input("🌐 Enter longitude", placeholder="e.g., -80.1918")
        

        if latitude and longitude:
            try:
                latitude = latitude.strip()
                longitude = longitude.strip()
                lat_float = float(latitude)
                lon_float = float(longitude)

                url = f"https://api.airvisual.com/v2/nearest_city?lat={lat_float}&lon={lon_float}&key={api_key}"
                aqi_data_dict = requests.get(url).json()

                if aqi_data_dict["status"] == "success":
                    display_weather_data(aqi_data_dict, f"Lat: {lat_float}, Lon: {lon_float}")
                else:
                    st.error("❌ No data available for this location.")
                    st.write(aqi_data_dict)  # Debug info
            except ValueError:
                st.error("❌ Please enter valid numeric latitude and longitude values.")
