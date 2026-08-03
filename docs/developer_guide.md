# CineScore+ Developer Guide (v2.0)

   ## Overview
   CineScore+ is a movie review app for film buffs with options to search for movies, review them, view a Movieboard to show top rated films, and get personalized recommendations based on their top reviewed films. Functionality is derived from using Python, Streamlit, and the TMDB API. 

   Users are able to:
   - Search for movies
   - Submit ratings for reviews
   - Filter movies by a genre tag
   - View a personalized Movieboard based on review history
   - Receive recommendations based on top rated genres

   The application consists of a backend .py file that handles API communication, data processing, and the recommendation flow, and a frontend .py file (app.py)  that provides an interactive experience using Streamlit. Data is stored locally using CSV files (reviews.csv and genres.csv), and TMDB provides external movie data. 
   
   ## Project Structure
   CINESCOREPLUS/

        backend/
            backend.py      # TMDB API calls, review storage, Movieboard processing, recommendations
        
        frontend/
            app.py          # Streamlit UI logic and page flows (run this using Streamlit command)
        
        data/
            genres.csv      # TMDB genre lookup table
            reviews.csv     # User review storage
        
        docs/
            developer_guide.md      # This document
        
        keys.py                     # TMDB API key
        requirements.txt            # Python dependencies
        README.md                   # User guide

   ## Installation and Setup
   ### Requirements
   - Python 3.13+
   - pip package manager
   - TMDB API key
   ### Install Dependencies
   ```bash
   pip install -r requirements.txt
   ```
   ### Add TMDB API Key
   NOTICE: You must generate your own TMDB API Key.
   1. Go to the TMDB website: https://www.themoviedb.org
   2. Create a free account if you don't already have one.
   3. Navigate to Settings/API/Request an API Key
   4. Choose Developer key (free).
   5. Once approved, you will see your API Read Access Token and API Key (v3 auth).

   Use the API Key (v3 auth) for CineScore+.

   Create keys.py, and insert this line

   ```python
   TMDB_API_KEY = "your_api_key_here"
   ```
   Make sure this file is not committed to public repos.

   ### Run the Application 
   #### Setup on Streamlit Community Cloud
   CineScore+ is currently deployed on Streamlit Community Cloud. For reference, here are the steps to deploy the app on Streamlit Community Cloud. NOTE: You will need access to the repo to be able to redeploy this app. 

   1. Sign into Streamlit Community Cloud with Github.
   2. Choose the app entry point. For this project the path is:
        frontend/app.py
   3. Add API key in "secrets".
   Streamlit Cloud allows you to enter API keys as a part of the app setup for deployment. When prompted to enter any "secrets" enter this:
   ```python
   TMDB_API_KEY = your_api_key_here
   ```
   4. Deploy the app
   Click save to advance and launch the app.

   #### After Deployment
   - The app runs online through the Streamlit Community Cloud.
   - Any updates to the repo are pushed automatically to the Streamlit Community Cloud.
   - TMDB API Key is accessed and stored in secrets using st.secrets["TMDB_API_KEY"].

   NOTE: The app may become inactive if left for extended periods of time, simply click the button to reboot if this happens.

   ## Backend Architecture
   CineScore+'s backend is responsible for all data processing, TMDB communication, review storage, and recommendation flow. The functions in backend/backend.py are imported into frontend.py to wire the logic to the Streamlit UI.

   ### Overview
   The backend provides:
   - A genre lookup system using genres.csv
   - Review storage using reviews.csv
   - Movieboard generation logic
   - A personalized recommendation flow based on top rated genres.

   ### TMDB API Layer
   CineScore+ communicates with TMDB using HTTPS requests. The API key is stored using Streamlit Community Cloud's secrets feature. The key is accessed in code using:
   ```python
   TMDB_API_KEY = st.secrets["TMDB_API_KEY"]
   ```
   #### Key Functions
   - search_movie(title, year=None)
   Searches TMDB for a matching title from user input, and returns a list of matching films with basic metadata.

   - get_movie_details(movie_id)
   Grabs movie details including genres, runtime, release date, poster and overview. 

   - get_director(movie_id)
   Gets crew information and pulls director name for Movieboard.

   - recommend_movies_by_genre(genre_id)
   Use TMDB's Discover API to fetch movies associated with a specific genre. 

   Developer Notes:
   - All API calls use requests.get()
   - Responses are validated for missing fields
   - TMDB genre IDs are numeric and require mapping to name tags
   - Poster URLs are constructed using TMDB's image base URL

   ### Genre Lookup System
   TMDB returns genres as numeric IDs. CineScore+ converts these into name tags for readability. A lookup table (data/genres.csv) is used for conversion.

   - The CSV is loaded using an absolute path to avoid issues with Streamlit Community Cloud's working directory.
   - IDs are cast to integers
   - A dictionary is constructed.
   ```python
   genre_lookup = dict(zip(df_genres["id"], df_genres["name"]))
   ```
   This lookup supports:
   - Displaying genre names in search results
   - Storing genre IDs with reviews
   - Computing top genres for the recommendation flow

   ### Review Storage
   User reviews are stored in data/reviews.csv. The file acts as a database for most data flows within the application

    - submit_review(movie_id, title, rating, genre_ids)
    Adds a new review to the CSV. If the file does not exist, it is created automatically.

    #### Data Model
    Each review consists of:

    - Movie ID
    - Title
    - Rating
    - Genre IDs (stored as stringified list)

    Genre lists are converted back to Python lists using:
    ```python
    ast.literal_eval()
    ```
    Developer Notes:
    - CSV writes using absolute paths
    - Reviews accumulate over time

    ### Movieboard Generation
    The Movieboard is a curated list of all movies that have been reviewed, organized based on popularity. 

    #### Key Function

    - generate_movieboard()
    Organizes metadata for Movieboard display.

    #### Process
    1. Load all reviews from reviews.csv
    2. Group reviews by movie
    3. Calculate average star rating for each movie
    4. Grab TMDB details for each movie.
    5. Grab director name
    6. Construct the list of movie entries

    Each entry includes:
    - Title
    - Average rating
    - Genres
    - Director
    - Poster
    - Release year

    ### Recommendation Flow
    CineScore+ can provide personalized movie recommendations based on review history

    #### Key Functions
    - get_top_genres()
    Determines user's favorite genres based on reviews

    - recommend_movies_by_genre(genre_id)
    Grabs movies from TMDB's Discover API. 

    - filter_out_reviewed(recommendations, reviewed_table)
    Removes movies from recommendations that have been previously reviewed.

    - generate_recommendations()
    Collects all information and returns top 10 relevant recommendations 

    #### Flow
    1. Identify top genres from reviews.csv
    2. Grab movies from TMDB based on those genres
    3. Remove movies that have already been reviewed
    4. Return a curated list of recommendations

    ### Error Handling
    The backend includes safeguards:
    - Missing TMDB fields are replaced with defaults
    - API failures return empty results instead of a crash
    - Missing posters or release dates are shown as placeholders
    - Genre parsing uses ast.literal_eval to avoid crashing


   ## Frontend Architecture
   The frontend is implemented in frontend/app.py using Streamlit. It handles user interaction, page navigation, UI rendering, and communication with the backend functionality. All data processing is done using the backend, and the frontend focuses on presentation and user flow.

   ### Overview
   - Renders CineScore+ interface using Streamlit
   - Imports backend functions for search, reviews, Movieboard generation, and recommendations
   - Manages page navigation through a sidebar dropdown menu
   - Displays TMDB results, user reviews, and personalized recommendations
   - Handles user input for searches and review submissions.

   ### Page Structure and Navigation
   CineScore+ uses a sidebar dropdown menu to switch between pages:

   - **Search Movies**
   - **Submit Review**
   - **Movieboard**
   - **Recommendations**

   ![Navigation Menu Screenshot](C:\Users\cdsch\OneDrive\Pictures\navbar.png)

   Navigation is controlled by a single selectbox:

   ```python
   page = st.sidebar.selectbox("Navigation", ["Search Movies", "Submit Review", "Movieboard", "Recommendations"])
   ```
   ### Search Page
   The Search page lets users look up movies using TMDB.

   #### Flow
   1. User enters a movie title
   2. Frontend calls search_movie()
   3. Results are displayed with:
        - Poster
        - Title
        - Release year
        - Genres
        - Overview

   #### Key UI Components
   - st.text_input() for search terms
   - st.button() to trigger search
   - st.image() for posters
   - st.write() for metadata

   ### Submit Review Page
   This page allows users to submit a rating for a movie.

   #### Flow
   1. User enters a movie title
   2. Frontend calls search_movie() based on search
   3. User selects movie they want to review
   4. User enters a rating out of 5
   5. Frontend calls submit_review()

   #### Key UI Components
   - Dropdown for selecting a movie
   - Slider for rating scale
   - Button to submit
   - Success message after saving

   ### Movieboard Page
   The Movieboard displays movies ranked on popularity.

   #### Flow 
   1. Frontend calls generate_movieboard()
   2. Backend returns a list of upgraded movie entries
   3. Frontend displays each entry with:
        - Poster
        - Title
        - Average rating
        - Director
        - Genres
        - Release year
    
    #### Key UI Components
    - st.header()
    - st.image()
    - st.write()

   ### Recommendations Page
   This page displays personalized recommendations based on the user's review history.

   #### Flow 
   1. Frontend calls generate_recommendations()
   2. Backend identifies top genres and fetches TMDB results
   3. Backend filters out previously reviewed movies
   4. Frontend displays recommended movies

   #### Key UI Components
   - Posters
   - Titles
   - Genre name tags
   - Release years

   ### State Management
   CineScore+ users Streamlit's built-in state model:
   - Each page re-runs upon interaction
   - Backend functions are stateless.
   - CSV files provide use throughout sessions

   ### Error Handling and User Feedback
   The frontend provides:
   - Messages when no search results are found
   - Warnings when fields are missing
   - Success messages after submitting reviews
   - Missing posters or metadata is communicated.

    All critical errors (API fails, missing CSVs) are handled in the backend.

   ### Design Philosophy
   The UI is intentionally designed to be:
   - Minimal
   - Responsive
   - Easy for future improvement
   - Dependent on backend logic

   ## Data Flow
   At a high level, CineScore+ operates through four major data pathways:

   1. **User Input -> Frontend**
   2. **Frontend -> Backend Functions**
   3. **Backend -> TMDB API / CSV Storage**
   4. **Backend Results -> Frontend Rendering**

   Search, review, Movieboard, recommendations all follow this flow. 

   ### Search Flow

   1. User enters a movie title to search for.
   2. Frontend calls search_movie() with the user's search term.
   3. Backend sends a request to TMDB's Search API.
   4. Backend gets JSON response and finds the corresponding genre ID to the name in genres.csv.
   5. Frontend displays results with posters, titles, release years, genres and overviews.

   ### Review Submission Flow

   1. User searches for a movie using search_movie().
   2. User selects the movie they want to review from the dropdown.
   3. User chooses a rating out of 5 on the slider.
   4. Frontend calls submit_review() with movie ID, title, rating and genre IDs.
   5. Backend writes the review to reviews.csv (creating the file if needed).
   6. Frontend displays a success confirmation.

   ### Movieboard FLow

   1. Frontend calls generate_movieboard().
   2. Backend loads all reviews from reviews.csv.
   3. Backend groups reviews by movie ID.
   4. Backend calculates average ratings for each movie.
   5. Backend grabs TMDB details and director information.
   6. Backend returns upgraded movie entries for Movieboard display.
   7. Frontend displays posters, titles, ratings, genres, director(s) and release years.

   ### Recommendation Flow

   1. Frontend calls generate_recommendations().
   2. Backend loads review history from reviews.csv.
   3. Backend identifies the user's top genres.
   4. Backend grabs movies from TMDB's Discover API for those genres.
   5. Backend filters out movies the user already reviewed.
   6. Backend returns a curated list of recommended movies.
   7. Frontend displays posters and metadata for each recommended movie.

   ### Summary Diagram 

   ```
   User Input
       ↓
    Frontend (Streamlit)
       ↓
    Backend Functions
       ↓
    TMDB API / CSV data storage
       ↓
    Processed Results
       ↓
    Frontend Rendering
    ```

   ## Known Issues and Possible Solutions
   CineScore+ is in a functional state currently, but some possible issues exist that could impact user experience. Each issue is labeled based on severity, and contains possible solutions that could be implemented in future development.

   ### TMDB Rate Limits - Major
   Repeated searches and API calls may trigger a rate limit from TMDB. When this occurs, search results may appear empty, slow or incomplete. Due to the app's reliance on TMDB functions, rate limiting can significantly impact user experience.

   **Possible Solutions**
   - Implement caching using Streamlit's st.cache_data
   - Add retry logic with short delays
   - Reduce redundant API calls by caching movie details and genre lookups
   - Display a UX-friendly message when TMDB is temporarily unavailable.

   ### TMDB Data Inconsistencies - Minor
   TMDB will occasionally return incomplete metadata such as missing posters, release dates, or genre lists. Since CineScore+ relies on TMDB responses, these gaps can lead to partially filled movie entries or placeholder images in the UI.

   **Possible Solutions**
    - Add placeholder images for missing posters and text for missing fields
    - Cache previously retrieved movie details to reduce repeated failures
    - Display a small warning icon or note when metadata is incomplete   

   ### CSV Storage Limitations - Major
   CineScore+ stores reviews in reviews.csv, which works for small-scale use, but introduces some issues:
   - The file grows indefinitely over time
   - No user-specific review separation
   - File corruption could break the whole pipeline for Movieboard and recommendations
   
   **Possible Solutions**

   - Migrate to SQLite for structured, reliable storage
   - Add file integrity checks before reading
   - Implement user-specific tables or identifiers
   - Create a maintenance script to archive or trim older entries

   ### Genre Parsing Edge Cases - Minor
   Genre IDs are stored as stringified lists in the CSV. If the file is manually edited or becomes malformed, ast.literal_eval() may fail, causing missing genres or errors in the recommendation flow.

   **Possible Solutions**
   - Validate genre lists before saving
   - Add error handling around ast.literal_eval()

   ### Recommendation Quality Variability - Minor
   The current recommendation system is intentionally simple, reliant on the user's most reviewed genres. This could cause generic recommendations, repeated movies within the list of recommendations, and limited variety if few movies are present in TMDB's genre group.

   **Possible Solutions**
    - Use TMDB's "similar movies" endpoint
    - Weight recommendations by TMDB rating or popularity
    - Incorporate multi-genre scoring instead of single-genre matching

   ### Streamlit Rerun Behavior - Minor
   Streamlit re-runs the entire script on every interaction. This can lead to repeated API calls, flickering UI elements, and slight delays when Movieboard or recommendations are being loaded.

   **Possible Solutions**
   - Cache TMDB responses and Movieboard results
   - Move more intensive functions to be cached in the backend
   - Reduce unnecessary refreshes by reorganizing UI components

   ### Missing or Corrupted Files - Major

   If reviews.csv is missing or corrupted:
   - The Movieboard will appear empty
   - Recommendation process may fail
   - Review history is lost

   If genres.csv is missing: 
   - Genre names won't be displayed
   - Recommendation quality decreases

   **Possible Solutions**
   - Add automatic CSV validation on startup
   - Recreate missing files with default structure
   - Add backup/restore logic for reviews.csv
   - Log file errors for debugging purposes

   ## Future Roadmap
   This roadmap outlines potential improvements that could be implemented in CineScore+ in future development. 

   ### Improve Data Storage
   CineScore+ currently uses CSV files for storing reviews and genre data. While a simple system, CSVs limit scalability and reliability. Moving to a lightweight database such as SQLite would provide better long term stability

   **Benefits**
   - Reduced risk of corruption
   - Easier querying and filtering
   - Foundation of multi-user support

   ### User Accounts & Personalization
   Adding optional user accounts allows for separate review histories, and more accurate recommendations. This could be implemented using Streamlit's authentication features or using a lightweight external auth service, such as SupaBase.

   **Benefits**
   - Personalized Movieboards
   - Individual review histories
   - Multi user public deployment
   - Ability to save preferences

   ### Enhanced Recommendation Engine
   The current recommendation system is entirely based on genres. A more advanced engine could be used to incorporate additional TMDB endpoints or even machine learning techniques.

   **Possible Upgrades**
   - TMDB's "similar movies" endpoint
   - Weighted scoring using TMDB ratings and popularity
   - Multi-genre similarity matching

   ### Caching for Performance
   Caching TMDB response and Movieboard results would reduce API calls, improve responsiveness, and help avoid the rate-limit issues.

   **Benefits**
   - Faster search results
   - Smoother Movieboard loading time
   - Reduced dependency on TMDB

   ### Expanded Metadata Display
   Movie entries could have expanded information to enrich the user experience.

   **Potential Additions**
   - Cast lists
   - Runtime
   - Budget and revenue
   - Links to Trailers, or where to watch the film
   - TMDB user ratings

   ### Improved UI/UX
   The current UI is intentionally minimal. Future versions could introduce more visual polish.

   **Ideas**
   - Custom CSS Styling
   - Genre badges
   - Star-based rating widgets
   - Hover tooltips
   - More structure layout of pages

   ### Error Logging and Monitoring
   Adding lightweight logging would help future developer diagnose issues easier.

   **Benefits**
   - Easier debugging
   - Clearer visibility with API issues
   - Better long term maintainability

   ### Optional Cloud Database Integration
   If CineScore+ grows beyond Streamlit Cloud usage, moving to a cloud database would support multi user environments.

   **Possible databases**
   - Supabase
   - Firebase
   - PlanetScale
   - MongoDB Atlas

   ### Automated Testing
   Introducing unit tests would ensure reliability as the codebase grows.

   **Recommended Test Areas**
   - TMDB related functions
   - CSV operations and validations
   - Recommendation processes
   - Movieboard generation

   
   
    

