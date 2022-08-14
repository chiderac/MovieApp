create database MovieApp;
use MovieApp;
​
create table Users
(
username VARCHAR(40) PRIMARY KEY,
fullname VARCHAR(40),
email VARCHAR(40),
password VARCHAR(40)
);
​
create table Movies
(
id INT PRIMARY KEY, 
title VARCHAR(100), 
year INT, 
genre VARCHAR(40), 
user_rating FLOAT, 
poster VARCHAR(100),
original_language VARCHAR(40),
trailer VARCHAR(100)
);
​
​
create table WatchedMovies
(
username VARCHAR(40), 
movie_id INT PRIMARY KEY,
title_watched VARCHAR(100),
FOREIGN KEY (username) REFERENCES Users(username),
FOREIGN KEY (movie_id) REFERENCES Movies(id)
);
​
create table SavedMovies
(
username VARCHAR(40), 
movie_id INT PRIMARY KEY,
title_saved VARCHAR(100)
FOREIGN KEY (username) REFERENCES Users(username),
FOREIGN KEY (movie_id) REFERENCES Movies(id)
);
​
create table StreamingService
(
movie_id INT,
service1 VARCHAR(100),
service2 VARCHAR(100),
service3 VARCHAR(100),
service4 VARCHAR(100),
service5 VARCHAR(100),
FOREIGN KEY (movie_id) REFERENCES Movies(id)

);
​