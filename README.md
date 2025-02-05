# Python Programmer Test

Your task is to implement the following, using GCP for deployment:

## 1. Fetch test data via https from OMDB API

- You should fetch 100 movies from the OMDB API. It's up to you what kind of movies

you will get.

- Movies should be saved in the database.

- This method should be run only once if the database is empty.

## 2. Implement an api

- The api should have a method that returns a list of movies from the database
- There should be option to set how many records are returned in single API

response (by default 10)

- There should be pagination implemented in the backend

- Data should be ordered by Title

- The api should have a method that returns a single movie from the database

- There should be option to get the movie by title

- The api should have a method to add a movie to the database

- Title should be provided in request

- All movie details should be fetched from OMDB API and saved in the database

- The api should have a method to remove a movie from the database

- There should be option to remove movie with it's id

- This method should be protected so only authorized user can perform this action

## 3. Unit tests for all cases
