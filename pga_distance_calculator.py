
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
        mode='markers+text',
        text=[f"{adjusted_distance} yd"],
        textposition="top center",
        marker=dict(size=12, color='crimson', symbol='x')
    ))
    fig.update_layout(
        yaxis_title="Yards",
        xaxis_title="Club",
        title="Club Carry vs. Adjusted Distance",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

def load_club_distances():
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r") as f:
            return json.load(f)
    else:
        return {
            "Pitching Wedge": 125, "9 Iron": 135, "8 Iron": 145, "7 Iron": 155, "6 Iron": 165,
            "5 Iron": 175, "4 Iron": 185, "3 Iron": 195, "5 Wood": 210, "3 Wood": 225, "Driver": 250
        }

def save_club_distances(distances):
    with open(SAVE_PATH, "w") as f:
        json.dump(distances, f)


def direction_to_degrees(dir):
    return {
        "N": 0, "NE": 45, "E": 90, "SE": 135,
        "S": 180, "SW": 225, "W": 270, "NW": 315
    }.get(dir, 0)


# Streamlit App
st.set_page_config("PGA2K25 Calculator", "⛳")
st.title("⛳ PGA2K25 Distance Calculator")

# Use input boxes instead of sliders
raw = st.number_input("Distance to pin (yards)", min_value=1, max_value=1000, value=150, step=1)
ws = st.number_input("Wind speed (mph)", min_value=0, max_value=100, value=10, step=1)
direction = st.radio("Wind Direction", options=["N", "NE", "E", "SE", "S", "SW", "W", "NW"], horizontal=True)
    wa = direction_to_degrees(direction)
elev = st.number_input("Elevation change (ft)", min_value=-100, max_value=100, value=0, step=1)
lie = st.selectbox("Lie condition", ["Fairway", "Light Rough", "Heavy Rough", "Bunker", "Fringe", "Rough"])

adjusted_distance = calculate(raw, ws, wa, elev, lie)
st.subheader(f"🎯 Adjusted distance: **{adjusted_distance} yd**")
render_wind_compass(wa)

st.markdown("### 🛠️ Customize Your Club Distances")
club_distances = load_club_distances()
updated_club_distances = {}
cols = st.columns(3)
for i, (club, dist) in enumerate(club_distances.items()):
    with cols[i % 3]:
        updated_club_distances[club] = st.number_input(f"{club}", value=dist, min_value=50, max_value=400, step=1)

if st.button("💾 Save My Club Distances"):
    save_club_distances(updated_club_distances)
    st.success("✅ Club distances saved!")

club = st.selectbox("Choose your club:", list(updated_club_distances.keys()))
st.markdown(f"📏 Your {club}: **{updated_club_distances[club]} yd carry**")

diff = updated_club_distances[club] - adjusted_distance
if abs(diff) <= 5: st.success("✅ Good club choice!")
elif diff > 5: st.warning("⬇️ Might need more club")
else: st.warning("⬆️ Might be too much club")

plot_club_carry_vs_adjusted(updated_club_distances, club, adjusted_distance)
