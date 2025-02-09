"""Mock responses for OMDB API tests."""

MOCK_SEARCH_RESPONSE = {
    "Search": [
        {
            "Title": "The Matrix",
            "Year": "1999",
            "imdbID": "tt0133093",
            "Type": "movie",
            "Poster": "https://example.com/matrix.jpg"
        },
        {
            "Title": "The Matrix Reloaded",
            "Year": "2003",
            "imdbID": "tt0234215",
            "Type": "movie",
            "Poster": "https://example.com/matrix2.jpg"
        }
    ],
    "totalResults": "2",
    "Response": "True"
}

MOCK_MOVIE_DETAILS = {
    "Title": "The Matrix",
    "Year": "1999",
    "Rated": "R",
    "Released": "31 Mar 1999",
    "Runtime": "136 min",
    "Genre": "Action, Sci-Fi",
    "Director": "Lana Wachowski, Lilly Wachowski",
    "Writer": "Lana Wachowski, Lilly Wachowski",
    "Actors": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss",
    "Plot": "A computer programmer discovers that reality as he knows it is a simulation created by machines, and joins a rebellion to break free.",
    "Language": "English",
    "Country": "United States",
    "Awards": "Won 4 Oscars.",
    "Poster": "https://example.com/matrix.jpg",
    "Ratings": [
        {
            "Source": "Internet Movie Database",
            "Value": "8.7/10"
        }
    ],
    "Metascore": "73",
    "imdbRating": "8.7",
    "imdbVotes": "1,800,000",
    "imdbID": "tt0133093",
    "Type": "movie",
    "DVD": "21 Sep 1999",
    "BoxOffice": "$171,479,930",
    "Production": "Warner Bros.",
    "Website": "N/A",
    "Response": "True"
}

MOCK_ERROR_RESPONSE = {
    "Response": "False",
    "Error": "Movie not found!"
}

MOCK_INVALID_RESPONSE = {
    "Response": "True",
    "unexpected_field": "unexpected_value"
}