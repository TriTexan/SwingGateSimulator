import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def get_elbow(p1, p2, r1, r2):
    x1, y1 = p1 
    x2, y2 = p2 
    d = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    if d > (r1 + r2 + 1e-4) or d < abs(r1 - r2) - 1e-4:
        return None
    if abs(d - (r1 + r2)) < 1e-4:
        return (x1 + r1 * (x2 - x1) / d, y1 + r1 * (y2 - y1) / d)
    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h = np.sqrt(max(0, r1**2 - a**2))
    x0, y0 = x1 + a * (x2 - x1) / d, y1 + a * (y2 - y1) / d
    rx, ry = (y2 - y1) * (h / d), -(x2 - x1) * (h / d)
    return (x0 + rx, y0 + ry)

st.set_page_config(page_title="Gate Simulator", layout="centered") 
st.title("Swing Gate Geometry Simulator")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Field Dimensions")
    gate_len = st.number_input("Gate Length (in)", value=168.0, step=1.0, format="%.2f")
    mount_dist = st.number_input("Bracket Dist (D)", value=49.0, step=0.1, format="%.2f")
    sx = st.number_input("Shaft X", value=39.0, step=0.1, format="%.2f")
    sy = st.number_input("Shaft Y (Setback)", value=-11.0, step=0.1, format="%.2f")
    st.header("Arm Lengths")
    r1 = st.number_input("Primary (R1)", value=31.96, step=0.01, format="%.2f")
    r2 = st.number_input("Secondary (R2)", value=39.60, step=0.01, format="%.2f")

# --- CORE MATH ---
angle = st.slider("Gate Swing", 0, 90, 0)
rad = np.radians(angle)

# Current Position
bx, by = mount_dist * np.sin(rad), mount_dist * np.cos(rad)
tx, ty = gate_len * np.sin(rad), gate_len * np.cos(rad)
elbow = get_elbow((sx, sy), (bx, by), r1, r2)

# FIX: Calculate "Overlap" based ONLY on the CLOSED (0 deg) distance
# Closed Bracket is at (0, mount_dist)
dist_closed = np.sqrt(sx**2 + (mount_dist - sy)**2)
total_reach = r1 + r2
overlap_closed = round(total_reach - dist_closed, 2)
is_straight = abs(overlap_closed) <= 0.05

# Current reachability check for the slider
dist_current = np.sqrt((bx - sx)**2 + (by - sy)**2)

# --- METRICS ---
m1, m2 = st.columns(2)
if total_reach < dist_current - 0.05:
    st.error(f"⚠️ TOO SHORT: Need {dist_current:.2f}\" to reach this angle.")
else:
    with m1:
        if is_straight: 
            st.success("✅ Arms Straight (Closed)")
        elif overlap_closed > 0: 
            st.warning(f"⚠️ Closed Overlap: {overlap_closed:.2f}\"")
        else:
            st.error(f"❌ Gap when Closed: {abs(overlap_closed):.2f}\"")
    with m2:
        if elbow:
            v_gate, v_arm = np.array([bx, by]), np.array([elbow[0] - bx, elbow[1] - by])
            cos_t = np.dot(v_gate, v_arm) / (np.linalg.norm(v_gate) * np.linalg.norm(v_arm))
            angle_val = 180 - np.degrees(np.arccos(np.clip(cos_t, -1.0, 1.0)))
            st.info(f"**Angle to Gate**: {angle_val:.1f}°")

# --- PLOTTING ---
fig, ax = plt.subplots(figsize=(8, 7)) 
ax.set_aspect('equal')

limit_max = max(gate_len, sx) + 20
limit_min = min(sy, -r2 - 20)
ax.set_xlim(-20, limit_max)
ax.set_ylim(limit_min, limit_max)
ax.grid(True, linestyle=':', alpha=0.4)

ax.plot(0, 0, 'ks', markersize=10, label="Hinge")
ax.plot([0, tx], [0, ty], color='brown', lw=6, label=f'Gate ({gate_len/12:.1f}ft)')
ax.plot(sx, sy, 'go', markersize=10, label='Shaft')

if elbow:
    ax.plot([sx, elbow[0], bx], [sy, elbow[1], by], 'r-o', lw=3, label='Arms')
elif is_straight and angle == 0:
    ax.plot([sx, bx], [sy, by], 'r-o', lw=3, label='Arms (Straight)')

ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=4, fontsize='small', frameon=False)
st.pyplot(fig, use_container_width=True)