import streamlit as st
from backend import search_movie, submit_review, generate_movieboard, get_director, get_movie_details, genre_lookup


st.title("CineScore+ Ver 2")

# Page Select
option = st.sidebar.selectbox(
    "Choose an action:",
    ["Search", "Review", "Filter by Genre", "View Movieboard"]
)

# Search Page
if option == "Search":
    st.header("Search for a Movie")

    title = st.text_input("Enter a movie title")
    year = st.text_input("Enter a release year (optional)")

    if st.button("Search"):
        results = search_movie(title, year)
        st.session_state["search_results"] = results

    results = st.session_state.get("search_results", [])

    if results:
        st.subheader("Results")

        for movie in results:
            # Convert genre IDs to words to display names
            genre_names = [genre_lookup.get(gid, "Unknown") for gid in movie["genre_ids"]]

            st.write(f"**{movie['title']} ({movie['year']})**")
            st.write(movie["overview"])
            st.write(f"Genres: {', '.join(genre_names)}")
            st.write("---")

# Review Page 
elif option == "Review":
    st.header("Review a movie.")

    # 1. Search for a movie
    title = st.text_input("Search for a movie")
    year = st.text_input("Release Year (optional)")

    if st.button("Search"):
        results = search_movie(title, year)
        st.session_state["search_results"] = results
    
    # 2. Show search results
    results = st.session_state.get("search_results", [])

    if results:
        st.subheader("Select a movie to review")

        movie_titles = [f"{m['title']} ({m['year']})" for m in results]
        selected = st.selectbox("Choose a movie", movie_titles)

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
    
# Filter results by genre page
elif option == "Filter by Genre":
    st.header("Filter Movies by Genre")

    # Search bar
    title = st.text_input("Search for a movie")
    year = st.text_input("Enter a release year (optional)")
    
    # Genre menu
    genre_names = list(genre_lookup.values())
    selected_genre = st.selectbox("Choose a genre to filter by", genre_names)

    # Convert genre names to ID for filtering
    genre_id = [gid for gid, name in genre_lookup.items() if name == selected_genre]

    # Buttons
    search_clicked = st.button("Search")
    filter_clicked = st.button("Filter by Genre")

    # Run search when button is clicked
    if search_clicked:
        results = search_movie(title, year)

        # Convert genre IDs to integers to avoid type issues
        for m in results:
            m["genre_ids"] = [int(g) for g in m["genre_ids"]]
        
        st.session_state["genre_search_results"] = results

    # Filter results
    if filter_clicked:
        results = st.session_state.get("genre_search_results", [])

        if not results:
            st.warning("Please search for a movie before filtering.")
        else:

            filtered = [m for m in results if genre_id in m["genre_ids"]]
            st.session_state["genre_filtered_results"] = filtered
    
    # Display filtered results
    filtered_results = st.session_state.get("genre_filtered_results", [])

    if filtered_results:
        st.subheader(f"Movies filtered by genre: {selected_genre}")

        for movie in filtered_results:
            # Convert genre IDs back to names for display
            genre_names = [genre_lookup.get(gid, "Unknown") for gid in movie["genre_ids"]]

            st.write(f"**{movie['title']} ({movie['year']})**")
            st.write(movie["overview"])
            st.write(f"Genres: {','.join(genre_names)}")
            st.write("----")
    

   

# Movieboard Page
elif option == "View Movieboard":
    st.header("Movieboard")
    
    board = generate_movieboard()

    # Check for the correct response from the API
    if not board:
        st.write("No reviews found. Submit reviews to view the movieboard.")
    else:
        for movie in board:
            st.subheader(movie["title"])
            st.write(f"Director: {movie['director']}")
            st.write(f"Average Rating: {movie['avg_rating']} ★")
            st.write(f"Review Count: {movie['review_count']}")
            st.write(f"Genres: {', '.join(movie['genres'])}")
            st.write("---")


