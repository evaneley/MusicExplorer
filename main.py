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
yt_wrapper = LabelFrame(root, text="Go To YouTube")

# Pack Frames
result_wrapper.pack(fill="both", expand=1, padx=20, pady=10)
search_wrapper.pack(fill="both", expand=1, padx=20, pady=10)
yt_wrapper.pack(fill="both", expand=1, padx=20, pady=10)

# Create Treeview
trv = ttk.Treeview(result_wrapper, columns=(
    1, 2, 3, 4), show="headings", height="10")
trv.pack()
# Make headings
trv.heading(1, text="Song")
trv.heading(2, text="Artist")
trv.heading(3, text="Album")
trv.heading(4, text="Year")

# Variables
artist_query = StringVar()

# Used to update table


def update(res):
    trv.delete(*trv.get_children())
    for artist in res["artist-list"]:
        trv.insert('', 'end', values=("null", artist["name"], "null", "null"))

# Searches by artist


def artist_search():
    artist_result = musicbrainzngs.search_artists(artist=artist_query.get())
    update(artist_result)

# Clears all entries from results


def clear():
    trv.delete(*trv.get_children())


# Search by Artist
artist_lbl = Label(search_wrapper, text="Search Artist")
artist_lbl.pack(side=tk.LEFT, padx=10)
artist_ent = Entry(search_wrapper, textvariable=artist_query)
artist_ent.pack(side=tk.LEFT, padx=6)
artist_btn = Button(search_wrapper, text="Search", command=artist_search)
artist_btn.pack(side=tk.LEFT, padx=6)

# Clear All Button
clr = Button(search_wrapper, text="Clear All", command=clear)
clr.pack(side=tk.RIGHT, padx=10)

# Render
root.title("MusicExplorer")
root.geometry("800x700")
root.mainloop()
