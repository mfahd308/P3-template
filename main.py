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

# Import the GameHashMap from the separate file
from heapsearch import GameHashMap


# Game Class Object
class Game:
    def __init__(self, title, platform, rating, genre):
        self.title = title
        self.platform = platform
        self.rating = rating
        self.genre = genre

    def get_details(self):
        platformString = ", ".join(self.platform)
        genreString = ", ".join(self.genre)
        return f"Title: {self.title}\nPlatform: {platformString}\nRating: {self.rating}\nGenre: {genreString}"


# Function to authenticate with Twitch API
def auth():
    client_id = "m5ytptns6qbg8z11o21cu8rxv8c1bn"
    client_secret = "b6jokdw7idz54bggwzhb0ft5t5uyur"

    auth_response = requests.post(
        "https://id.twitch.tv/oauth2/token",
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        },
    )
    auth_response.raise_for_status()
    auth_response = auth_response.json()
    return auth_response.get("access_token")


# Function to fetch game data
def get_game_data(access_token, limit=500, offset=0):
    headers = {
        "Client-ID": "m5ytptns6qbg8z11o21cu8rxv8c1bn",
        "Authorization": f"Bearer {access_token}",
    }
    query = f"""
    fields name, platforms.name, genres.name, aggregated_rating;
    limit {limit};
    offset {offset};
    """
    response = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query)
    response.raise_for_status()
    return response.json()


# Main function to fetch and process game data
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


# GUI Window
def gameWindow(data):
    # Initialize the GameHashMap
    game_map = GameHashMap(data)

    # tkinter rootwindow
    root = tk.Tk()
    root.title("Game Search Engine")
    root.geometry("800x600")
    root.configure(background="black")

    label = tk.Label(root, text="What is your name?", bg="black", fg="white")
    label.pack(pady=10)

    name = tk.Entry(root, width=50)
    name.pack(pady=10)

    gameInfo = tk.Label(
        root, text="", bg="black", fg="white", anchor="nw", justify="left", wraplength=750
    )
    gameInfo.pack(pady=10, fill=tk.BOTH, expand=True)

    def listGames():
        """List all games in the database."""
        frame = tk.Frame(root, bg="black")
        frame.pack(fill=tk.BOTH, expand=True, pady=10)

        listBox = tk.Listbox(
            frame,
            width=50,
            height=20,
            bg="black",
            fg="white",
            font=("Helvetica", 12),
            selectbackground="green",
        )
        listBox.pack(side=tk.LEFT, fill=tk.Y)

        scrollBar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=listBox.yview)
        scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
        listBox.config(yscrollcommand=scrollBar.set)

        for game in data:
            listBox.insert(tk.END, game.title)

        def selectGame(event):

            selected_index = listBox.curselection()

            if selected_index:

                selected_game = data[selected_index[0]]
                gameInfo.config(text=selected_game.get_details(), bg="grey")

        listBox.bind("<<ListboxSelect>>", selectGame) #connects user interaction with logic to display

    def searchGame():
        """Search for a specific game."""

        search_query = search_entry.get().strip()

        if search_query:

            result = game_map.search_game_by_title(search_query)

            if result:

                genre_str = ", ".join(result["genre"])
                platform_str = ", ".join(result["platform"])
                gameInfo.config(
                    text=f"Title: {search_query}\nGenre: {genre_str}\nRating: {result['rating']}\nPlatform: {platform_str}",
                    bg="grey",
                    fg="black",
                )

            else:

                gameInfo.config(text="Game not found!", bg="black", fg="red")

        else:

            gameInfo.config(text="Please enter a valid game title.", bg="black", fg="red")

    def userNamePrompt():
        userName = name.get()
        if userName.isalpha():
            label.config(
                text=f"Welcome to the Game Search Engine, {userName}!",
                bg="black",
                fg="green",
            )
            name.destroy()
            submitButton.destroy()
            listGames()
        else:
            label.config(text="Please enter your name", bg="black", fg="red")

    search_label = tk.Label(root, text="Search for a game:", bg="black", fg="white")
    search_label.pack(pady=10)

    search_entry = tk.Entry(root, width=50)
    search_entry.pack(pady=10)

    search_button = tk.Button(root, text="Search", command=searchGame)
    search_button.pack(pady=10)

    submitButton = tk.Button(root, text="Submit", command=userNamePrompt)
    submitButton.pack(pady=10)

    exitButton = tk.Button(root, text="Exit", command=root.quit)
    exitButton.pack(pady=10, side=tk.BOTTOM)

    root.mainloop()


if __name__ == "__main__":
    data = main()
    gameWindow(data)
