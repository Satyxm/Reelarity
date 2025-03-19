import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import ast
from pathlib import Path

def convert(text):
    L = []
    for i in ast.literal_eval(text):
        L.append(i['name'])
    return L

def convert3(text):
    L = []
    count = 0
    for i in ast.literal_eval(text):
        if count < 3:
            L.append(i['name'])
            count += 1
    return L

def fetch_dir(text):
    L = []
    for i in ast.literal_eval(text):
        if i['job'] == 'Director':
            L.append(i['name'])
    return L

def fetch_prod(text):
    L = []
    for i in ast.literal_eval(text):
        L.append(i['name'])
    return L

def remGap(L):
    L1 = []
    for i in L:
        L1.append(i.replace(" ", ""))
    return L1

# Load and preprocess data
def preprocess_data():
    # Check if data files exist
    if not Path("tmdb_5000_movies.csv").exists() or not Path("tmdb_5000_credits.csv").exists():
        raise FileNotFoundError("Please download the TMDB dataset files first")
    
    # Load movies data
    mov = pd.read_csv("tmdb_5000_movies.csv")
    cred = pd.read_csv("tmdb_5000_credits.csv")
    
    # Merge datasets
    cred.rename(columns={'title': 'original_title'}, inplace=True)
    mov = mov.merge(cred, on="original_title")
    
    # Select relevant columns
    mov = mov[['budget', 'homepage', 'id', 'original_language', 'original_title', 
               'genres', 'popularity', 'production_companies', 'cast', 'crew', 
               'vote_average', 'vote_count']]
    
    # Drop rows with missing values
    mov.dropna(inplace=True)
    
    # Process genres
    mov['genres'] = mov['genres'].apply(convert)
    
    # Process cast (top 3 actors)
    mov['cast'] = mov['cast'].apply(convert3)
    
    # Process crew (directors)
    mov['crew'] = mov['crew'].apply(fetch_dir)
    
    # Process production companies
    mov['production_companies'] = mov['production_companies'].apply(fetch_prod)
    
    # Remove spaces from all lists
    mov['cast'] = mov['cast'].apply(remGap)
    mov['crew'] = mov['crew'].apply(remGap)
    mov['genres'] = mov['genres'].apply(remGap)
    mov['production_companies'] = mov['production_companies'].apply(remGap)
    
    # Normalize numerical features
    scaler = MinMaxScaler()
    mov['popularity_norm'] = scaler.fit_transform(mov[['popularity']])
    mov['budget_norm'] = scaler.fit_transform(mov[['budget']])
    mov['vote_score'] = mov['vote_average'] * np.log1p(mov['vote_count'])
    mov['vote_score_norm'] = scaler.fit_transform(mov[['vote_score']])
    
    # Create enhanced tags
    mov['tags'] = mov.apply(lambda x: 
        x['genres'] + 
        [actor for actor in x['cast']] + 
        [director for director in x['crew']] + 
        [company for company in x['production_companies']] +
        [f"popular_{x['popularity_norm']:.2f}"] +
        [f"budget_{x['budget_norm']:.2f}"] +
        [f"vote_{x['vote_score_norm']:.2f}"]
    , axis=1)
    
    # Convert tags to string
    mov['tags'] = mov['tags'].apply(lambda x: " ".join(x))
    
    return mov

def create_recommendation_model():
    try:
        # Preprocess data
        mov = preprocess_data()
        
        # Create TF-IDF vectors
        tfidf = TfidfVectorizer(max_features=5000, stop_words='english')
        vector = tfidf.fit_transform(mov['tags']).toarray()
        
        # Calculate cosine similarity
        similarity = cosine_similarity(vector)
        
        # Save the model and data
        pickle.dump(similarity, open('similarity.pkl', 'wb'))
        pickle.dump(mov.to_dict(), open('movies_dictionary.pkl', 'wb'))
        
        print("Recommendation model created successfully!")
        
    except Exception as e:
        print(f"Error creating recommendation model: {str(e)}")
        raise

if __name__ == "__main__":
    create_recommendation_model() 