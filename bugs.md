Bug: search_movie() gave NoneType error during testing with message "NoneType is not iterable". 
What happened: TMDB was not feeding the right info, and updating the function to have some printouts helped fix the issue.
Status: Bug was fixed after retried. Added some printouts to check to make sure json was being sent by TMDB API.

Bug: generate_movieboard() was not displaying the correct number of ratings instead it was nan and 0 reviews.
What happened: Ratings and reviews were confused and used interchangibly to refer to the ratings column. The column was interperted as not a number. This created another column in reviews.csv that wasn't looked at by the functions using it. Pandas treated the column as empty or invalid, and the mean and count returned to NaN and 0.
Status: Fixed after adjusting standard to rating to refer to the 1-5 star rating system. The movieboard now displays the correct values.

Bug:Key error after adding lines to load new genres.csv. Columns were not in the correct order, so a key error was kicked back. 
What happened:When I ran the cell containing the new code to load in entries for each ID and genre words, the program became confused because I listed the genre ID second rather than first. My columns were also not labeled, which I believe also contributed.
Status: Updated and reformatted genres.csv with correct names and column order.