import streamlit as st
import math

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

def get_wind_emoji(deg):
    dirs = ["⬆️","↗️","➡️","↘️","⬇️","↙️","⬅️","↖️"]
    return dirs[round(deg / 45) % 8]

def calculate(raw_dist, wind_speed, wind_angle, elev, lie):
    return round(raw_dist + elevation_adjustment(elev)
                 + wind_adjustment(wind_speed, wind_angle)
                 + raw_dist * lie_penalty(lie), 1)

# UI
st.set_page_config("PGA2K25 Calculator","⛳")
st.title("⛳ PGA2K25 Calculator")
raw = st.slider("Distance to pin (yards)",50,300,150)
ws = st.slider("Wind speed (mph)",0,30,10)
wa = st.slider("Wind direction (°)",0,360,0)
elev = st.slider("Elevation change (ft)",-50,50,0)
lie = st.selectbox("Lie condition",["Fairway","Light Rough","Heavy Rough","Bunker","Fringe","Rough"])

adj = calculate(raw, ws, wa, elev, lie)
st.subheader(f"🎯 Adjusted distance: **{adj} yd**")
st.write(f"Wind ➡️ {ws} mph {get_wind_emoji(wa)} ({wa}°)")

# Club carry reference
club = st.selectbox("Club",["Pitching Wedge","9 Iron","8 Iron","7 Iron","6 Iron","5 Iron",
                             "4 Iron","3 Iron","5 Wood","3 Wood","Driver"])
carry = {"Pitching Wedge":125,"9 Iron":135,"8 Iron":145,"7 Iron":155,"6 Iron":165,
         "5 Iron":175,"4 Iron":185,"3 Iron":195,"5 Wood":210,"3 Wood":225,"Driver":250}[club]
st.markdown(f"📏 Typical {club}: **{carry} yd carry**")

diff = carry - adj
if abs(diff) <= 5: st.success("✅ Good club choice!")
elif diff > 5: st.warning("⬇️ Might need more club")
else: st.warning("⬆️ Might be too much club")
