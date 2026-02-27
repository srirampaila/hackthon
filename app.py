import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title=" Sentiment Trader", layout="wide", initial_sidebar_state="collapsed")

# ----------------- CSS STYLING -----------------
st.markdown("""
<style>
/* General App Styling */
.stApp {
    background-color: #ffffff;
    color: #111111;
}

/* Header & Profile styling */
.profile-container {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 15px;
    padding: 10px 0;
}
.greeting {
    font-size: 1.1rem;
    font-weight: 500;
    color: #333333;
}
.brand-logo {
    font-weight: 800;
    font-size: 1.4rem;
    color: #007bff;
    letter-spacing: 1px;
    margin-right: auto; /* Push everything else to the right */
}

/* Terminal Feed Styling */
.terminal-container {
    background-color: #000000;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 15px;
    height: 700px;
    overflow-y: auto;
    font-family: 'Courier New', Courier, monospace;
    color: #00ff00;
    box-shadow: 0 0 10px rgba(0,255,0,0.1);
}
.terminal-line {
    margin-bottom: 12px;
    font-size: 0.9rem;
    line-height: 1.4;
}
.timestamp {
    color: #888;
    margin-right: 8px;
}
/* Sentiment Pills */
.pill {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: bold;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #111;
    margin-right: 8px;
}
.pill.positive { background-color: #00ff7f; box-shadow: 0 0 5px #00ff7f; }
.pill.negative { background-color: #ff4500; box-shadow: 0 0 5px #ff4500; color: #fff;}
.pill.neutral  { background-color: #ffd700; box-shadow: 0 0 5px #ffd700; }

/* Watchlist Cards & 3D Hover Interactions */
.watchlist-container {
    display: flex;
    gap: 15px;
    padding-bottom: 25px; /* extra space for shadows */
    padding-top: 10px;
    perspective: 1000px;
    width: 100%;
}
.watch-card {
    background: linear-gradient(145deg, #ffffff, #f8f9fa);
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 15px 10px;    /* Proper inner spacing */
    flex: 1;              /* Makes all 5 cards equal width */
    text-align: center;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    position: relative;
    cursor: pointer;
    transform-style: preserve-3d;
    transition: transform 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    overflow: hidden;
}

/* Hover: Lift, Drop Shadow, and Tilt */
.watch-card:hover {
    box-shadow: 0 15px 25px rgba(0,0,0,0.1), 0 5px 10px rgba(0,0,0,0.05);
}

/* Shimmer/Border Beam Animation on Hover */
.watch-card::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%; width: 200%; height: 200%;
    background: conic-gradient(from 0deg, transparent 70%, rgba(0, 123, 255, 0.4) 80%, transparent 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
    animation: rotate-beam 3s linear infinite;
    pointer-events: none;
    z-index: 0;
}
.watch-card:hover::before {
    opacity: 1;
}
/* Mask out the inside so only the border glows */
.watch-card::after {
    content: '';
    position: absolute;
    top: 1px; left: 1px; right: 1px; bottom: 1px;
    background: linear-gradient(145deg, #ffffff, #f8f9fa);
    border-radius: 11px;
    z-index: 1;
}

@keyframes rotate-beam {
    100% { transform: rotate(360deg); }
}

/* High-Density Asset Card Layout */
.watch-card-content {
    position: relative;
    z-index: 2;
    transform: translateZ(10px); /* Internal 3D pop */
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
    align-items: center;
    text-align: left;
    height: 100%;
}

.watch-card-ticker {
    font-size: 1.1rem;
    font-weight: 800;
    color: #111;
    grid-column: 1 / 2;
    grid-row: 1 / 2;
}
.watch-card-price {
    font-size: 1.05rem;
    font-weight: 600;
    color: #333;
    grid-column: 1 / 2;
    grid-row: 2 / 3;
    margin-top: 4px;
}
.watch-card-change { 
    font-weight: 700; 
    font-size: 0.9rem;
    grid-column: 2 / 3;
    grid-row: 1 / 2;
    text-align: right;
}
.watch-card-change.up { color: #00c853; }
.watch-card-change.down { color: #d50000; }

.watch-card-sparkline {
    grid-column: 2 / 3;
    grid-row: 2 / 3;
    width: 100%;
    height: 30px;
    margin-top: 5px;
}

/* Empty Ghost Add Box State */
.watch-card-add {
    background: rgba(250, 250, 250, 0.3); /* very faint gray-50 */
    border: 2px dashed #cfd8dc;            /* Dashed faint grey */
    border-radius: 12px;
    display: flex;
    justify-content: center;
    align-items: center;
    flex: 1;              /* Exact same size as active cards */
    cursor: pointer;
    transform-style: preserve-3d;
    transition: all 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.watch-card-add:hover {
    background: rgba(255, 255, 255, 0.9);
    border: 2px solid #007bff; /* Turns solid + blue */
    box-shadow: 0 15px 25px rgba(0,123,255,0.15), 0 5px 10px rgba(0,123,255,0.05); /* Soft glowing shadow */
}
.watch-card-add svg {
    width: 32px;
    height: 32px;
    stroke: #aaa; /* Thin/light icon weight handled by stroke-width in svg */
    transition: stroke 0.2s ease;
    transform: translateZ(10px);
}
.watch-card-add:hover svg {
    stroke: #007bff;
}

/* Header Glass Search Bar */
.header-left-col {
    display: flex;
    align-items: center;
    gap: 20px;
}
.search-container {
    position: relative;
    flex-grow: 1;
    max-width: 300px;
}
.search-input {
    width: 100%;
    padding: 8px 15px 8px 35px;
    border-radius: 20px;
    border: 1px solid rgba(0,0,0,0.1);
    background: rgba(255,255,255,0.6);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    font-size: 0.9rem;
    color: #333;
    outline: none;
    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
}
.search-input:focus {
    width: 105%;
    border-color: rgba(0, 123, 255, 0.5);
    background: #ffffff;
    box-shadow: 0 0 0 3px rgba(0,123,255,0.15), inset 0 1px 3px rgba(0,0,0,0.05);
}
.search-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 14px;
    height: 14px;
    stroke: #888;
    pointer-events: none;
}


</style>
""", unsafe_allow_html=True)

# ----------------- MOCK DATA -----------------
# Generate data for the CSI Area Chart
dates = pd.date_range(end=datetime.now(), periods=50, freq='h')
np.random.seed(42)
csi_values = np.sin(np.linspace(0, 10, 50)) * 50 + 50 + np.random.normal(0, 10, 50)
csi_values = np.clip(csi_values, 0, 100) # Keep between 0 and 100

# Generating Data for mini Sparkline
spark_v = np.cumsum(np.random.randn(24) * 2 + 1) + 100

# ----------------- HEADER -----------------
head_col1, head_col2 = st.columns([1, 1])

with head_col1:
    st.markdown("""
        <div class="header-left-col">
            <div class="brand-logo">Agentic <span style="font-weight:300;color:#888;">Trader</span></div>
            <div class="search-container">
                <svg class="search-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
                <input type="text" class="search-input" id="global-search" placeholder="Search to add...">
            </div>
        </div>
    """, unsafe_allow_html=True)

with head_col2:
    # Build sparkline using plotly
    fig_spark = go.Figure(go.Scatter(y=spark_v, mode='lines', line={"color": '#00ff7f', "width": 2}))
    fig_spark.update_layout(
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        width=100, height=30,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis={"showgrid": False, "zeroline": False, "showticklabels": False},
        yaxis={"showgrid": False, "zeroline": False, "showticklabels": False}
    )
    
    st.markdown(f"""
    <div class="profile-container">
        <div class="greeting">Welcome back, <b>Alex</b>.</div>
        <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Alex" width="40" style="border-radius:20px; border:2px solid #555;">
    </div>
    """, unsafe_allow_html=True)
    
    # We inject the sparkline right under the profile widget using st.plotly_chart in a tiny container
    col_s1, col_s2, col_s3 = st.columns([6, 2, 1])
    with col_s2:
        st.write("<div style='text-align:right; font-size:12px; color:#555;'>24h P&L</div>", unsafe_allow_html=True)
        st.plotly_chart(fig_spark, config={'displayModeBar': False})


# ----------------- MAIN LAYOUT -----------------
main_col, feed_col = st.columns([2.2, 1])

# Helper for inline CSS SVG sparklines in Watchlist
def generate_sparkline_svg(color, is_up=True):
    # Generates a smooth, random-looking bezier path for aesthetic purposes
    points = [100, 80, 40, 60, 20, 0] if is_up else [0, 20, 60, 40, 80, 100]
    # Add some random noise
    points = [max(0, min(100, p + np.random.randint(-15, 15))) for p in points]
    path_d = f"M 0 {points[0]} C 20 {points[1]}, 40 {points[2]}, 60 {points[3]} S 80 {points[4]}, 100 {points[5]}"
    return f'''
    <svg class="watch-card-sparkline" viewBox="0 0 100 100" preserveAspectRatio="none">
        <path d="{path_d}" fill="none" stroke="{color}" stroke-width="6" stroke-linecap="round" vector-effect="non-scaling-stroke"/>
    </svg>
    '''

with main_col:
    # 1. Stocks Watchlist (Horizontal Cards) with 3D interactions
    st.markdown("<h3 style='margin-top: -45px;'>Agent Watchlist</h3>", unsafe_allow_html=True)
    watchlist_html = f"""
    <div class="watchlist-container">
        <div class="watch-card tiltable">
            <div class="watch-card-content">
                <div class="watch-card-ticker">AAPL</div>
                <div class="watch-card-change up">+1.24%</div>
                <div class="watch-card-price">$189.43</div>
                {generate_sparkline_svg('#00c853', True)}
            </div>
        </div>
        <div class="watch-card tiltable">
            <div class="watch-card-content">
                <div class="watch-card-ticker">TSLA</div>
                <div class="watch-card-change down">-0.85%</div>
                <div class="watch-card-price">$214.10</div>
                {generate_sparkline_svg('#d50000', False)}
            </div>
        </div>
        <div class="watch-card tiltable">
            <div class="watch-card-content">
                <div class="watch-card-ticker">NVDA</div>
                <div class="watch-card-change up">+3.10%</div>
                <div class="watch-card-price">$875.28</div>
                {generate_sparkline_svg('#00c853', True)}
            </div>
        </div>
        <div class="watch-card tiltable">
            <div class="watch-card-content">
                <div class="watch-card-ticker">MSFT</div>
                <div class="watch-card-change up">+0.45%</div>
                <div class="watch-card-price">$415.50</div>
                {generate_sparkline_svg('#00c853', True)}
            </div>
        </div>
        
        <!-- Ghost Add Card -->
        <div class="watch-card-add tiltable" onclick="document.querySelector('.search-input').focus()">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
        </div>
    </div>
    
    <script>
    // Apply 3D Spring Tilt physics to all watch cards
    const watchCards = window.parent.document.querySelectorAll('.tiltable') || document.querySelectorAll('.tiltable');
    watchCards.forEach(card => {{
        card.addEventListener('mousemove', (e) => {{
            const rect = card.getBoundingClientRect();
            // Calculate relative offset and map to [-1, 1] range
            const x = (e.clientX - rect.left - rect.width / 2) / (rect.width / 2);
            const y = (e.clientY - rect.top - rect.height / 2) / (rect.height / 2);
            
            // Soft 5-degree perspective tilt
            const rotateX = -y * 8; 
            const rotateY = x * 8;
            
            card.style.transform = `rotateX(${{rotateX}}deg) rotateY(${{rotateY}}deg) scale3d(1.02, 1.02, 1.02)`;
        }});
        
        card.addEventListener('mouseleave', () => {{
            card.style.transform = `rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)`;
        }});
    }});
    </script>
    """
    st.components.v1.html(watchlist_html, height=140)

    # 2. Risk Meter (Ultra High-Fidelity 3D Glassmorphic Gauge)
    st.markdown("### Portfolio Risk Assessment")
    cur_risk = 68  # Yellow zone
    
    # 3D Glassmorphism Gauge HTML/CSS/JS
    gauge_html = f"""
    <div class="ultimate-gauge-wrapper">
        <div class="glass-gauge-card" id="tilt-card">
            
            <!-- Floating Text Label -->
            <div class="gauge-title">Current Risk Level</div>
            
            <!-- The 3D Glass Gauge Base -->
            <div class="gauge-base">
                <svg viewBox="0 0 200 100" class="gauge-svg">
                    <!-- Definitions for Dropshadows and Gradients -->
                    <defs>
                        <filter id="ambientOcclusion" x="-20%" y="-20%" width="140%" height="140%">
                            <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#000" flood-opacity="0.15"/>
                        </filter>
                        <filter id="needleShadow" x="-50%" y="-50%" width="200%" height="200%">
                            <feDropShadow dx="0" dy="15" stdDeviation="10" flood-color="#000" flood-opacity="0.25"/>
                        </filter>
                    </defs>

                    <!-- Background Glass Track (Semi-translucent) -->
                    <!-- Green Segment -->
                    <path class="segment green-seg" d="M 20 100 A 80 80 0 0 1 60 30.7" fill="none" stroke="rgba(141, 242, 184, 0.4)" stroke-width="24" stroke-linecap="round"/>
                    <!-- Yellow Segment -->
                    <path class="segment yellow-seg" d="M 60 30.7 A 80 80 0 0 1 140 30.7" fill="none" stroke="rgba(255, 226, 112, 0.4)" stroke-width="24"/>
                    <!-- Red Segment -->
                    <path class="segment red-seg" d="M 140 30.7 A 80 80 0 0 1 180 100" fill="none" stroke="rgba(255, 159, 128, 0.4)" stroke-width="24" stroke-linecap="round"/>

                    <!-- Foreground Black Needle Arc (Thick, Matte Obsidian) -->
                    <!-- Stroke dasharray/offset trick to animate it to 68% -->
                    <path class="needle-arc" 
                          d="M 20 100 A 80 80 0 0 1 180 100" 
                          fill="none" 
                          stroke="#1a1c24" 
                          stroke-width="12" 
                          stroke-linecap="round"
                          stroke-dasharray="251.2" 
                          stroke-dashoffset="80.38" 
                          filter="url(#needleShadow)" />
                </svg>

                <!-- 3D Extruded Center Number -->
                <div class="gauge-value">{cur_risk}</div>
                
                <!-- Glass Light Sweep Effect -->
                <div class="light-sweep"></div>
            </div>
        </div>
    </div>

    <style>
    /* Wrapper handles perspective */
    .ultimate-gauge-wrapper {{
        perspective: 1200px;
        padding: 20px;
        display: flex;
        justify-content: center;
        align-items: center;
    }}

    /* Card acts as the rotatable plane */
    .glass-gauge-card {{
        position: relative;
        width: 100%;
        max-width: 350px;
        height: 250px;
        border-radius: 20px;
        background: linear-gradient(135deg, rgba(255,255,255,0.7) 0%, rgba(240,245,250,0.4) 100%);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.8);
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        transform-style: preserve-3d;
        /* Default Spring Physics transition for returning to center */
        transition: transform 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}

    /* Hover elevation */
    .glass-gauge-card:hover {{
        box-shadow: 0 30px 60px rgba(0,0,0,0.12), 0 10px 20px rgba(0,0,0,0.08);
        transition: transform 0.1s ease-out; /* Fast response on mousemove */
    }}

    /* Title floats above */
    .gauge-title {{
        position: absolute;
        top: 20px;
        width: 100%;
        text-align: center;
        font-size: 1.1rem;
        font-weight: 600;
        color: #333;
        transform: translateZ(30px); /* 3D pop */
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}

    /* The actual gauge base */
    .gauge-base {{
        position: absolute;
        bottom: 20px;
        left: 5%;
        width: 90%;
        height: 150px;
        transform-style: preserve-3d;
        transform: translateZ(40px); /* Lifts the gauge off the card */
    }}

    /* SVG Styling */
    .gauge-svg {{
        width: 100%;
        height: 100%;
        overflow: visible;
        filter: url(#ambientOcclusion);
    }}

    /* The Floating Value */
    .gauge-value {{
        position: absolute;
        bottom: 15px;
        width: 100%;
        text-align: center;
        font-size: 4.5rem;
        font-weight: 800;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #1a1c24;
        transform: translateZ(60px); /* Floats highest */
        /* Extruded 3D Text Shadow */
        text-shadow: 
            0 1px 0 #ccc, 
            0 2px 0 #c9c9c9, 
            0 3px 0 #bbb, 
            0 4px 0 #b9b9b9, 
            0 5px 0 #aaa, 
            0 6px 1px rgba(0,0,0,.1), 
            0 0 5px rgba(0,0,0,.1), 
            0 1px 3px rgba(0,0,0,.3), 
            0 3px 5px rgba(0,0,0,.2), 
            0 5px 10px rgba(0,0,0,.25), 
            0 10px 10px rgba(0,0,0,.2), 
            0 20px 20px rgba(0,0,0,.15);
    }}

    /* Realistic Light Sweep over the glass */
    .light-sweep {{
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        border-radius: 100px 100px 0 0;
        background: linear-gradient(105deg, 
            rgba(255,255,255,0) 0%, 
            rgba(255,255,255,0.0) 40%, 
            rgba(255,255,255,0.8) 50%, 
            rgba(255,255,255,0.0) 60%, 
            rgba(255,255,255,0) 100%);
        background-size: 200% 100%;
        z-index: 10;
        opacity: 0;
        mix-blend-mode: overlay;
        transform: translateZ(45px); /* Just above the glass */
        pointer-events: none;
    }}

    .glass-gauge-card:hover .light-sweep {{
        animation: sweep 2s infinite ease-in-out;
        opacity: 1;
    }}

    @keyframes sweep {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}
    </style>

    <script>
    // 3D Gyroscope Hover Physics using Spring Damping mimicking math
    const card = window.parent.document.getElementById('tilt-card') || document.getElementById('tilt-card');
    
    if (card) {{
        card.addEventListener('mousemove', (e) => {{
            const rect = card.getBoundingClientRect();
            // Calculate mouse position relative to center of card (-1 to 1)
            const x = (e.clientX - rect.left - rect.width / 2) / (rect.width / 2);
            const y = (e.clientY - rect.top - rect.height / 2) / (rect.height / 2);
            
            // Max rotation is 15 degrees
            const rotateX = -y * 15; 
            const rotateY = x * 15;
            
            card.style.transform = `rotateX(${{rotateX}}deg) rotateY(${{rotateY}}deg)`;
        }});
        
        // Reset with spring transition
        card.addEventListener('mouseleave', () => {{
            card.style.transform = `rotateX(0deg) rotateY(0deg)`;
        }});
    }}
    </script>
    """
    
    # Render custom component
    st.components.v1.html(gauge_html, height=350)
    st.markdown("</div>", unsafe_allow_html=True)

    # 3. CSI Chart (Area chart with gradient based on sentiment)
    st.markdown("### Composite Sentiment Index (CSI)")
    
    current_csi = csi_values[-1]
    # Set fill color based on current CSI value (high=green, low=red)
    fill_color = "rgba(0, 255, 127, 0.3)" if current_csi >= 50 else "rgba(255, 69, 0, 0.3)"
    line_color = "#00ff7f" if current_csi >= 50 else "#ff4500"

    fig_csi = go.Figure()
    fig_csi.add_trace(go.Scatter(
        x=dates, y=csi_values,
        fill='tozeroy',
        mode='lines',
        line={"color": line_color, "width": 3},
        fillcolor=fill_color
    ))
    fig_csi.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=350,
        margin={"l": 0, "r": 0, "t": 20, "b": 20},
        xaxis={"showgrid": True, "gridcolor": '#eee', "title": "Time"},
        yaxis={"showgrid": True, "gridcolor": '#eee', "title": "Sentiment Score (0-100)", "range": [0, 100]},
        font={"color": '#333'}
    )
    st.markdown('<div class="gauge-container">', unsafe_allow_html=True)
    st.plotly_chart(fig_csi, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


with feed_col:
    st.markdown("<h3 style='margin-top: 15px;'>Live Evaluation Feed</h3>", unsafe_allow_html=True)
    
    terminal_logs = [
        {"time": "10:45:12", "sentiment": "POSITIVE", "score": "+0.85", "text": "Fed announces rate cut possibilities; market rallies. Re-allocating portfolio weighting to tech."},
        {"time": "10:48:03", "sentiment": "NEUTRAL",  "score": " 0.00", "text": "Scanning real-time order books for TSLA... Volume normalized."},
        {"time": "10:52:19", "sentiment": "NEGATIVE", "score": "-0.62", "text": "Earnings miss detected from tier-2 supplier context. Short-term bearish signal fired for NVDA supply chain."},
        {"time": "10:55:01", "sentiment": "POSITIVE", "score": "+0.91", "text": "Breaking news indexed: Apple launches new AI framework. Upgrading target price logic..."},
        {"time": "10:58:30", "sentiment": "NEUTRAL",  "score": "+0.10", "text": "Holding steady. Risk metric at 68%. Awaiting CPI print at 11:00 EST."},
        {"time": "11:00:05", "sentiment": "POSITIVE", "score": "+0.78", "text": "CPI data cooler than expected. Triggering automated buy algorithms on SPY."},
        {"time": "11:02:40", "sentiment": "NEGATIVE", "score": "-0.40", "text": "Minor correction in energy sector detected based on API inventory report. Adjusting weights."}
    ]

    feed_html = '<div class="terminal-container gauge-container">'
    for log in terminal_logs:
        css_class = log["sentiment"].lower()
        
        feed_html += f'''<div class="terminal-line">
<span class="timestamp">[{log['time']}]</span>
<span class="pill {css_class}">[{log['score']} {log['sentiment']}]</span>
<span class="log-text">{log['text']}</span>
</div>'''
        
    feed_html += '</div>'
    st.markdown(feed_html, unsafe_allow_html=True)
