# For the GUI
import tkinter as tk
import tkinter.ttk as ttk

# Data manipulation
import pandas as pd
import matplotlib as mpl
import matplotlib.backends.backend_tkagg

# Data structure implementation
import heapq

import requests



# Game Class Object
class Game:
    def __init__(self, title, platform, rating, genre):
        self.title = title
        self.platform = platform
        self.rating = round(rating, 1)
        self.genre = genre

    def get_details(self):
        platformString = ", ".join(self.platform)
        genreString = ", ".join(self.genre)
        return f"Title: {self.title}\nPlatform: {platformString}\nRating: {self.rating}\nGenre: {genreString}"

    # Make less than comparison opposite so the heapq (min heap) is implemented as max heap
    def __lt__(self, other):
        return self.rating > other.rating

# Function to get the game data
def auth():
    # twitch auth
    client_id = "m5ytptns6qbg8z11o21cu8rxv8c1bn"
    client_secret = "b6jokdw7idz54bggwzhb0ft5t5uyur"

    auth_response = requests.post("https://id.twitch.tv/oauth2/token", data={
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    })
    auth_response.raise_for_status()
    auth_response = auth_response.json()
    return auth_response.get("access_token")

def get_game_data(access_token, limit=500, offset=0):
    headers = {
        "Client-ID": "m5ytptns6qbg8z11o21cu8rxv8c1bn",
        "Authorization": f"Bearer {access_token}"
    }
    query = f"""
    fields name, platforms.name, genres.name, aggregated_rating;
    limit {limit};
    offset {offset};
    """
    response = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
    response.raise_for_status()
    return response.json()

def main():
    access_token = auth()
    maxGames = 250
    limit = 500
    offset = 0

    games = []
    while len(games) < maxGames:
        data = get_game_data(access_token, limit, offset)
        if not data:
            break
        for game in data:
            title = game.get("name", "Unknown")
            platform = [p["name"] for p in game.get("platforms", []) if "name" in p]
            rating = game.get("aggregated_rating")
            genre = [g["name"] for g in game.get("genres", []) if "name" in g]
            if title and platform and rating is not None and genre:
                games.append(Game(title, platform, rating, genre))
                if len(games) >= maxGames:
                    break
        offset += limit
    print(len(games))
    return games

def gameWindow(data):

    # tkinter rootwindow
    root = tk.Tk()
    root.title("Game Search Engine")
    root.geometry("800x600")
    root.configure(background="black")
    label = tk.Label(root, text="What is your name?", bg="black", fg="white")
    label.pack(pady=10)

    name = tk.Entry(root, width=50)
    name.pack(pady=10)

    gameInfo = tk.Label(root, text="", bg="black", fg="white", anchor="nw", justify="left", wraplength=750)
    gameInfo.pack(pady=10, fill=tk.BOTH, expand=True)

    # Define genres list

    def genreRatings():
        genre_heaps = sortIntoHeaps(data)
        genres_list = [
            "Pinball", "Adventure", "Indie", "Arcade", "Visual Novel",
            "Card & Board Game", "MOBA", "Point-and-click", "Fighting",
            "Shooter", "Music", "Platform", "Puzzle", "Racing",
            "Real Time Strategy (RTS)", "Role-playing (RPG)", "Simulator",
            "Sport", "Strategy", "Turn-based strategy (TBS)", "Tactical",
            "Hack and slash/Beat 'em up", "Quiz/Trivia"
        ]

        # Create drop-down (ComboBox) for genres, initially hidden
        genre_label = tk.Label(root, text="See Genre's Top Rated Games:", bg="black", fg="white")
        genre_label.pack(pady=10)

        genre_combobox = ttk.Combobox(root, values=genres_list, width=50, state="readonly")
        genre_combobox.pack(pady=10)

        def genreSelected(event):
            selected_genre = genre_combobox.get()

            top5Games = getTop5(genre_heaps[selected_genre])

            # Create a popup window for the top 5 games
            popup = tk.Toplevel(root)
            popup.title(f"Top 5 Games in {selected_genre} Genre")
            popup.geometry("300x300")  # Adjust size as needed
            popup.resizable(False, False)  # Prevent resizing

            canvas = tk.Canvas(popup)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill="y")

            canvas.config(yscrollcommand=scrollbar.set)

            info_frame = tk.Frame(canvas, bg="grey")
            canvas.create_window((0, 0), window=info_frame, anchor="nw")

            # Display the top 5 games in the frame inside the popup
            for i, game in enumerate(top5Games):
                game_details = tk.Label(info_frame, text=f"{i + 1}.\n{game.get_details()}",
                                        anchor="nw", justify="left", wraplength=250)
                game_details.pack(pady=5, fill=tk.BOTH, expand=True)

            info_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))

            close_button = tk.Button(popup, text="Close", command=popup.destroy)
            close_button.pack(pady=10)



        genre_combobox.bind("<<ComboboxSelected>>", genreSelected)




    def listGames():
        """need to make a frame to create the sorting options, slider or combobox"""

        # Create a frame to hold both the Listbox and Scrollbar
        frame = tk.Frame(root, bg="black")
        frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Listbox to display game titles
        listBox = tk.Listbox(frame, width=50, height=20, bg="black", fg="white", font=("Helvetica", 12), selectbackground="green")
        listBox.pack(side=tk.LEFT, fill=tk.Y)

        # Scrollbar for the Listbox
        scrollBar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listBox.yview)
        scrollBar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure Listbox to work with Scrollbar
        listBox.config(yscrollcommand=scrollBar.set)

        # Add game titles to the Listbox
        for game in data:
            listBox.insert(tk.END, game.title)

        # Function to display selected game's details in the grey area
        def selectGame(event):
            selected_index = listBox.curselection()
            if selected_index:  # Ensure a game is selected
                selected_game = data[selected_index[0]]
                gameInfo.config(text=selected_game.get_details(), bg="grey")  # Update grey area

        # Bind double-click event to the Listbox
        listBox.bind("<<ListboxSelect>>", selectGame)

    # Create button that lists top 5 games and hides top 5 games when toggled and untoggled
    heap_colleectopn = sortIntoHeaps(data)



    def userNamePrompt():
        userName = name.get()
        if userName.isalpha():
            label.config(text=f"Welcome to the Game Search Engine, {userName}!", bg="black", fg="green")
            name.destroy()
            submitButton.destroy()
            listGames()
            genreRatings()
        else:
            label.config(text="Please enter your name", bg="black", fg="red")
    """visualize function that uses matplotlib to display certain data (e.g., how many games are on each platform)"""

    submitButton = tk.Button(root, text="Submit", command=userNamePrompt)
    submitButton.pack(pady=10)

    exitButton = tk.Button(root, text="Exit", command=root.quit)
    exitButton.pack(pady=10, side=tk.BOTTOM)

    root.mainloop()


def getTop5(heap):
    extracted = []
    for i in range(min(5, len(heap))):
        extracted.append(heapq.heappop(heap))
    return extracted

def sortIntoHeaps(games):
    heap_collection = {}
    for game in games:
        for singleGenre in game.genre:
            if singleGenre not in heap_collection:
                heap_collection[singleGenre] = []
            heapq.heappush(heap_collection[singleGenre], game)
    return heap_collection




if __name__ == "__main__":
    data = main()
    gameWindow(data)
