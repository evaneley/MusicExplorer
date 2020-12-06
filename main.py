from tkinter import Frame, LabelFrame, Button, Tk, StringVar, ttk, messagebox, Label, Entry
import tkinter as tk
import musicbrainzngs
import webbrowser

# Initialize user agent to DB
musicbrainzngs.set_useragent(
    "MusicExplorer", "0.0.1", contact="ee991216@ohio.edu")

# Initialize Main Window
root = Tk()

# Frames
# Where results are shown
result_wrapper = LabelFrame(root, text="Results")
# Where user enters search info
search_wrapper = LabelFrame(root, text="Search")
# Search Song
search_song_fr = Frame(search_wrapper)
# Search Artist
search_artist_fr = Frame(search_wrapper)
# Search Album
search_album_fr = Frame(search_wrapper)
# Filter by Year
filter_year_fr = Frame(search_wrapper)
# Search and Clear All Buttons
buttons_fr = Frame(search_wrapper)
# Where YouTube search option is shown
yt_wrapper = LabelFrame(root, text="Go To YouTube")

# Pack Frames
result_wrapper.pack(fill="both", expand=1, padx=20, pady=10)
search_wrapper.pack(fill="both", expand=1, padx=20, pady=10)
search_artist_fr.pack(fill="x", pady=10)
search_song_fr.pack(fill="x", pady=10)
search_album_fr.pack(fill="x", pady=10)
filter_year_fr.pack(fill="x", pady=10)
buttons_fr.pack(fill="x", pady=10)
yt_wrapper.pack(fill="both", expand=1, padx=20, pady=10)

# Create Treeview
trv = ttk.Treeview(result_wrapper, columns=(
    1, 2, 3, 4), show="headings", height="10")
trv.pack(side="left", fill="both", expand=1, padx=5, pady=5)
# Make headings
trv.heading(1, text="Song")
trv.heading(2, text="Artist")
trv.heading(3, text="Album")
trv.heading(4, text="Date")
# Add a vertical scrollbar
scrlbar = ttk.Scrollbar(result_wrapper, orient="vertical", command=trv.yview)
scrlbar.pack(side='right', fill='y')
trv.configure(yscrollcommand=scrlbar.set)

# Variables
artist_query = StringVar()  # User-Entered Artist
song_query = StringVar()    # User-Entered Song
album_query = StringVar()   # User-Entered Album
yt_query = StringVar()      # Generated YouTube Query
year_query = StringVar()    # User-Entered Year
b_range = StringVar()       # User-Entered Begin Range
e_range = StringVar()       # User-Entered End Range
song_wc = False             # If "See All" button in Song selected
album_wc = False            # If "See All" button in Album selected
year_bf = False             # If "Before" button selected
year_ex = False             # If "Exact" button selected
year_af = False             # If "After" button selected
incl = False                # If "Include" button selected
excl = False                # If "Exclude" button selected


# On double click, set search fields with selected item
def double_click(event):
    # Get Selection
    item = trv.selection()[0]
    # Set Values
    values = trv.item(item, "values")
    song_query.set(values[0])
    artist_query.set(values[1])
    album_query.set(values[2])
    # Update YT Query with new values
    update_yt()


# Define a double click event in the TreeView
trv.bind("<Double-1>", double_click)


# Get the album and date of a song
# Paramater (song) - Dictionary containing song metadata
def get_release(song):
    date = ""
    album = ""
    if "release-list" in song:
        for release in song["release-list"]:
            if "date" in release and release["date"] != "":
                # Occurs first time
                if date == "":
                    date = release["date"]
                    album = release["title"]
                else:
                    # Check if year is less
                    if int(release["date"][0:4]) < int(date[0:4]):
                        # If year is same, check month (both dates must have a month)
                        if (int(release["date"][0:4]) == int(date[0:4])) and len(release["date"]) >= 7 and len(date) >= 7:
                            # If month is same, check day (both dates must have a day)
                            if (int(release["date"][8:10]) == int(date[8:10])) and len(release["date"]) == 10 and len(date) >= 10:
                                if int(release["date"][8:10]) < int(date[8:10]):
                                    date = release["date"]
                                    album = release["title"]
                            # Else, compare month
                            if int(release["date"][5:7]) < int(date[5:7]):
                                date = release["date"]
                                album = release["title"]
                        # Else, compare year
                        else:
                            date = release["date"]
                            album = release["title"]

    # Return the album and the date
    return album, date


# Check year_query to make sure it is properly formatted
# If there is an entry, one of the buttons must be toggled
def check_valid_yr():
    # Import Globals
    global year_bf
    global year_ex
    global year_af
    global incl
    global excl
    # Check if it is a single year filter
    if year_bf or year_ex or year_af:
        # Input, but not correct format
        if len(year_query.get()) != 4 and year_query.get() != "":
            tk.messagebox.showerror(
                title="Error", message="Invalid Year. Use format YYYY.")
            return False
        # No input, but a button selected (just reset button and let happen)
        elif year_query.get() == "":
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
    # Check if it is a range filter
    elif incl or excl:
        # Input, but not correct format
        if (len(b_range.get()) != 4 and b_range.get() != "") or (len(e_range.get()) != 4 and e_range.get() != ""):
            tk.messagebox.showerror(
                title="Error", message="Invalid Year. Use format YYYY.")
            return False
        # No input, but a button selected (just reset button and let happen)
        elif b_range.get() == "" and e_range.get() == "":
            if incl:
                tgl_incl()
            else:
                tgl_excl()
            return True
        # Correct format, but invalid range
        elif int(b_range.get()) > int(e_range.get()):
            tk.messagebox.showerror(title="Error", message="Invalid Range.")
            return False
        # Valid Range
        else:
            return True
    # No filter
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
    global incl
    global excl
    if check_valid_yr():
        # Get StringVars for filters if necessary
        year = year_query.get()
        brng = b_range.get()
        erng = e_range.get()
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
        # Get songs in range
        elif incl:
            for song in res["recording-list"]:
                # Get Album and Date
                album, date = get_release(song)
                if date != "" and int(date[0:4]) >= int(brng) and int(date[0:4]) <= int(erng):
                    trv.insert('', 'end', values=(
                        song["title"], song["artist-credit"][0]["name"], album, date))
        # Get songs out of range
        elif excl:
            for song in res["recording-list"]:
                # Get Album and Date
                album, date = get_release(song)
                if date != "" and (int(date[0:4]) < int(brng) or int(date[0:4]) > int(erng)):
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
    global incl
    global excl
    if check_valid_yr():
        # Get StringVars if necessary
        year = year_query.get()
        brng = b_range.get()
        erng = e_range.get()
        trv.delete(*trv.get_children())
        # Get albums before entered year
        if year_bf:
            for album in res["release-list"]:
                # Get Date
                date = ""
                if "date" in album:
                    date = album["date"]
                # Check Date
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
                # Check Date
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
                # Check Date
                if date != "" and date[0:4] > year:
                    trv.insert('', 'end', values=(
                        "", album["artist-credit"][0]["name"], album["title"], date))
        # Get albums in range
        elif incl:
            for album in res["release-list"]:
                # Get Date
                date = ""
                if "date" in album:
                    date = album["date"]
                # Check Date
                if date != "" and (date[0:4] >= brng and date[0:4] <= erng):
                    trv.insert('', 'end', values=(
                        "", album["artist-credit"][0]["name"], album["title"], date))
        # Get albums out of range
        elif excl:
            for album in res["release-list"]:
                # Get Date
                date = ""
                if "date" in album:
                    date = album["date"]
                # Check Date
                if date != "" and (date[0:4] < brng or date[0:4] > erng):
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
    # Query
    artist_result = musicbrainzngs.search_artists(
        artist=artist_query.get(), limit=100)
    # Update Results
    update_artist(artist_result)
    # Update YouTube Query
    update_yt()


# Search for Songs
def song_search():
    # Query
    song_result = musicbrainzngs.search_recordings(
        recording=song_query.get(), artistname=artist_query.get(), release=album_query.get(), limit=100)
    # Update Results
    update_song(song_result)
    # Update YouTube Query
    update_yt()


# Search for Albums
def album_search():
    # Query
    album_result = musicbrainzngs.search_releases(
        release=album_query.get(), artistname=artist_query.get(), limit=100)
    # Update Results
    update_album(album_result)
    # Update YouTube
    update_yt()


# Toggle "Before" Button for Year Filter
def tgl_bf():
    # Import Globals
    global year_bf
    global year_ex
    global year_af
    global incl
    global excl
    # If on, toggle off
    if bf_btn.config('relief')[-1] == 'sunken':
        bf_btn.config(relief="raised")
        year_bf = False
    # Else, toggle on, and toggle other buttons off
    else:
        bf_btn.config(relief="sunken")
        year_bf = True
        ex_btn.config(relief="raised")
        year_ex = False
        af_btn.config(relief="raised")
        year_af = False
        incl_btn.config(relief="raised")
        incl = False
        excl_btn.config(relief="raised")
        excl = False


# Toggle "Exact" Button for Year Filter
def tgl_ex():
    # Import Globals
    global year_bf
    global year_ex
    global year_af
    global incl
    global excl
    # If on, toggle off
    if ex_btn.config('relief')[-1] == 'sunken':
        ex_btn.config(relief="raised")
        year_ex = False
    # Else toggle on, toggle other buttons off
    else:
        bf_btn.config(relief="raised")
        year_bf = False
        ex_btn.config(relief="sunken")
        year_ex = True
        af_btn.config(relief="raised")
        year_af = False
        incl_btn.config(relief="raised")
        incl = False
        excl_btn.config(relief="raised")
        excl = False


# Toggle "After" Button for Year Filter
def tgl_af():
    # Import Globals
    global year_bf
    global year_ex
    global year_af
    global incl
    global excl
    # If on, toggle off
    if af_btn.config('relief')[-1] == 'sunken':
        af_btn.config(relief="raised")
        year_af = False
    # Else toggle on, toggle other buttons off
    else:
        bf_btn.config(relief="raised")
        year_bf = False
        ex_btn.config(relief="raised")
        year_ex = False
        af_btn.config(relief="sunken")
        year_af = True
        incl_btn.config(relief="raised")
        incl = False
        excl_btn.config(relief="raised")
        excl = False


# Toggle Song Wildcard Button
def tgl_song():
    # Import Global
    global song_wc
    # If on, toggle off
    if song_btn.config('relief')[-1] == 'sunken':
        song_btn.config(relief="raised")
        song_wc = False
    # Else, toggle on
    else:
        song_btn.config(relief="sunken")
        song_wc = True


# Toggle Album Wildcard Button
def tgl_album():
    # Import Global
    global album_wc
    # If on, toggle off
    if album_btn.config('relief')[-1] == 'sunken':
        album_btn.config(relief="raised")
        album_wc = False
    # Else, toggle on
    else:
        album_btn.config(relief="sunken")
        album_wc = True


# Toggle "Include" Button
def tgl_incl():
    # Import Globals
    global incl
    global excl
    global year_bf
    global year_ex
    global year_af
    # If on, toggle off
    if incl_btn.config('relief')[-1] == 'sunken':
        incl_btn.config(relief="raised")
        incl = False
    # Else toggle on, toggle other buttons off
    else:
        incl_btn.config(relief="sunken")
        incl = True
        excl_btn.config(relief="raised")
        excl = False
        bf_btn.config(relief="raised")
        year_bf = False
        ex_btn.config(relief="raised")
        year_ex = False
        af_btn.config(relief="raised")
        year_af = False


# Toggle "Exclude" Button
def tgl_excl():
    # Import Globals
    global incl
    global excl
    global year_bf
    global year_ex
    global year_af
    # If on, toggle off
    if excl_btn.config('relief')[-1] == 'sunken':
        excl_btn.config(relief="raised")
        excl = False
    # Else toggle on, toggle other buttons off
    else:
        excl_btn.config(relief="sunken")
        excl = True
        incl_btn.config(relief="raised")
        incl = False
        bf_btn.config(relief="raised")
        year_bf = False
        ex_btn.config(relief="raised")
        year_ex = False
        af_btn.config(relief="raised")
        year_af = False


# Execute proper search based on user's input
def search():
    # If both WC buttons are pressed, toggle album (song search should be done)
    if song_wc and album_wc:
        tgl_album()
    # Nothing entered, do nothing
    if song_query.get() == "" and artist_query.get() == "" and album_query.get() == "":
        return
    # If song is entered, or song wildcard selected, do a song search
    elif song_query.get() != "" or song_wc:
        # If album wildcard was set, reset it
        if album_wc:
            tgl_album()
        # If user entered in song field and song_wc is set, reset song_wc
        if song_wc and song_query.get() != "":
            tgl_song()
        song_search()
    # Album is entered but no song, or album wildcard selected do an album search
    elif album_query.get() != "" or album_wc:
        # If user entered in album field and album_wc is set, reset album_wc
        if album_wc and album_query.get() != "":
            tgl_album()
        album_search()
    # Only artist entered, search artist
    else:
        artist_search()


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
    b_range.set("")
    e_range.set("")
    # Reset buttons
    if year_bf:
        tgl_bf()
    if year_ex:
        tgl_ex()
    if year_af:
        tgl_af()
    if song_wc:
        tgl_song()
    if album_wc:
        tgl_album()
    if incl:
        tgl_incl()
    if excl:
        tgl_excl()


# Searches what the user has entered on YouTube
def yt_search():
    # Prevent seaching for nothing
    if yt_query.get() == "":
        return
    # Split by space
    search_term = yt_query.get().split()
    search_term_string = ""
    for i in search_term:
        # Avoid problem chars
        if i != "&" and i != "?":
            search_term_string += i + "+"
        elif i == "&":
            # Replace '&' char to avoid breaking query
            search_term_string += "and+"
    # Build the URL
    search_url = "https://www.youtube.com/results?search_query=" + search_term_string
    # Open URL in browser
    webbrowser.open(search_url)


# Updates the preview text for the YouTube search
def update_yt():
    yt = ""
    # Add song
    if song_query.get() != "":
        yt += song_query.get() + " "
    # Add artist
    if artist_query.get() != "":
        yt += artist_query.get() + " "
    # Add album
    if album_query.get() != "":
        yt += album_query.get() + " "
    # Set the query
    yt_query.set(yt)


# Search by Artist
# Label
artist_lbl = Label(search_artist_fr, text="By Artist\t")
artist_lbl.pack(side=tk.LEFT, padx=10)
# Entry
artist_ent = Entry(search_artist_fr, textvariable=artist_query)
artist_ent.pack(side=tk.LEFT, padx=6)

# Search by Song
# Label
song_lbl = Label(search_song_fr, text="By Song\t")
song_lbl.pack(side=tk.LEFT, padx=10)
# Entry
song_ent = Entry(search_song_fr, textvariable=song_query)
song_ent.pack(side=tk.LEFT, padx=6)
# See All button
song_btn = Button(search_song_fr, text="See All",
                  command=tgl_song, relief="raised")
song_btn.pack(side=tk.LEFT, padx=6)

# Search by Album
# Label
album_lbl = Label(search_album_fr, text="By Album")
album_lbl.pack(side=tk.LEFT, padx=8)
# Entry
album_ent = Entry(search_album_fr, textvariable=album_query)
album_ent.pack(side=tk.LEFT, padx=6)
# See All button
album_btn = Button(search_album_fr, text="See All",
                   command=tgl_album, relief="raised")
album_btn.pack(side=tk.LEFT, padx=6)

# Filter by Year
# Label
year_lbl = Label(filter_year_fr, text="Filter Year")
year_lbl.pack(side=tk.LEFT, padx=8)
# Single year entry
year_ent = Entry(filter_year_fr, textvariable=year_query)
year_ent.pack(side=tk.LEFT, padx=6)
# Before button
bf_btn = Button(filter_year_fr, text="Before",
                relief="raised", command=tgl_bf)
bf_btn.pack(side=tk.LEFT, padx=6)
# Exact button
ex_btn = Button(filter_year_fr, text="Exact",
                relief="raised", command=tgl_ex)
ex_btn.pack(side=tk.LEFT, padx=6)
# After button
af_btn = Button(filter_year_fr, text="After",
                relief="raised", command=tgl_af)
af_btn.pack(side=tk.LEFT, padx=6)

# Filter by Year Range
# Label
or_lbl = Label(filter_year_fr, text="    OR\t Filter by Range")
or_lbl.pack(side=tk.LEFT, padx=8)
# Beginning of Range Entry
b_range_ent = Entry(filter_year_fr, textvariable=b_range, width=10)
b_range_ent.pack(side=tk.LEFT)
# Hyphen
hyphen = Label(filter_year_fr, text="-")
hyphen.pack(side=tk.LEFT)
# End of Range Entry
e_range_ent = Entry(filter_year_fr, textvariable=e_range, width=10)
e_range_ent.pack(side=tk.LEFT)
# Include Button
incl_btn = Button(filter_year_fr, text="Include",
                  relief="raised", command=tgl_incl)
incl_btn.pack(side=tk.LEFT, padx=12)
# Exclude Button
excl_btn = Button(filter_year_fr, text="Exclude",
                  relief="raised", command=tgl_excl)
excl_btn.pack(side=tk.LEFT)


# Search and Clear All Buttons
# Search button
search_btn = Button(buttons_fr, text="Search", command=search)
search_btn.pack(side=tk.LEFT, padx=10)
# Clear button
clr = Button(buttons_fr, text="Clear All", command=clear)
clr.pack(side=tk.LEFT, padx=10)

# YouTube Search
# Beginning of preview
_lbl = Label(yt_wrapper, text="Search for")
_lbl.pack(side=tk.LEFT)
# Insert query
prev_lbl = Label(yt_wrapper, textvariable=yt_query)
prev_lbl.pack(side=tk.LEFT)
# End of preview
lbl_ = Label(yt_wrapper, text="on YouTube")
lbl_.pack(side=tk.LEFT)
# Go button
yt_btn = Button(yt_wrapper, text="Go", command=yt_search)
yt_btn.pack(side=tk.LEFT, padx=20)

# Render
root.title("MusicExplorer")
root.geometry("900x700")
root.mainloop()
