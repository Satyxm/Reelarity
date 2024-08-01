import pandas as pd
import requests
import streamlit as st
import pickle

def fetchPoster(id):
    url = f"https://api.themoviedb.org/3/movie/{id}?api_key=338c67d8c97683ce0149f14d5342fb2a"
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie):
    index = mov[mov['original_title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movieName = []
    recommended_moviePosters = []

    for i in distances[1:6]:
        id = mov.iloc[i[0]].id
        recommended_moviePosters.append(fetchPoster(id))
        recommended_movieName.append(mov.iloc[i[0]].original_title)

    return recommended_movieName, recommended_moviePosters


movies_dict = pickle.load(open('movies_dictionary.pkl', 'rb'))
mov = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl', 'rb'))


st.title('REELARITY 🍿')

movList = mov['original_title'].values

selectedMov = st.selectbox(
    "Type the Movie Name",
    mov['original_title'].values,
)

if(st.button('Recommend')):
    recommended_movieName, recommended_moviePosters = recommend(selectedMov)
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.text(recommended_movieName[0])
        st.image(recommended_moviePosters[0])
    with col2:
        st.text(recommended_movieName[1])
        st.image(recommended_moviePosters[1])

    with col3:
        st.text(recommended_movieName[2])
        st.image(recommended_moviePosters[2])
    with col4:
        st.text(recommended_movieName[3])
        st.image(recommended_moviePosters[3])
    with col5:
        st.text(recommended_movieName[4])
        st.image(recommended_moviePosters[4])

