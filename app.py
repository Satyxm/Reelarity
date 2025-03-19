import pandas as pd
import requests
import streamlit as st
import pickle
from streamlit_option_menu import option_menu
import time
from PIL import Image
import io
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Reelarity - Movie Recommender",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
    @keyframes gradient {
        0% {
            background-position: 0% 50%;
        }
        50% {
            background-position: 100% 50%;
        }
        100% {
            background-position: 0% 50%;
        }
    }
    
    @keyframes glow {
        0% {
            box-shadow: 0 0 5px #E50914, 0 0 10px #E50914, 0 0 15px #E50914;
        }
        50% {
            box-shadow: 0 0 10px #E50914, 0 0 20px #E50914, 0 0 30px #E50914;
        }
        100% {
            box-shadow: 0 0 5px #E50914, 0 0 10px #E50914, 0 0 15px #E50914;
        }
    }

    .stApp {
        background-color: #000000 !important;
        color: #FFFFFF !important;
    }
    .main .block-container {
        background-color: #000000 !important;
    }
    .stMarkdown {
        background-color: #000000 !important;
    }
    .stSelectbox {
        background-color: #000000 !important;
    }
    .stSelectbox > div > div {
        background-color: #1A1A1A !important;
        border: 1px solid #333333 !important;
    }
    .stSelectbox > div > div:hover {
        border-color: #E50914 !important;
    }
    .stSelectbox > div > div:focus {
        border-color: #E50914 !important;
    }
    .movie-card {
        background: linear-gradient(-45deg, #1A1A1A, #2A2A2A, #1A1A1A, #2A2A2A);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(229, 9, 20, 0.1);
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.5);
    }
    .movie-card:hover {
        transform: scale(1.05);
        animation: glow 2s ease-in-out infinite;
        border: 1px solid rgba(229, 9, 20, 0.3);
        box-shadow: 0 0 30px rgba(229, 9, 20, 0.2);
    }
    .movie-title {
        color: #FFFFFF;
        font-size: 1.2em;
        font-weight: bold;
        margin: 10px 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        text-shadow: 0 0 10px rgba(229, 9, 20, 0.5);
    }
    .movie-poster {
        width: 100%;
        height: 300px;
        object-fit: cover;
        border-radius: 5px;
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
    }
    .movie-card:hover .movie-poster {
        transform: scale(1.05);
    }
    .movie-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(0, 0, 0, 0.98), rgba(229, 9, 20, 0.2));
        padding: 20px;
        color: white;
        opacity: 0;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        backdrop-filter: blur(5px);
    }
    .movie-card:hover .movie-overlay {
        opacity: 1;
    }
    .movie-detail {
        margin: 10px 0;
        font-size: 1.1em;
        width: 100%;
        transform: translateY(20px);
        opacity: 0;
        transition: all 0.3s ease;
    }
    .movie-card:hover .movie-detail {
        transform: translateY(0);
        opacity: 1;
    }
    .movie-detail-title {
        font-weight: bold;
        color: #E50914;
        margin-bottom: 5px;
        font-size: 1.2em;
        text-shadow: 0 0 10px rgba(229, 9, 20, 0.5);
    }
    .movie-detail-content {
        color: #FFFFFF;
        font-size: 1em;
        text-shadow: 0 0 5px rgba(255, 255, 255, 0.3);
    }
    .stButton>button {
        background: linear-gradient(45deg, #E50914, #B1060F) !important;
        color: white !important;
        border: none !important;
        padding: 10px 20px !important;
        border-radius: 5px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 0 10px rgba(229, 9, 20, 0.3) !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 20px rgba(229, 9, 20, 0.5) !important;
    }
    .stButton>button:focus {
        box-shadow: 0 0 15px rgba(229, 9, 20, 0.4) !important;
    }
    .stButton>button:active {
        transform: translateY(1px);
        box-shadow: 0 0 5px rgba(229, 9, 20, 0.3) !important;
    }
    .sidebar .sidebar-content {
        background-color: #000000 !important;
        border-right: 1px solid #333333;
    }
    .sidebar .nav-item {
        margin: 1rem 0;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: all 0.3s ease;
        color: #FFFFFF !important;
    }
    .sidebar .nav-item:hover {
        background-color: #1A1A1A !important;
        color: #E50914 !important;
    }
    .sidebar .nav-item.active {
        background-color: #E50914 !important;
        color: #FFFFFF !important;
    }
    /* Responsive Design */
    @media screen and (max-width: 1400px) {
        .movie-poster {
            height: 250px;
        }
    }
    @media screen and (max-width: 1200px) {
        .movie-poster {
            height: 220px;
        }
        .movie-title {
            font-size: 1.1em;
        }
    }
    @media screen and (max-width: 992px) {
        .movie-poster {
            height: 200px;
        }
        .movie-title {
            font-size: 1em;
        }
    }
    @media screen and (max-width: 768px) {
        .movie-poster {
            height: 180px;
        }
        .movie-title {
            font-size: 0.9em;
        }
    }
    @media screen and (max-width: 576px) {
        .movie-poster {
            height: 160px;
        }
        .movie-title {
            font-size: 0.8em;
        }
    }
    </style>
""", unsafe_allow_html=True)

def fetchPoster(movie_id):
    try:
        api_key = os.getenv('TMDB_API_KEY', '8265bd1679663a7ea12ac168da84d2e8')  # Fallback for demo purposes
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        
        if 'poster_path' not in data or data['poster_path'] is None:
            # Return a default poster URL if no poster is available
            return "https://via.placeholder.com/500x750?text=No+Poster+Available"
            
        poster_path = data['poster_path']
        full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
        return full_path
    except requests.RequestException as e:
        st.error(f"Error fetching poster: {str(e)}")
        return "https://via.placeholder.com/500x750?text=Error+Loading+Poster"
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        return "https://via.placeholder.com/500x750?text=Error+Loading+Poster"

def recommend(movie):
    try:
        index = movies[movies['original_title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommended_movies = []
        recommended_posters = []
        recommended_details = []
        
        for i in distances[1:11]:
            movie_id = movies.iloc[i[0]].id
            movie_data = movies.iloc[i[0]]
            recommended_movies.append(movie_data.original_title)
            recommended_posters.append(fetchPoster(movie_id))
            
            # Get additional details
            try:
                api_key = os.getenv('TMDB_API_KEY', '8265bd1679663a7ea12ac168da84d2e8')
                url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
                response = requests.get(url)
                data = response.json()
                
                # Extract release year
                release_date = data.get('release_date', '')
                release_year = release_date.split('-')[0] if release_date else 'N/A'
                
                # Extract genres with fallback
                genres = [genre['name'] for genre in data.get('genres', [])]
                if not genres:
                    # Default genres based on movie data
                    if 'overview' in data:
                        overview = data['overview'].lower()
                        if any(word in overview for word in ['action', 'fight', 'war', 'battle']):
                            genres.append('Action')
                        if any(word in overview for word in ['comedy', 'funny', 'laugh', 'humor']):
                            genres.append('Comedy')
                        if any(word in overview for word in ['drama', 'emotional', 'life']):
                            genres.append('Drama')
                        if any(word in overview for word in ['romance', 'love', 'relationship']):
                            genres.append('Romance')
                        if any(word in overview for word in ['horror', 'scary', 'fear', 'thriller']):
                            genres.append('Horror')
                        if any(word in overview for word in ['sci-fi', 'science', 'future']):
                            genres.append('Science Fiction')
                        if any(word in overview for word in ['fantasy', 'magic', 'supernatural']):
                            genres.append('Fantasy')
                        if any(word in overview for word in ['crime', 'police', 'detective']):
                            genres.append('Crime')
                        if any(word in overview for word in ['documentary', 'real', 'true']):
                            genres.append('Documentary')
                        if any(word in overview for word in ['animation', 'cartoon', 'animated']):
                            genres.append('Animation')
                        if not genres:
                            genres.append('General')
                
                genres_str = ', '.join(genres[:3])  # Limit to 3 genres
                
                details = {
                    'genres': genres_str,
                    'year': release_year
                }
            except Exception as e:
                details = {
                    'genres': 'General',
                    'year': 'N/A'
                }
            
            recommended_details.append(details)
            
        return recommended_movies, recommended_posters, recommended_details
    except IndexError:
        st.error("Movie not found in the database")
        return [], [], []
    except Exception as e:
        st.error(f"Error generating recommendations: {str(e)}")
        return [], [], []

# Load data
try:
    movies = pd.read_pickle('movies_dictionary.pkl')
    similarity = pd.read_pickle('similarity.pkl')
    
    # Convert dictionary to DataFrame if needed
    if isinstance(movies, dict):
        movies = pd.DataFrame(movies)
    
except FileNotFoundError as e:
    st.error("Required data files not found. Please make sure 'movies_dictionary.pkl' and 'similarity.pkl' exist.")
    st.stop()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Sidebar navigation
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h2 style='color: #E50914;'>🎬 Reelarity</h2>
        </div>
    """, unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=["Home", "Search", "About"],
        icons=["house", "search", "info-circle"],
        menu_icon="film",
        default_index=0,
    )

if selected == "Home":
    st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>Movie Recommender</h2>", unsafe_allow_html=True)

    # Search functionality
    movie_list = movies['original_title'].values
    selected_movie = st.selectbox(
        "Type or select a movie from the dropdown",
        movie_list
    )

    if st.button('Show Recommendation'):
        recommended_movies, recommended_posters, recommended_details = recommend(selected_movie)
        
        if recommended_movies and recommended_posters:
            # First row of 5 movies
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{recommended_posters[0]}" class="movie-poster">
                        <div class="movie-title">{recommended_movies[0]}</div>
                        <div class="movie-overlay">
                            <div class="movie-detail">
                                <div class="movie-detail-title">Year</div>
                                <div class="movie-detail-content">{recommended_details[0]['year']}</div>
                            </div>
                            <div class="movie-detail">
                                <div class="movie-detail-title">Genres</div>
                                <div class="movie-detail-content">{recommended_details[0]['genres']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{recommended_posters[1]}" class="movie-poster">
                        <div class="movie-title">{recommended_movies[1]}</div>
                        <div class="movie-overlay">
                            <div class="movie-detail">
                                <div class="movie-detail-title">Year</div>
                                <div class="movie-detail-content">{recommended_details[1]['year']}</div>
                            </div>
                            <div class="movie-detail">
                                <div class="movie-detail-title">Genres</div>
                                <div class="movie-detail-content">{recommended_details[1]['genres']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{recommended_posters[2]}" class="movie-poster">
                        <div class="movie-title">{recommended_movies[2]}</div>
                        <div class="movie-overlay">
                            <div class="movie-detail">
                                <div class="movie-detail-title">Year</div>
                                <div class="movie-detail-content">{recommended_details[2]['year']}</div>
                            </div>
                            <div class="movie-detail">
                                <div class="movie-detail-title">Genres</div>
                                <div class="movie-detail-content">{recommended_details[2]['genres']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{recommended_posters[3]}" class="movie-poster">
                        <div class="movie-title">{recommended_movies[3]}</div>
                        <div class="movie-overlay">
                            <div class="movie-detail">
                                <div class="movie-detail-title">Year</div>
                                <div class="movie-detail-content">{recommended_details[3]['year']}</div>
                            </div>
                            <div class="movie-detail">
                                <div class="movie-detail-title">Genres</div>
                                <div class="movie-detail-content">{recommended_details[3]['genres']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col5:
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{recommended_posters[4]}" class="movie-poster">
                        <div class="movie-title">{recommended_movies[4]}</div>
                        <div class="movie-overlay">
                            <div class="movie-detail">
                                <div class="movie-detail-title">Year</div>
                                <div class="movie-detail-content">{recommended_details[4]['year']}</div>
                            </div>
                            <div class="movie-detail">
                                <div class="movie-detail-title">Genres</div>
                                <div class="movie-detail-content">{recommended_details[4]['genres']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            # Second row of 5 movies
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{recommended_posters[5]}" class="movie-poster">
                        <div class="movie-title">{recommended_movies[5]}</div>
                        <div class="movie-overlay">
                            <div class="movie-detail">
                                <div class="movie-detail-title">Year</div>
                                <div class="movie-detail-content">{recommended_details[5]['year']}</div>
                            </div>
                            <div class="movie-detail">
                                <div class="movie-detail-title">Genres</div>
                                <div class="movie-detail-content">{recommended_details[5]['genres']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{recommended_posters[6]}" class="movie-poster">
                        <div class="movie-title">{recommended_movies[6]}</div>
                        <div class="movie-overlay">
                            <div class="movie-detail">
                                <div class="movie-detail-title">Year</div>
                                <div class="movie-detail-content">{recommended_details[6]['year']}</div>
                            </div>
                            <div class="movie-detail">
                                <div class="movie-detail-title">Genres</div>
                                <div class="movie-detail-content">{recommended_details[6]['genres']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{recommended_posters[7]}" class="movie-poster">
                        <div class="movie-title">{recommended_movies[7]}</div>
                        <div class="movie-overlay">
                            <div class="movie-detail">
                                <div class="movie-detail-title">Year</div>
                                <div class="movie-detail-content">{recommended_details[7]['year']}</div>
                            </div>
                            <div class="movie-detail">
                                <div class="movie-detail-title">Genres</div>
                                <div class="movie-detail-content">{recommended_details[7]['genres']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col4:
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{recommended_posters[8]}" class="movie-poster">
                        <div class="movie-title">{recommended_movies[8]}</div>
                        <div class="movie-overlay">
                            <div class="movie-detail">
                                <div class="movie-detail-title">Year</div>
                                <div class="movie-detail-content">{recommended_details[8]['year']}</div>
                            </div>
                            <div class="movie-detail">
                                <div class="movie-detail-title">Genres</div>
                                <div class="movie-detail-content">{recommended_details[8]['genres']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            with col5:
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{recommended_posters[9]}" class="movie-poster">
                        <div class="movie-title">{recommended_movies[9]}</div>
                        <div class="movie-overlay">
                            <div class="movie-detail">
                                <div class="movie-detail-title">Year</div>
                                <div class="movie-detail-content">{recommended_details[9]['year']}</div>
                            </div>
                            <div class="movie-detail">
                                <div class="movie-detail-title">Genres</div>
                                <div class="movie-detail-content">{recommended_details[9]['genres']}</div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

elif selected == "Search":
    st.title("Search Movies")
    search_term = st.text_input("Enter a movie title")
    
    if search_term:
        filtered_movies = movies[movies['original_title'].str.contains(search_term, case=False, na=False)]
        if not filtered_movies.empty:
            for _, movie in filtered_movies.iterrows():
                poster_url = fetchPoster(movie['id'])
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{poster_url}" class="movie-poster">
                        <div class="movie-title">{movie['original_title']}</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No movies found matching your search.")

else:  # About
    st.title("About Reelarity")
    st.markdown("""
        Reelarity is an AI-powered movie recommendation system that helps you discover new movies based on your preferences.
        
        ### Features:
        - Personalized movie recommendations
        - Beautiful, Netflix-inspired interface
        - Search functionality
        - Detailed movie information
        
        ### How it works:
        Our recommendation system uses advanced machine learning algorithms to analyze movie features including:
        - Genre
        - Cast and crew
        - Production companies
        - Budget and revenue
        - Release date
        
        This helps us provide you with the most relevant movie suggestions based on your interests.
    """)
    
    # Technical Information
    st.markdown("### Technical Details")
    st.write("Total number of movies in database:", len(movies))
    st.write("Sample movie data structure:")
    st.dataframe(movies.head(1))

