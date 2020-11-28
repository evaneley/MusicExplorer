from tkinter import *
import tkinter as tk
import musicbrainzngs
import webbrowser
from tkinter import ttk
from tkinter import messagebox

# Initialize agent to DB
musicbrainzngs.set_useragent(
    "MusicExplorer", "0.0.1", contact="evan_eley@yahoo.com")

root = Tk()

# Frames
result_wrapper = LabelFrame(root, text="Results")
search_wrapper = LabelFrame(root, text="Search")
search_song_fr = Frame(search_wrapper)
search_artist_fr = Frame(search_wrapper)
search_album_fr = Frame(search_wrapper)
#search_artist_fr = Frame(search_wrapper)
yt_wrapper = LabelFrame(root, text="Go To YouTube")

# Pack Frames
result_wrapper.pack(fill="both", expand=1, padx=20, pady=10)
search_wrapper.pack(fill="both", expand=1, padx=20, pady=10)
search_artist_fr.pack(fill="x", pady=10)
search_song_fr.pack(fill="x", pady=10)
search_album_fr.pack(fill="x", pady=10)
yt_wrapper.pack(fill="both", expand=1, padx=20, pady=10)

# Create Treeview
trv = ttk.Treeview(result_wrapper, columns=(
    1, 2, 3, 4), show="headings", height="10")
trv.pack(fill="both", expand=1, padx=5, pady=5)
# Make headings
trv.heading(1, text="Song")
trv.heading(2, text="Artist")
trv.heading(3, text="Album")
trv.heading(4, text="Date")

# Variables
artist_query = StringVar()
song_query = StringVar()
album_query = StringVar()
yt_query = StringVar()


# On double click, set search fields with selected item
def double_click(event):
    item = trv.selection()[0]
    values = trv.item(item, "values")
    song_query.set(values[0])
    artist_query.set(values[1])
    album_query.set(values[2])
    update_yt()

# Define a double click event in the TreeView
trv.bind("<Double-1>", double_click)


# Get the album and date of a song
def get_release(song):
    date = ""
    album = ""
    if "release-list" in song:
        for release in song["release-list"]:
            if "date" in release and release["date"] != "":
                #print(release["date"])
                if date == "":
                    date = release["date"]
                    album = release["title"]
                else:
                    #Check if year is less
                    if int(release["date"][0:4]) < int(date[0:4]):
                        #If year is same, check month (both dates must have a month)
                        if (int(release["date"][0:4]) == int(date[0:4])) and len(release["date"]) >= 7 and len(date) >= 7:
                            if int(release["date"][6:7]) < int(date[6:7]):
                                date = release["date"]
                                album = release["title"]
                        else:
                            date = release["date"]
                            album = release["title"]
    
    #print(date)
    #print(album)
    return album, date
        


# Update table with artist
def update_artist(res):
    trv.delete(*trv.get_children())
    for artist in res["artist-list"]:
        trv.insert('', 'end', values=("", artist["name"], "", ""))


# Update table with songs
def update_song(res):
    trv.delete(*trv.get_children())
    for song in res["recording-list"]:
        #Get Album and Date
        album, date = get_release(song)
        trv.insert('', 'end', values=(
            song["title"], song["artist-credit"][0]["name"], album, date))


# Update table with albums
def update_album(res):
    trv.delete(*trv.get_children())
    for album in res["release-list"]:
        #Get Date
        date = ""
        if "date" in album:
            date = album["date"]
        trv.insert('', 'end', values=("", album["artist-credit"][0]["name"], album["title"], date))
        #print(album)

# Search for Artist
def artist_search():
    artist_result = musicbrainzngs.search_artists(artist=artist_query.get())
    update_artist(artist_result)
    update_yt()


# Search for Songs
def song_search():
    song_result = musicbrainzngs.search_recordings(
        recording=song_query.get(), artistname=artist_query.get(), release=album_query.get())
    update_song(song_result)
    update_yt()


# Search for Albums
def album_search():
    album_result = musicbrainzngs.search_releases(release=album_query.get(), artistname=artist_query.get())
    update_album(album_result)
    update_yt()


# Clears all entries from results
def clear():
    # Clear search results
    trv.delete(*trv.get_children())
    # Clear text fields
    artist_query.set("")
    song_query.set("")
    album_query.set("")
    yt_query.set("")


# Searches what the user has entered on YouTube
def yt_search():
    search_term = yt_query.get().split()
    search_term_string = ""
    for i in search_term:
        search_term_string += i + "+"
    search_url = "https://www.youtube.com/results?search_query=" + search_term_string
    webbrowser.open(search_url)


# Updates the preview text for the YouTube search
def update_yt():
    yt = ""
    if song_query.get() != "":
        yt += song_query.get() + " "
    if artist_query.get() != "":
        yt += artist_query.get() + " "
    if album_query.get() != "":
        yt += album_query.get() + " "
    yt_query.set(yt)


# Search by Artist
artist_lbl = Label(search_artist_fr, text="By Artist\t")
artist_lbl.pack(side=tk.LEFT, padx=10)
artist_ent = Entry(search_artist_fr, textvariable=artist_query)
artist_ent.pack(side=tk.LEFT, padx=6)
artist_btn = Button(search_artist_fr, text="Search", command=artist_search)
artist_btn.pack(side=tk.LEFT, padx=6)

# Search by Song
artist_lbl = Label(search_song_fr, text="By Song\t")
artist_lbl.pack(side=tk.LEFT, padx=10)
artist_ent = Entry(search_song_fr, textvariable=song_query)
artist_ent.pack(side=tk.LEFT, padx=6)
artist_btn = Button(search_song_fr, text="Search", command=song_search)
artist_btn.pack(side=tk.LEFT, padx=6)

# Search by Album
artist_lbl = Label(search_album_fr, text="By Album")
artist_lbl.pack(side=tk.LEFT, padx=8)
artist_ent = Entry(search_album_fr, textvariable=album_query)
artist_ent.pack(side=tk.LEFT, padx=6)
artist_btn = Button(search_album_fr, text="Search", command=album_search)
artist_btn.pack(side=tk.LEFT, padx=6)

# Clear All Button
clr = Button(search_wrapper, text="Clear All", command=clear)
clr.pack(side=tk.RIGHT, padx=10)

# YouTube Search
_lbl = Label(yt_wrapper, text="Search for \"")
_lbl.pack(side=tk.LEFT)
prev_lbl = Label(yt_wrapper, textvariable=yt_query)
prev_lbl.pack(side=tk.LEFT)
lbl_ = Label(yt_wrapper, text="\" on YouTube")
lbl_.pack(side=tk.LEFT)
yt_btn = Button(yt_wrapper, text="Go", command=yt_search)
yt_btn.pack(side=tk.LEFT, padx=20)

# Render
root.title("MusicExplorer")
root.geometry("900x700")
root.mainloop()
