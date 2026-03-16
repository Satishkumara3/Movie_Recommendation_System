import streamlit as st
import pickle
import pandas as pd
import time
import requests
import base64
from concurrent.futures import ThreadPoolExecutor

# ──────────────────────────────────────────────
# Page Config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="🎬 CineMatch — Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ──────────────────────────────────────────────
# Premium Glassmorphism CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

    /* ── Global Dark Theme ── */
    .stApp {
        background-color: transparent;
        font-family: 'Outfit', sans-serif;
    }

    /* Animated background particles effect */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background:
            radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.15) 0%, transparent 50%),
            radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.1) 0%, transparent 50%),
            radial-gradient(circle at 50% 80%, rgba(120, 200, 255, 0.1) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    /* ── Hide Streamlit defaults ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 0rem !important;
    }

    /* ── Custom Header ── */
    .hero-header {
        text-align: center;
        padding: 0.5rem 1rem 0.5rem;
        position: relative;
        z-index: 1;
    }

    .hero-header h1 {
        font-family: 'Outfit', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #f5af19 0%, #f12711 30%, #c471ed 60%, #12c2e9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
        letter-spacing: -1px;
    }

    .hero-header p {
        color: rgba(255,255,255,0.6);
        font-size: 1.1rem;
        font-weight: 300;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* ── Glass Card for Search Area ── */
    .glass-search {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.2rem 2rem;
        margin: 0.5rem auto 1rem;
        max-width: 700px;
        box-shadow:
            0 8px 32px rgba(0, 0, 0, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }

    .glass-search label, .glass-search .search-label {
        color: rgba(255, 255, 255, 0.85) !important;
        font-weight: 500;
        font-size: 0.95rem;
        letter-spacing: 0.5px;
    }

    /* ── Selectbox styling ── */
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        color: white !important;
        font-family: 'Outfit', sans-serif !important;
    }

    .stSelectbox label {
        color: rgba(255,255,255,0.8) !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
    }

    /* ── Premium Button ── */
    .stButton > button {
        background: linear-gradient(135deg, #f12711 0%, #f5af19 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.7rem 2.5rem !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 20px rgba(241, 39, 17, 0.3) !important;
        width: 100% !important;
        margin-top: 0.5rem !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 30px rgba(241, 39, 17, 0.5) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── Section Title ── */
    .section-title {
        text-align: center;
        margin: 2rem 0 1.5rem;
        position: relative;
        z-index: 1;
    }

    .section-title h2 {
        font-family: 'Outfit', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.3rem;
    }

    .section-title .divider {
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #f12711, #f5af19);
        margin: 0 auto;
        border-radius: 2px;
    }

    /* ── Movie Card Glass ── */
    .movie-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
        position: relative;
        z-index: 1;
    }

    .movie-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow:
            0 12px 40px rgba(0, 0, 0, 0.4),
            0 0 30px rgba(241, 39, 17, 0.15);
        border-color: rgba(245, 175, 25, 0.3);
    }

    .movie-card img {
        width: 100%;
        max-height: 290px;
        object-fit: cover;
        border-radius: 16px 16px 0 0;
        display: block;
    }

    .movie-card .movie-title {
        padding: 0.5rem 0.4rem;
        text-align: center;
        color: rgba(255,255,255,0.9);
        font-family: 'Outfit', sans-serif;
        font-weight: 500;
        font-size: 0.85rem;
        line-height: 1.3;
        min-height: 2.8rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* ── Glow effect on card hover ── */
    .movie-card::after {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(241,39,17,0.05), rgba(245,175,25,0.05));
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }

    .movie-card:hover::after {
        opacity: 1;
    }

    /* ── Movie Link ── */
    .movie-link {
        color: rgba(255,255,255,0.7);
        text-decoration: none;
        margin-left: 0.3rem;
        transition: color 0.3s ease;
        display: inline-flex;
        align-items: center;
    }

    .movie-link:hover {
        color: #f5af19;
    }

    /* ── Movie Badges & Hover Details ── */
    .movie-badges {
        position: absolute;
        bottom: 3.5rem; /* just above the title */
        left: 0.5rem;
        display: flex;
        gap: 0.4rem;
        z-index: 2;
    }

    .badge {
        background: rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
        color: white;
        font-family: 'Outfit', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        gap: 0.2rem;
    }

    .badge-rating i {
        color: #f5af19;
    }

    .movie-overlay {
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 290px;
        background: rgba(15, 12, 41, 0.9);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        color: rgba(255,255,255,0.9);
        font-family: 'Outfit', sans-serif;
        font-size: 0.8rem;
        line-height: 1.4;
        padding: 1.2rem;
        overflow-y: auto;
        opacity: 0;
        transition: opacity 0.3s ease;
        z-index: 3;
        display: flex;
        flex-direction: column;
        border-radius: 16px 16px 0 0;
    }

    .movie-card:hover .movie-overlay {
        opacity: 1;
    }
    
    .movie-overlay h4 {
        margin: 0 0 0.5rem 0;
        color: white;
        font-size: 1rem;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 0.3rem;
    }

    /* Custom scrollbar for overlay */
    .movie-overlay::-webkit-scrollbar {
        width: 4px;
    }
    .movie-overlay::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
    }
    .movie-overlay::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.2);
        border-radius: 4px;
    }

    /* ── Spinner ── */
    .loading-text {
        text-align: center;
        color: rgba(255,255,255,0.7);
        font-family: 'Outfit', sans-serif;
        font-size: 1.1rem;
        padding: 2rem;
    }

    /* ── Footer ── */
    .app-footer {
        text-align: center;
        padding: 1rem 0 0.5rem;
        color: rgba(255,255,255,0.3);
        font-family: 'Outfit', sans-serif;
        font-size: 0.8rem;
        letter-spacing: 1px;
        position: relative;
        z-index: 1;
    }

    /* Override Streamlit column gaps */
    [data-testid="stHorizontalBlock"] {
        gap: 1rem;
    }

    /* Warning box styling */
    .stAlert {
        background: rgba(255, 193, 7, 0.1) !important;
        border: 1px solid rgba(255, 193, 7, 0.2) !important;
        border-radius: 12px !important;
        color: rgba(255, 193, 7, 0.9) !important;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Background Image Setup
# ──────────────────────────────────────────────
def set_background(image_file):
    try:
        with open(image_file, "rb") as f:
            img_data = f.read()
        b64_encoded = base64.b64encode(img_data).decode()
        style = f"""
            <style>
            .stApp {{
                background: transparent !important;
            }}
            .stApp::before {{
                content: "";
                position: fixed;
                top: -5vw;
                left: -5vw;
                right: -5vw;
                bottom: -5vw;
                background-image: linear-gradient(to bottom, rgba(15, 12, 41, 0.7) 0%, rgba(15, 12, 41, 0.4) 50%, rgba(15, 12, 41, 0.9) 100%), url(data:image/jpeg;base64,{b64_encoded}) !important;
                background-size: cover !important;
                background-position: center !important;
                background-repeat: no-repeat !important;
                filter: blur(12px);
                z-index: 0;
                pointer-events: none;
            }}
            </style>
        """
        st.markdown(style, unsafe_allow_html=True)
    except FileNotFoundError:
        pass

set_background('app_bg_low.jpg')


# ──────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────
def get_placeholder_image(text="No Poster"):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="300" height="450">
        <defs>
            <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#1a1a2e"/>
                <stop offset="100%" style="stop-color:#16213e"/>
            </linearGradient>
        </defs>
        <rect width="300" height="450" fill="url(#bg)"/>
        <text x="150" y="210" font-family="Arial" font-size="40" fill="#e0e0e0"
              text-anchor="middle" dominant-baseline="middle">🎬</text>
        <text x="150" y="260" font-family="Arial" font-size="16" fill="rgba(255,255,255,0.6)"
              text-anchor="middle" dominant-baseline="middle">{text}</text>
    </svg>'''
    b64 = base64.b64encode(svg.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64}"


# Reusable HTTP session for faster connection pooling
http_session = requests.Session()

def fetch_poster(movie_id):
    cache_key = f"poster_{movie_id}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]

    max_retries = 5
    for attempt in range(max_retries):
        try:
            api_key = os.environ.get("TMDB_API_KEY", "4d4c2bfb1b500a5ed7cbe3893f65158e")
            url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
            response = http_session.get(url, timeout=10)
            
            # Raise exception for bad status codes (like 429 Too Many Requests)
            response.raise_for_status()

            data = response.json()
            poster_path = data.get("poster_path")
            rating = round(data.get("vote_average", 0), 1)
            release_date = data.get("release_date", "N/A")
            year = release_date.split("-")[0] if release_date else "N/A"
            overview = data.get("overview", "No overview available.")

            if poster_path:
                poster_url = "https://image.tmdb.org/t/p/w500" + poster_path
            else:
                poster_url = get_placeholder_image("Poster Not Found")
                
            res = (poster_url, rating, year, overview)
            st.session_state[cache_key] = res
            return res

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1 + attempt * 0.5)  # Exponential-ish backoff
                continue
            else:
                print(f"Failed to fetch details for ID {movie_id}: {e}")
                return (get_placeholder_image("Network Error"), "N/A", "N/A", "Details unavailable due to network error.")


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]

    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movie_names = []
    movie_ids = []

    for i in distances[1:6]:
        recommended_movie_names.append(movies.iloc[i[0]].title)
        movie_ids.append(movies.iloc[i[0]].movie_id)

    # Fetch all 5 details in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        fetched_data = list(executor.map(fetch_poster, movie_ids))
        
    recommended_movie_posters = []
    recommended_ratings = []
    recommended_years = []
    recommended_overviews = []
    
    for data in fetched_data:
        if isinstance(data, tuple) and len(data) == 4:
            recommended_movie_posters.append(data[0])
            recommended_ratings.append(data[1])
            recommended_years.append(data[2])
            recommended_overviews.append(data[3])
        else:
            recommended_movie_posters.append(get_placeholder_image("Error"))
            recommended_ratings.append("N/A")
            recommended_years.append("N/A")
            recommended_overviews.append("Error loading details.")

    return recommended_movie_names, recommended_movie_posters, recommended_ratings, recommended_years, recommended_overviews, movie_ids


import os
import gdown

# ──────────────────────────────────────────────
# Load Data
# ──────────────────────────────────────────────
def download_similarity_file():
    file_id = '13uR8yGrUmc1wBY4M1uo768xhvvHDesER'
    output = 'similarity.pkl'
    if not os.path.exists(output):
        with st.spinner("🚀 Downloading model data (184MB)... Please wait."):
            url = f'https://drive.google.com/uc?id={file_id}'
            gdown.download(url, output, quiet=False)

download_similarity_file()

movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies['movie_id'] = movies['movie_id'].astype(int)
movie_list = movies['title'].values


# ──────────────────────────────────────────────
# UI Layout
# ──────────────────────────────────────────────

# Hero Header
st.markdown("""
<div class="hero-header">
    <h1>🎬 CineMatch</h1>
    <p>Powered Movie Recommendations</p>
</div>
""", unsafe_allow_html=True)

# Search Section in glass card
st.markdown('<div class="glass-search">', unsafe_allow_html=True)
st.markdown('<p class="search-label">🔍 Search for a movie you love</p>', unsafe_allow_html=True)

selected_movie = st.selectbox(
    "Type or select a movie",
    movie_list,
    label_visibility="collapsed"
)

show_btn = st.button("✨ Get Recommendations")
st.markdown('</div>', unsafe_allow_html=True)

# Recommendations
if show_btn:
    st.markdown("""
    <div class="section-title">
        <h2>🍿 Recommended For You</h2>
        <div class="divider"></div>
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("🎬 Finding the best movies for you..."):
        names, posters, ratings, years, overviews, ids = recommend(selected_movie)

    cols = st.columns(5)

    for col, name, poster, rating, year, overview, tmdb_id in zip(cols, names, posters, ratings, years, overviews, ids):
        with col:
            st.markdown(f"""
            <div class="movie-card">
                <img src="{poster}" alt="{name}"
                     onerror="this.style.display='none'"/>
                <div class="movie-badges">
                    <div class="badge badge-rating">⭐ {rating}</div>
                    <div class="badge badge-year">{year}</div>
                </div>
                <div class="movie-overlay">
                    <h4>Overview</h4>
                    {overview}
                </div>
                <div class="movie-title">
                    {name}
                    <a href="https://www.themoviedb.org/movie/{tmdb_id}" target="_blank" class="movie-link" title="View on TMDB">
                        ➱
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="app-footer">
    CINEMATCH © 2026 — POWERED BY TMDB ✨
</div>
""", unsafe_allow_html=True)