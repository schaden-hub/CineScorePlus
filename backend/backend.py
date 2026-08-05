"""
Backend logic for CineScore+ (2.0)

This file handles:
- TMDB API communication (searching, details, credits)
- Review storage and formatting for reviews.csv
- Genre lookup and standardization
- Movieboard generation
- Recommendation flow (top genres -> discover API endpoint -> filtering)

All functions here are used by Streamlit UI in frontend/app.py

"""


import requests
import pandas as pd
import ast
import streamlit as st
import os
import json 

TMDB_API_KEY = st.secrets["TMDB_API_KEY"] or os.getenv("TMDB_API_KEY")

BASE_URL = "https://api.themoviedb.org/3"

# Load in csv information
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENRES_PATH = os.path.join(ROOT_DIR, "data", "genres.csv")

df_genres = pd.read_csv(GENRES_PATH)

# Converts TMDB genre CSV into a dictionary for fast ID to nametag mapping
df_genres["id"] = df_genres["id"].astype(int)
genre_lookup = dict(zip(df_genres["id"], df_genres["name"]))



def search_movie(term, year=None):
    """
    Search TMDB for movies matching a title and optional release year.

    Args:
        term (str): Movie title to search for.
        year (str or int, optional): Release year filter.

    Returns:
        list[dict]: List of movie dictionaries containing id, title, poster_path, year, overview and genre_ids.

    Notes:
        GOTCHA: TMDB may return mvoies with missing fields, such as poster_path.
    """
    url = f"{BASE_URL}/search/movie"    

    params = {
        "api_key": TMDB_API_KEY,
        "query": term
    }

    # Include year in search only if the user includes it
    if year:
       params["primary_release_year"] = year

    # TODO: Cache API responses to reduce repeated network calls.
    response = requests.get(url, params=params)

    # Check to make sure results are actually being sent
    if response.status_code != 200:
        print("Error: ", response.status_code)
        print(response.text)
        return []


    data = response.json()

    # If something is returned that isn't expected
    if "results" not in data or data["results"] is None:
        print("TMDB returned no results.")
        print(data)
        return []
    
    results = data.get("results", [])
    # TODO : Add error handling for incorrect reviews.csv rows.

    # Format result output
    movies = []
    for m in results:
        movies.append({
            "id": m["id"],
            "title": m["title"],
            "poster_path": m.get("poster_path"),
            "year": (m.get("release_date") or "")[:4],
            "overview": m.get("overview", ""),
            "genre_ids": m.get("genre_ids", [])
        })



    return movies


def get_director(movie_id):
    
    """
    Fetch the director's name for a given movie using the TMDB credits endpoint. Used for movieboard.

        Args:
            movie_id (int): TMDB movie ID.
    
        Returns:
            str: Director name, or "Unknown" if not found.
        
        Notes:
            GOTCHA: Some movies have multiple 'Director' roles or none listed.
    """
    # Set endpoint for director info
    url = f"{BASE_URL}/movie/{movie_id}/credits"
    params = {"api_key": TMDB_API_KEY}

    response = requests.get(url, params=params)

    # Check to make sure API is returning needed information
    if response.status_code != 200:
        print("Error getting director info:", response.status_code)
        return "Unknown"
    
    data = response.json()

    # Get crew data
    crew = data.get("crew", [])

    # Loop through crew list to find director
    for person in crew:
        if person.get("job") == "Director":
            return person.get("name", "Unknown")
        
    # Return Director name
    return "Unknown"


def submit_review(movie_id, rating, movie_title, genre_ids=None):

    """
    Append a new review to reviews.csv, creating the file if needed.

        Args:
            movie_id (int): TMDB movie ID.
            rating (float): User 'star' rating from 1 to 5.
            movie_title (str): Movie title.
            genre_ids (list[int], optional): Genre IDs associated with the movie.
        
        Notes:
            TODO: Consider validating reviews or updating existing ones.

    """
    # Validate User review
    if rating < 1 or rating > 5:
        print("You must pick between 1 and 5 stars.")
        return

    # Fetch real TMDB details to fix poster issue with movieboard
    details = get_movie_details(movie_id)
    real_id = details.get("id", movie_id)
    real_genres = details.get("genre_ids", genre_ids or [])
    
    # Load existing reviews (if any)
    try:
        df = pd.read_csv("reviews.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["movie_id", "title", "rating", "genre_ids"])


    # Add a new row for the new review
    new_row = {
        "movie_id": real_id,
        "title": movie_title,
        "rating": float(rating),
        "genre_ids": json.dumps(real_genres)
    }

    # Add new review to the bottom of reviews.csv
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save new review to reviews.csv
    df.to_csv("reviews.csv", index=False)
    print("Your review was saved!")


def get_movie_details(movie_id):
    """
    Retrieve detailed TMDB metadata for a movie.

        Args:
            movie_id (int): TMDB Movie ID.

        Returns:
            dict: Movie details including standardized genre_ids.
        
        Notes:
            GOTCHA: TMDB may return unexpected formats or missing fields.
    """
    # Get movie details from TMDB
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY
    }

    # Check to make sure network connects to API
    try:
        response = requests.get(url, params=params)
    except Exception as e:
        print("Network error while fetching movie details:", e)
        return {}

    # Check to make sure request is fufilled by TMDB API
    if response.status_code != 200:
        print("TMDB request error:", response.status_code)
        return {}

    data = response.json()

    # Catch missing or incorrect TMDB responses
    if not isinstance(data, dict):
        print("Invalid TMDB response format for movie:", movie_id)
        return {}


    # Save poster path
    poster_path = data.get("poster_path")

    # Convert TMDB "genres" objects to "genre_ids" 
    data = standardize_genre_ids(data)

    # Add poster_path back into returned dictionary
    data["poster_path"] = poster_path
    
    # Return details
    return data


def movies_with_genre(df_movies, genre_id):
    """
    Filter a Dataframe of movies by specific genre ID.

        Args:
            df_movies (pd.DataFrame): Movie data.
            genre_id (int): Genre ID to filter by.
    
        Returns:
            pd.DataFrame: Filtered movies by the specified genre.
    """
    # Filter results by user selected genre
    return df_movies[df_movies["genre_ids"].apply(lambda g: genre_id in g)]


def generate_movieboard(top_n=10):
    """
    Create a movieboard based on user's top rated movies.

        Args:
            top_n (int): Number of top rated movies to display.
    
        Returns:
            list[dict]: Movieboard containing title, director, avg_rating , review_count, and genres.

        Notes:
            GOTCHA: TMDB may fail to return details for older or more obscure movies.
    """
    # Read reviews.csv and check to see if there is reviews
    try:
        df = pd.read_csv("reviews.csv")
    except FileNotFoundError:
        print("No reviews yet.")
        return
    
    # No reviews present?
    if df.empty:
        print("No reviews yet.")
        return
    
    # Convert genre_ids back to lists
    df["genre_ids"] = df["genre_ids"].apply(lambda x: ast.literal_eval(x) if x else []) # Add space if no genre id is present
    
    # Group movies by movie_id to calculate avg rating and counts
    grouped_ID = df.groupby("movie_id")["rating"].agg(["mean", "count"]).reset_index()
    grouped_ID = grouped_ID.sort_values(by=["mean", "count"], ascending=[False, False])

    movieboard = []

    # Show top movies based on set value (n)
    print("Top movies:")
    for i, row in grouped_ID.head(top_n).iterrows():
        movie_id = int(row["movie_id"])
        avg = row["mean"]
        review_count = int(row["count"])

        # Get movie title from TMDB 
        details = get_movie_details(movie_id)
        title = details.get("title", "Unknown title")


        # Convert TMDB Genre IDs to words
        tmdb_genres = details.get("genres", [])
        genre_names = [genre_lookup[g["id"]] for g in tmdb_genres if g["id"] in genre_lookup]

        # Add placeholder if no genre tags present
        if not genre_names:
            genre_names = ["No genre tags available"]

        
        # Get director name using get_director()
        director = get_director(movie_id)

        # Assemble movieboard entry
        movie_entry = {
            "movie_id": movie_id,
            "title": title,
            "avg_rating": float(round(avg, 2)),
            "review_count": review_count,
            "genres": genre_names,
            "director": director,
            # "poster": poster_url,  # Commented out until fixed in future, became larger issue
            "debug_details": details # Debug for poster issue

        }

        # Add entry to final board
        movieboard.append(movie_entry)


    return movieboard

def standardize_genre_ids(details):
    """
    Convert TMDB 'genres' objects into a flat list of genre_ids.
        Args:
            details (dict): TMDB movie details dictionary.

        Returns:
              dict: Updated details with genre_ids included.
    """
    # If TMDB returns "genres" objects, convert them to genre_ids for ease of use
    if "genres" in details and isinstance(details["genres"], list):
        details["genre_ids"] = [g["id"] for g in details["genres"]]
    return details

# --- Full recommendation flow: top genres -> discover API -> filtering ---

def get_top_genres(df_reviews, genre_lookup):
    """
    Identify the user's top genres based on movie rated 4+ 'stars'.

        Args:
            df_reviews (pd.DataFrame): User review data.
            genre_lookup (dict): Mapping of genre IDs to genre name tags.
    
        Returns:
            list[int]: Top 2 genre IDs sorted by frequency.
        
        Notes:
            TODO: Consider weighting genres by rating strength.
    """
    # CSV check for content
    if df_reviews.empty:
        print("CSV is empty. Make a review.")
        return []


    # Identify highest rated movies >= 4 stars
    high_rated = df_reviews[df_reviews["rating"] >= 4]

    # No high rated movies present?
    if high_rated.empty:
        print("No high rated movies.")
        return []
    
    genre_counts = {}

    for _, row in high_rated.iterrows():
        movie_id = row["movie_id"]
        details = get_movie_details(movie_id)

        # Skip entry if API fails
        if not details or "genre_ids" not in details:
            print("Skipping movie, no genre_ids:", movie_id)
            continue

        # Count genres to find top genres
        for gid in details["genre_ids"]:
            genre_counts[gid] = genre_counts.get(gid, 0) + 1
        
    # Sort counted genres by frequency
    print("Genre  counts:", genre_counts)

    # Stop if no genres are counted
    if not genre_counts:
        print("No genres counted from high-rated movies.")
        return []

    # Sort genres with sorted()
    sorted_genres = sorted(genre_counts, key=genre_counts.get, reverse=True)
 
    return sorted_genres[:2] # Return top 2 genres
    
def recommend_movies_by_genre(top_genres):
    """
    Use TMDB Discover API to get popular movies for each of the user's top genres.

        Args:
            top_genres (list[int]): Genre IDs to recommend movies from.
    
        Returns:
            list[dict]: Raw recommended movie dictionaries.
        
        Notes:
            GOTCHA: Discover API may return adult content unless it is filtered.
    """
    recommended = []

    for gid in top_genres:
        # Setup endpoint for recommendations
        url = f"{BASE_URL}/discover/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "with_genres": gid,
            "sort_by": "popularity.desc",
            "include_adult": True,
            "language": "en-US",
            "page": 1
        }

        # Return error if API does not return expected response
        try:
            data = requests.get(url, params=params).json()
        except:
            print("Discover API failed for genre:", gid)
            continue

        # Print out genre if there is an issue with results
        if "results" not in data or not data["results"]:
            print("No results returned for genre:", gid)
            continue

        # Format recommendations
        # GOTCHA: TMDB Discover API may return movies with no release_date.
        for m in data.get("results", []):
            recommended.append({
                "title": m.get("title"),
                "year": m.get("release_date", "")[:4],
                "overview": m.get("overview"),
                "genre_ids": m.get("genre_ids", []),
                "poster_path": m.get("poster_path"),
                "id": m.get("id")
            })

    # No recommendations found?
    if not recommended:
        print("No recommended movies found for top genres.")
    
    return recommended

def filter_out_reviewed(recomended, df_reviews):
    """
    Remove movies from recommendations that the user has already reviewed.

        Args:
            recommended (list[dict]): Raw recommended movies.
            df_reviews (pd.DataFrame): User review data from csv.
    
        Returns:
            list[dict]: Filtered recommendations.
    """
    # Filter out movies user already reviewed
    reviewed_ids = set(df_reviews["movie_id"].tolist())
    return [m for m in recomended if m["id"] not in reviewed_ids]

def generate_recommendations(df_reviews, genre_lookup):
    """
    Full recommendation flow:
    - Identify top genres using get_top_genres()
    - Fetch movies from TMDB Discover API
    - Filter out previously reviewed films
    - Return top 10 recommendations

        Args:
            df_reviews (pd.DataFrame): User review data.
            genre_lookup (dict): Mapping genre IDs to name tags.
    
        Returns:
            list[dict]: Final curated recommendations.
    """
    
    # Show error if previous steps in recommendation process fail
    try:
        top_genres = get_top_genres(df_reviews, genre_lookup)
    except Exception as e:
        print("Error generating top genres:", e)

    # Check to see if top genres are present
    if not top_genres:
        return []
    
    # Get recommendations
    recs = recommend_movies_by_genre(top_genres)

    # Check to make sure recs are there
    if not recs:
        print("No raw recommendations returned.")
        return []
    
    # Make sure no previously logged movies are present
    final_recs = filter_out_reviewed(recs, df_reviews)

    # Final check to make sure recs are present
    if not final_recs:
        print("All recommended movies were already reviewed.")
        return []

    return final_recs[:10] # Show top 10 recomendations
        

    


