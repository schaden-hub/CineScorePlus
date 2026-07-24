Bug: search_movie() gave NoneType error during testing with message "NoneType is not iterable". 
What happened: TMDB was not feeding the right info, and updating the function to have some printouts helped fix the issue.
Status: Bug was fixed after retries. Added some printouts to check to make sure json was being sent by TMDB API.

Bug: generate_movieboard() was not displaying the correct number of ratings instead it was nan and 0 reviews.
What happened: Ratings and reviews were confused and used interchangibly to refer to the ratings column. The column was interperted as not a number. This created another column in reviews.csv that wasn't looked at by the functions using it. Pandas treated the column as empty or invalid, and the mean and count returned to NaN and 0.
Status: Fixed after adjusting standard to rating to refer to the 1-5 star rating system. The movieboard now displays the correct values.

Bug:Key error after adding lines to load new genres.csv. Columns were not in the correct order, so a key error was kicked back. 
What happened:When I ran the cell containing the new code to load in entries for each ID and genre words, the program became confused because I listed the genre ID second rather than first. My columns were also not labeled, which I believe also contributed.
Status: Updated and reformatted genres.csv with correct names and column order.

Bug: Search returned a 404 error when a year was added as a search term option
What happened: After adding code to allow for users to search with a title and release year, a search with a year attatched, ei Dune 2021, would return a 404 error. The year parameter was not included in the params dictionary. 
Status: Fixed after adding year to the parameters. The TMDB url was built correctly this way, and returned the correct results.

Bug: No search results were appearing on the genre filtering page.
What happened: Filtered results were always 0 even when the genre matched the searched movie. Converting genre IDs showed mismatched data types (string vs int) that caused issues with searching and filtering results based on genre. 
Status: Functionality was restored after editing conversion code. Ids were converted to integers in order to filter correctly. Expanded the cleanup loop when filtering by genre. 

Bug: Key error when referring to star ratings
What happened: Recieved a key error when implementing recommendation system. The rating column in the csv was referred to as stars in the get_top_genres function. The different names caused a key error.
Status: