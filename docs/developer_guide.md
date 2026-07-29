# CineScore+ Developer Guide (v2.0)

   ## Overview
   CineScore+ is a movie review app for film buffs with options to search for movies, review them, view a Movieboard to show top rated films, and get personalized recommendations based on their top reviewed films. Functionality is derived from using Python, Streamlit, and the TMDB API. 

   Users are able to:
   - Search for movies
   - Submit ratings for reviews
   - Filter movies by a genre tag
   - View a personalized movieboard based on review history
   - Receive recommendations based on top rated genres

   The application consists of a backend .py file that handles API communication, data processing, and the recommendation flow, and a frontend .py file (app.py)  that provides an interactive experience using Streamlit. Data is stored locally using CSV files (reviews.csv and genres.csv), and TMDB provides external movie data. 
   
   ## Project Structure
   CINESCOREPLUS/

        backend/
            backend.py      # TMDB API calls, review storage, movieboard processing, recommendations
        
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
   pip instal -r requirements.txt
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

   ## Backend Architecture

   ## Frontend Architecture

   ## Data Flow

   ## Known Issues

   ## Future Roadmap
   
    

