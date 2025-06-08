
import streamlit as st
import math
import plotly.graph_objects as go
import json
import os

SAVE_PATH = "club_distances.json"

def wind_adjustment(wind_speed, wind_angle_deg):
    θ = math.radians(wind_angle_deg)
    comp = wind_speed * math.cos(θ)
    return comp * (0.7 if comp > 0 else 0.5)

def elevation_adjustment(elev_ft):
    return elev_ft * 0.3

def lie_penalty(lie):
    pen = {"Fairway":0.0,"Light Rough":0.05,"Heavy Rough":0.10,
           "Bunker":0.12,"Fringe":0.02,"Rough":0.07}
    return pen.get(lie, 0.0)

def calculate(raw_dist, wind_speed, wind_angle, elev, lie):
    return round(raw_dist + elevation_adjustment(elev)
                 + wind_adjustment(wind_speed, wind_angle)
                 + raw_dist * lie_penalty(lie), 1)

def render_wind_compass(wind_angle_deg):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[1],
        theta=[wind_angle_deg],
        mode='markers+text',
        marker=dict(size=16, color='deepskyblue'),
        text=["💨"],
        textposition="top center",
        showlegend=False
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=False),
            angularaxis=dict(
                rotation=90,
                direction="clockwise",
                tickmode="array",
                tickvals=[0, 45, 90, 135, 180, 225, 270, 315],
                ticktext=["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
            )
        ),
        showlegend=False,
        margin=dict(t=20, b=20, l=40, r=40),
        height=300
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_club_carry_vs_adjusted(club_distances, selected_club, adjusted_distance):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=list(club_distances.keys()),
        y=list(club_distances.values()),
        name="Typical Carry",
        marker_color='lightslategray'
    ))
    fig.add_trace(go.Scatter(
        x=[selected_club],
        y=[adjusted_distance],
        name="Adjusted Distance",
        mode="markers+text",
        marker=dict(size=12, color="crimson"),
        text=[f"{adjusted_distance}y"],
        textposition="bottom center"
    ))
    fig.update_layout(barmode="group", height=400)
    unique_key = f"chart_{selected_club}_{adjusted}"
    unique_key = f\"chart_{selected_club}_{adjusted}\"
    st.plotly_chart(fig, use_container_width=True, key=unique_key)

def save_clubs(club_data):
    with open(SAVE_PATH, "w") as f:
        json.dump(club_data, f)

def load_clubs():
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r") as f:
            return json.load(f)
    return None

# -- UI --

st.title("🏌️ PGA 2K25 Distance Calculator")

if "club_data" not in st.session_state:
    default = load_clubs()
    st.session_state.club_data = default if default else [
        {"name": "Driver", "distance": 280},
        {"name": "3W", "distance": 250},
        {"name": "5W", "distance": 235},
        {"name": "3H", "distance": 225},
        {"name": "4i", "distance": 210},
        {"name": "5i", "distance": 200},
        {"name": "6i", "distance": 190},
        {"name": "7i", "distance": 180},
        {"name": "8i", "distance": 170},
        {"name": "9i", "distance": 160},
        {"name": "PW", "distance": 150},
        {"name": "GW", "distance": 140},
        {"name": "SW", "distance": 130},
        {"name": "LW", "distance": 120},
    ]

st.subheader("Clubs & Distances")
for i in range(len(st.session_state.club_data)):
    col1, col2, col3 = st.columns([3, 2, 1])
    st.session_state.club_data[i]["name"] = col1.text_input(
        f"Club {i+1} Name", value=st.session_state.club_data[i]["name"], key=f"name_{i}"
    )
    st.session_state.club_data[i]["distance"] = col2.number_input(
        f"Distance {i+1}", value=st.session_state.club_data[i]["distance"], step=1, key=f"dist_{i}"
    )
    if col3.button("Remove", key=f"remove_{i}"):
        st.session_state.club_data.pop(i)
        st.experimental_rerun()

if st.button("Add Club"):
    st.session_state.club_data.append({"name": "New Club", "distance": 150})
    st.experimental_rerun()

if st.button("💾 Save My Bag"):
    save_clubs(st.session_state.club_data)
    st.success("Clubs saved!")

if st.button("📂 Load Saved Bag"):
    loaded = load_clubs()
    if loaded:
        st.session_state.club_data = loaded
        st.experimental_rerun()

clubs = st.session_state.club_data

club_names = [c["name"] for c in clubs]
club_distances = {c["name"]: c["distance"] for c in clubs}

st.subheader("Course Conditions")
selected_club = st.selectbox("Select Club", club_names)
wind_speed = st.slider("Wind Speed (mph)", -20, 20, 0)
elevation = st.slider("Elevation Change (ft)", -100, 100, 0)
lie = st.selectbox("Lie", ["Fairway", "Light Rough", "Rough", "Heavy Rough", "Bunker", "Fringe"])

st.subheader("Wind Direction")
directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
direction_degrees = {"N": 0, "NE": 45, "E": 90, "SE": 135, "S": 180, "SW": 225, "W": 270, "NW": 315}
selected_direction = st.radio("Wind From", directions, horizontal=True)
render_wind_compass(direction_degrees[selected_direction])

raw_dist = club_distances[selected_club]
adjusted = calculate(raw_dist, wind_speed, direction_degrees[selected_direction], elevation, lie)

st.markdown(f"### 🎯 Adjusted Distance: `{adjusted}` yards")
plot_club_carry_vs_adjusted(club_distances, selected_club, adjusted)


# Show Adjusted Distance
st.markdown(f"### 🎯 Adjusted Distance: `{adjusted}` yards")

# Plot
plot_club_carry_vs_adjusted(club_distances, selected_club, adjusted)

# Suggested Club
closest_club = min(clubs, key=lambda c: abs(c["distance"] - adjusted))
st.markdown(f"### 💡 Suggested Club: `{closest_club['name']}` ({closest_club['distance']}y)")
