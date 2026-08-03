"""
Streamlit UI for CineScore+ (2.0)

Handles user flows for:
- Searching for movies
- Submitting reviews
- Filtering based on genre tags
- Viewing the movieboard display
- Generating recommendations

Backend logic is handled in backend/backend.py

"""
import sys
import os

# Add repo root to Python path so Streamlit Cloud can find the backend folder
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

import streamlit as st
import pandas as pd
from backend.backend import search_movie, submit_review, generate_movieboard, get_director, get_movie_details, genre_lookup, generate_recommendations, filter_out_reviewed, get_top_genres


st.title("CineScore+ Version 2.0")

# Page Select
option = st.sidebar.selectbox(
    "Choose an action:",
    ["Search", "Review", "Filter by Genre", "View Movieboard", "Recommendations"]
)

# --- SEARCH Page ---
# Allows user to search for movies using TMDB by title and release year (optional).
# Results show posters, overviews and genre tags. Result information is used throughout through session_state().
if option == "Search":
    st.header("Search for a Movie")

    # Search prompts for user
    title = st.text_input("Enter a movie title")
    year = st.text_input("Enter a release year (optional)")

    # Search button behavior
    if st.button("Search"):
        results = search_movie(title, year)
        st.session_state["search_results"] = results

    # Get results and store them for later use
    results = st.session_state.get("search_results", [])

    # Display results
    # TODO: Add multiple page navigation for longer search results
    # TODO: Consider adding loading screen for long API calls
    if results:
        st.subheader("Results")

        for movie in results:
            # Convert genre IDs to words to display names for tags instead of ID
            genre_names = [genre_lookup.get(gid, "Unknown") for gid in movie["genre_ids"]]

              # Display movie poster image, show message if one isn't availible
              # GOTCHA: TMDB sometimes returns movies with no poster_path
            if movie["poster_path"]:
                poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                st.image(poster_url, width=200)
            else:
                st.write("No poster availible.")
            
            st.write(f"**{movie['title']} ({movie['year']})**")
            st.write(movie["overview"])
            st.write(f"Genres: {', '.join(genre_names)}")
            st.write("---")

# --- REVIEW Page ---
# Lets users search for a movie, select it, and submit a review. The rating is done on a slider from 1 to 5 stars.
# Stores reviews in reviews.csv for later use in recommendation system and movieboard display.
elif option == "Review":
    st.header("Review a movie.")

    # 1. Search for a movie
    title = st.text_input("Search for a movie")
    year = st.text_input("Release Year (optional)")

    # Search button behavior
    if st.button("Search"):
        results = search_movie(title, year)
        st.session_state["search_results"] = results
    
    # 2. Show search results
    results = st.session_state.get("search_results", [])

    if results:
        st.subheader("Select a movie to review")

        movie_titles = [f"{m['title']} ({m['year']})" for m in results]
        selected = st.selectbox("Choose a movie", movie_titles)

        # GOTCHA: If TMDB returns movies with the same title, selecting by index might pick the wrong one
        movie = results[movie_titles.index(selected)]

        movie_id = movie["id"]
        movie_title = movie["title"]
        genre_ids = movie["genre_ids"]

        # 3. Input a rating for the review
        rating = st.slider("Your rating", 1, 5)

        # 4. Submit the review
        if st.button("Submit Review"):
            submit_review(movie_id, rating, movie_title, genre_ids)
            st.success("Your review was saved!")
    
# --- FILTER RESULTS BY GENRE Page ---
# Search page, with ability to filter results further based on genre tag
elif option == "Filter by Genre":
    st.header("Filter Movies by Genre")

    # Search bar
    title = st.text_input("Search for a movie")
    year = st.text_input("Enter a release year (optional)")
    
    # Genre menu
    genre_names = list(genre_lookup.values())
    selected_genre = st.selectbox("Choose a genre to filter by", genre_names)

    # Convert genre names to ID for filtering
    genre_id = next(gid for gid, name in genre_lookup.items() if name == selected_genre) # Use next to build full list and avoid issues with duplicate ID numbers
   

    # One button for search and filtering at the same time
    if st.button("Search & Filter"):
        results = search_movie(title, year)


        # Convert genre IDs to integers and standardize ID type
        for m in results:
            clean_ids = []
            for g in m["genre_ids"]:
                try:
                    clean_ids.append(int(g))
                except:
                    pass
            m["genre_ids"] = clean_ids



        # Filter results
        filtered = [m for m in results if genre_id in m["genre_ids"]]

        st.write(f"Filtered down to {len(filtered)} movies")

        st.session_state["genre_filtered_results"] = filtered


    # Display filtered results
    filtered_results = st.session_state.get("genre_filtered_results", [])

    if filtered_results:
        st.subheader(f"Movies filtered by genre: {selected_genre}")

        for movie in filtered_results:
            # Convert genre IDs back to names for display
            genre_names = [genre_lookup.get(gid, "Unknown") for gid in movie["genre_ids"]]

            # Display movie poster
            if movie["poster_path"]:
                poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                st.image(poster_url, width=200)
            else:
                st.write("No poster availible.")

            st.write(f"**{movie['title']} ({movie['year']})**")
            st.write(movie["overview"])
            st.write(f"Genres: {','.join(genre_names)}")
            st.write("----")
    

   

# Movieboard Page
# Pulls review history from reviews.csv, formats them into a leaderboard to show the top 10 rated films.
elif option == "View Movieboard":
    st.header("Movieboard")
    
    board = generate_movieboard()

    # Check for the correct response from the API
    if not board:
        st.write("No reviews found. Submit reviews to view the movieboard.")
    else:
        # Display movieboard
        for movie in board:
            
            # Display movie poster
            if movie["poster_path"]:
                poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                st.image(poster_url, width=200)
            else:
                st.write("No poster available.")
            
            st.subheader(movie["title"])
            st.write(f"Director: {movie['director']}")
            st.write(f"Average Rating: {movie['avg_rating']} ★")
            st.write(f"Review Count: {movie['review_count']}")
            st.write(f"Genres: {', '.join(movie['genres'])}")
            st.write("---")

# Recommendation Page
# Generates personalized movie recommendations based on the top rated genres.
# At least one rating of 4 stars or higher is required. Posters and descriptions are displayed.
elif option == "Recommendations":
    st.header("Looking for something new to watch?")

    # Check if there is reviews present, and they are readable
    try: 
        df_reviews = pd.read_csv("reviews.csv")
    except FileNotFoundError:
        st.error("No reviews found. Review some movies first.")
        st.stop()
    except Exception as e:
        st.error(f"Error reading reviews: {e}")
        st.stop()

    
    # Recommendation button behavior
    if st.button("Give me a recommendation"):
        df_reviews = pd.read_csv("reviews.csv")
        recs = generate_recommendations(df_reviews, genre_lookup)
        st.session_state["recs"] = recs

    # Store recommendations 
    recs = st.session_state.get("recs", [])

    # Check for correct recommendations
    if not recs:
        st.info("No recommendations available yet. Review some movies before asking for a recommendation.")
        st.stop()

    # Display recommendation results
    if recs:
        for movie in recs:
            if movie["poster_path"]:
                poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                st.image(poster_url, width=200)

            st.write(f"**{movie['title']} ({movie['year']})**")
            st.write(movie["overview"])

            genre_names =[genre_lookup.get(gid, "Unknown") for gid in movie["genre_ids"]]
            st.write(f"Genres: {','.join(genre_names)}")
            st.write("---")

    # Show error message if no recommendations availible
    if not recs:
        st.info("No recommendations available yet. Review more movies for a recommendation.")




