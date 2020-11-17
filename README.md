# MusicExplorer
A simple music explorer that allows a user to search for music and quickly pull up music on YouTube to listen to.

# Installation
- You will need Python (I used Python 3 for development)
- Install the musicbrainz library: **pip install musicbrainzngs**

# Overview
The project involves taking a database of music and allowing a user to query on this database. If the user finds an artist, song, or album they are interested in listening to, they can then simply click a button, and be taken to YouTube page that will display search results of what the user was looking for. For example, if someone were to search for “The Beatles” in the program, then wanted to listen to their music, the user’s browser will open and take them to the search results on YouTube as if they had manually gone to YouTube and searched “The Beatles”. The developer wants to make this modular so it can search from a variety of the metadata provided by the database, and can be combinations of the metadata so someone can search for an artist and a song, or a song and an album, or any combination of that sort.

# Motivation
This project would be useful because it can allow a user a quick way to search for music and discover certain artists, albums, songs, etc. in a convenient way. It will also then allow the user to be able to quickly pull up a song on YouTube and listen to it, or even search on YouTube just for the artist and continue their searching on there.

# Dataset
The database the developer would be using for this project is called MusicBrainz (https://musicbrainz.org/). MusicBrainz is an open-source database that contains metadata for tons of music. It is publicly contributed to, like Wikipedia. Along with its developmental libraries, the developer thinks this would be a great library for the project, as it already contains tons of data, and the developer would not have to worry about populating their own database.

# Methodology
The developer’s idea is to develop this project in Python. MusicBrainz supplies a Python development library (musicbrainzngs) that can be used to make queries on the database using the XML web service. For user-interactivity, the developer would like to take a shot at creating a GUI using Tkinter. This way, everything can be done away from the console like any other program that somebody would use. Finally, to execute the YouTube search, the developer would use the webbrowser library to open the user’s web-browser and take them to the search page. If the developer can create a list of the terms for the user’s search, they can easily create the URL for the YouTube search page with the user’s keywords. 
