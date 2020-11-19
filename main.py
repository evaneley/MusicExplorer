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
#search_artist_fr = Frame(search_wrapper)
#search_artist_fr = Frame(search_wrapper)
yt_wrapper = LabelFrame(root, text="Go To YouTube")

# Pack Frames
result_wrapper.pack(fill="both", expand=1, padx=20, pady=10)
search_wrapper.pack(fill="both", expand=1, padx=20, pady=10)
search_artist_fr.pack(fill="x")
search_song_fr.pack(fill="x")
yt_wrapper.pack(fill="both", expand=1, padx=20, pady=10)

# Create Treeview
trv = ttk.Treeview(result_wrapper, columns=(
    1, 2, 3, 4), show="headings", height="10")
trv.pack(fill="both", expand=1, padx=5, pady=5)
# Make headings
trv.heading(1, text="Song")
trv.heading(2, text="Artist")
trv.heading(3, text="Album")
trv.heading(4, text="Year")

# Variables
artist_query = StringVar()
song_query = StringVar()
yt_query = StringVar()

# Used to update table


def update_artist(res):
    trv.delete(*trv.get_children())
    for artist in res["artist-list"]:
        trv.insert('', 'end', values=("null", artist["name"], "null", "null"))


"""Potential Blog post: Documentation says that it is a 'recording-list' but it is actually a 'release-list' """


def update_song(res):
    trv.delete(*trv.get_children())
    for song in res["recording-list"]:
        trv.insert('', 'end', values=(
            song["title"], song["artist-credit"][0]["name"], "null", "null"))
        # print(song)
        # print()


# Search for Artist
def artist_search():
    artist_result = musicbrainzngs.search_artists(artist=artist_query.get())
    update_artist(artist_result)
    update_yt()


# Search for Songs
def song_search():
    song_result = musicbrainzngs.search_recordings(
        release=song_query.get(), artistname=artist_query.get())
    update_song(song_result)
    update_yt()


# Clears all entries from results
def clear():
    # Clear search results
    trv.delete(*trv.get_children())
    # Clear text fields
    artist_query.set("")
    song_query.set("")
    yt_query.set("")


# Searches what the user has entered on YouTube
def yt_search():
    print(yt_query.get())
    search_term = yt_query.get().split()
    search_term_string = ""
    for i in search_term:
        print(i)
        search_term_string += i + "+"
    print(search_term_string)
    search_url = "https://www.youtube.com/results?search_query=" + search_term_string
    webbrowser.open(search_url)


# Updates the preview text for the YouTube search
def update_yt():
    yt = ""
    if song_query.get() != "":
        yt += song_query.get() + " "
    if artist_query.get() != "":
        yt += artist_query.get() + " "
    yt_query.set(yt)


# Search by Artist
artist_lbl = Label(search_artist_fr, text="By Artist")
artist_lbl.pack(side=tk.LEFT, padx=10)
artist_ent = Entry(search_artist_fr, textvariable=artist_query)
artist_ent.pack(side=tk.LEFT, padx=6)
artist_btn = Button(search_artist_fr, text="Search", command=artist_search)
artist_btn.pack(side=tk.LEFT, padx=6)

# Search by Song
artist_lbl = Label(search_song_fr, text="By Song")
artist_lbl.pack(side=tk.LEFT, padx=10)
artist_ent = Entry(search_song_fr, textvariable=song_query)
artist_ent.pack(side=tk.LEFT, padx=6)
artist_btn = Button(search_song_fr, text="Search", command=song_search)
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
