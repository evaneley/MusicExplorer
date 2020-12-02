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
filter_year_fr = Frame(search_wrapper)
yt_wrapper = LabelFrame(root, text="Go To YouTube")

# Pack Frames
result_wrapper.pack(fill="both", expand=1, padx=20, pady=10)
search_wrapper.pack(fill="both", expand=1, padx=20, pady=10)
search_artist_fr.pack(fill="x", pady=10)
search_song_fr.pack(fill="x", pady=10)
search_album_fr.pack(fill="x", pady=10)
filter_year_fr.pack(fill="x", pady=10)
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
year_query = StringVar()
year_bf = False
year_ex = False
year_af = False


# On double click, set search fields with selected item
def double_click(event):
    item = trv.selection()[0]
    values = trv.item(item, "values")
    song_query.set(values[0])
    artist_query.set(values[1])
    album_query.set(values[2])
    # year_query.set(values[3][0:4])
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
                # print(release["date"])
                if date == "":
                    date = release["date"]
                    album = release["title"]
                else:
                    # Check if year is less
                    if int(release["date"][0:4]) < int(date[0:4]):
                        # If year is same, check month (both dates must have a month)
                        if (int(release["date"][0:4]) == int(date[0:4])) and len(release["date"]) >= 7 and len(date) >= 7:
                            if int(release["date"][6:7]) < int(date[6:7]):
                                date = release["date"]
                                album = release["title"]
                        else:
                            date = release["date"]
                            album = release["title"]

    # print(date)
    # print(album)
    return album, date


# Check year_query to make sure it is properly formatted
# If there is an entry, one of the buttons must be toggled
def check_valid_yr():
    # Input, but not correct format
    if len(year_query.get()) != 4 and year_query.get() != "":
        tk.messagebox.showerror(
            title="Error", message="Invalid Year. Use format YYYY.")
        return False
    # Input, but no button selected
    elif (year_query.get() != "") and (not year_bf) and (not year_ex) and (not year_af):
        tk.messagebox.showerror(
            title="Error", message="Please select an option for the year")
    # No input, but a button selected (just reset button and let happen)
    elif (year_query.get() == "") and (year_bf or year_ex or year_af):
        if year_bf:
            tgl_bf()
        elif year_ex:
            tgl_ex()
        else:
            tgl_af()
        return True
    # Valid entry
    else:
        return True


# Update table with artist
def update_artist(res):
    trv.delete(*trv.get_children())
    for artist in res["artist-list"]:
        trv.insert('', 'end', values=("", artist["name"], "", ""))


# Update table with songs
def update_song(res):
    # Import globals
    global year_bf
    global year_ex
    global year_af
    if check_valid_yr():
        year = year_query.get()
        trv.delete(*trv.get_children())
        # Get songs before entered year
        if year_bf:
            for song in res["recording-list"]:
                # Get Album and Date
                album, date = get_release(song)
                if date != "" and int(date[0:4]) < int(year):
                    trv.insert('', 'end', values=(
                        song["title"], song["artist-credit"][0]["name"], album, date))
        # Get songs on entered year
        elif year_ex:
            for song in res["recording-list"]:
                # Get Album and Date
                album, date = get_release(song)
                if date != "" and int(date[0:4]) == int(year):
                    trv.insert('', 'end', values=(
                        song["title"], song["artist-credit"][0]["name"], album, date))
        # Get songs after entered year
        elif year_af:
            for song in res["recording-list"]:
                # Get Album and Date
                album, date = get_release(song)
                if date != "" and int(date[0:4]) > int(year):
                    trv.insert('', 'end', values=(
                        song["title"], song["artist-credit"][0]["name"], album, date))
        # No year filter
        else:
            for song in res["recording-list"]:
                # Get Album and Date
                album, date = get_release(song)
                trv.insert('', 'end', values=(
                    song["title"], song["artist-credit"][0]["name"], album, date))


# Update table with albums
def update_album(res):
    # Import globals
    global year_bf
    global year_ex
    global year_af
    if check_valid_yr():
        year = year_query.get()
        trv.delete(*trv.get_children())
        # Get albums before entered year
        if year_bf:
            for album in res["release-list"]:
                # Get Date
                date = ""
                if "date" in album:
                    date = album["date"]
                if date != "" and date[0:4] < year:
                    trv.insert('', 'end', values=(
                        "", album["artist-credit"][0]["name"], album["title"], date))
        # Get albums on entered year
        elif year_ex:
            for album in res["release-list"]:
                # Get Date
                date = ""
                if "date" in album:
                    date = album["date"]
                if date != "" and date[0:4] == year:
                    trv.insert('', 'end', values=(
                        "", album["artist-credit"][0]["name"], album["title"], date))
        # Get albums after entered year
        elif year_af:
            for album in res["release-list"]:
                # Get Date
                date = ""
                if "date" in album:
                    date = album["date"]
                if date != "" and date[0:4] > year:
                    trv.insert('', 'end', values=(
                        "", album["artist-credit"][0]["name"], album["title"], date))
        # No filter
        else:
            for album in res["release-list"]:
                # Get Date
                date = ""
                if "date" in album:
                    date = album["date"]
                trv.insert('', 'end', values=(
                    "", album["artist-credit"][0]["name"], album["title"], date))


# Search for Artist
def artist_search():
    artist_result = musicbrainzngs.search_artists(
        artist=artist_query.get(), limit=100)
    update_artist(artist_result)
    update_yt()


# Search for Songs
def song_search():
    song_result = musicbrainzngs.search_recordings(
        recording=song_query.get(), artistname=artist_query.get(), release=album_query.get(), limit=100)
    update_song(song_result)
    update_yt()


# Search for Albums
def album_search():
    album_result = musicbrainzngs.search_releases(
        release=album_query.get(), artistname=artist_query.get(), limit=100)
    update_album(album_result)
    update_yt()


# Toggle "Before" Button for Year Filter
def tgl_bf():
    global year_bf
    global year_ex
    global year_af
    if bf_btn.config('relief')[-1] == 'sunken':
        bf_btn.config(relief="raised")
        year_bf = False
    else:
        bf_btn.config(relief="sunken")
        year_bf = True
        ex_btn.config(relief="raised")
        year_ex = False
        af_btn.config(relief="raised")
        year_af = False


# Toggle "Exact" Button for Year Filter
def tgl_ex():
    global year_bf
    global year_ex
    global year_af
    if ex_btn.config('relief')[-1] == 'sunken':
        ex_btn.config(relief="raised")
        year_ex = False
    else:
        bf_btn.config(relief="raised")
        year_bf = False
        ex_btn.config(relief="sunken")
        year_ex = True
        af_btn.config(relief="raised")
        year_af = False


# Toggle "After" Button for Year Filter
def tgl_af():
    global year_bf
    global year_ex
    global year_af
    if af_btn.config('relief')[-1] == 'sunken':
        af_btn.config(relief="raised")
        year_af = False
    else:
        bf_btn.config(relief="raised")
        year_bf = False
        ex_btn.config(relief="raised")
        year_ex = False
        af_btn.config(relief="sunken")
        year_af = True


# Clears all entries from results
def clear():
    # Clear search results
    trv.delete(*trv.get_children())
    # Clear text fields
    artist_query.set("")
    song_query.set("")
    album_query.set("")
    yt_query.set("")
    year_query.set("")
    # Reset buttons
    bf_btn.config(relief="raised")
    ex_btn.config(relief="raised")
    af_btn.config(relief="raised")


# Searches what the user has entered on YouTube
def yt_search():
    search_term = yt_query.get().split()
    search_term_string = ""
    for i in search_term:
        if i != "&" and i != "?":
            search_term_string += i + "+"
        elif i == "&":
            # Replace '&' char to avoid breaking query
            search_term_string += "and+"
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

# Filter by Year
year_lbl = Label(filter_year_fr, text="Filter Year")
year_lbl.pack(side=tk.LEFT, padx=8)
year_ent = Entry(filter_year_fr, textvariable=year_query)
year_ent.pack(side=tk.LEFT, padx=6)
bf_btn = Button(filter_year_fr, text="Before",
                relief="raised", command=tgl_bf)
bf_btn.pack(side=tk.LEFT, padx=6)
ex_btn = Button(filter_year_fr, text="Exact",
                relief="raised", command=tgl_ex)
ex_btn.pack(side=tk.LEFT, padx=6)
af_btn = Button(filter_year_fr, text="After",
                relief="raised", command=tgl_af)
af_btn.pack(side=tk.LEFT, padx=6)

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
