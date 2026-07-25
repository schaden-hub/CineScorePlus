import requests
import pandas as pd
import ast

from keys import TMDB_API_KEY

BASE_URL = "https://api.themoviedb.org/3"

# Load in csv information
df_genres = pd.read_csv("genres.csv")
df_genres["id"] = df_genres["id"].astype(int)
genre_lookup = dict(zip(df_genres["id"], df_genres["name"]))



def search_movie(term, year=None):
    url = f"{BASE_URL}/search/movie"    

    params = {
        "api_key": TMDB_API_KEY,
        "query": term
    }

    # Include year in search only if the user includes it
    if year:
       params["primary_release_year"] = year

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
        
    return "Unknown"


def submit_review(movie_id, rating, movie_title, genre_ids=None):
    # Validate User review
    if rating < 1 or rating > 5:
        print("You must pick between 1 and 5 stars.")
        return
    
    # Load existing reviews (if any)
    try:
        df = pd.read_csv("reviews.csv")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["movie_id", "title", "rating", "genre_ids"])

    # Check to see if there is genre ids, add space if none
    if genre_ids is None:
        genre_ids_str = ""
    else:
        genre_ids_str = str(genre_ids)

    # Add a new row for the new review
    new_row = {
        "movie_id": movie_id,
        "title": movie_title,
        "rating": float(rating),
        "genre_ids": genre_ids_str
    }
    # Add new review to the bottom of reviews.csv
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save new review to reviews.csv
    df.to_csv("reviews.csv", index=False)
    print("Your review was saved!")


def get_movie_details(movie_id):

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

    # Convert TMDB "genres" objects to "genre_ids" 
    data = standardize_genre_ids(data)
    
    # Return details
    return data


def movies_with_genre(df_movies, genre_id):
    # Filter results by user selected genre
    return df_movies[df_movies["genre_ids"].apply(lambda g: genre_id in g)]


def generate_movieboard(top_n=10):
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
    
    # group movies by ID
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
            "id": movie_id,
            "title": title,
            "avg_rating": float(round(avg, 2)),
            "review_count": review_count,
            "genres": genre_names,
            "director": director

        }

        # Add entry to final board
        movieboard.append(movie_entry)


    return movieboard

def standardize_genre_ids(details):
    # If TMDB returns "genres" objects, convert them to genre_ids for ease of use
    if "genres" in details and isinstance(details["genres"], list):
        details["genre_ids"] = [g["id"] for g in details["genres"]]
    return details

def get_top_genres(df_reviews, genre_lookup):

    # CSV check for content
    if df_reviews.empty:
        print("CSV is empty. Make a review.")
        return []


    # Identify highest rated movies >= 4 stars
    high_rated = df_reviews[df_reviews["rating"] >= 4]

    # No high rated movies present
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

    if not genre_counts:
        print("No genres counted from high-rated movies.")
        return []
    
    sorted_genres = sorted(genre_counts, key=genre_counts.get, reverse=True)
 
    return sorted_genres[:2] # Return top 2 genres
    
def recommend_movies_by_genre(top_genres):
    recommended = []

    for gid in top_genres:
        url = f"{BASE_URL}/discover/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "with_genres": gid,
            "sort_by": "popularity.desc",
            "include_adult": True,
            "language": "en-US",
            "page": 1
        }


        try:
            data = requests.get(url, params=params).json()
        except:
            print("Discover API failed for genre:", gid)
            continue

        # Print out genre if there is an issue with results
        if "results" not in data or not data["results"]:
            print("No results returned for genre:", gid)
            continue

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
    # Filter out movies user already reviewed
    reviewed_ids = set(df_reviews["movie_id"].tolist())
    return [m for m in recomended if m["id"] not in reviewed_ids]

def generate_recommendations(df_reviews, genre_lookup):

    try:
        top_genres = get_top_genres(df_reviews, genre_lookup)
    except Exception as e:
        print("Error genreating top genres:", e)

    # Check to see if top genres are present
    if not top_genres:
        return []
    
    recs = recommend_movies_by_genre(top_genres)

    # Check to make sure recs are there
    if not recs:
        print("No raw recommendations returned.")
        return []
    
    final_recs = filter_out_reviewed(recs, df_reviews)

    # Final check to make sure recs are present
    if not final_recs:
        print("All recommended movies were already reviewed.")
        return []

    return final_recs[:10] # Top 10 recomendations
        

    


