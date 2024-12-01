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

    def listGames():
        """need to make a frame to create the sorting options, slider or combobox"""

        # Create a frame to hold both the Listbox and Scrollbar
        frame = tk.Frame(root, bg="black")
        frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Listbox to display game titles
        listBox = tk.Listbox(frame, width=50, height=20, bg="black", fg="white", font=("Helvetica", 12),
                             selectbackground="green")
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
                gameInfo.config(text=selected_game.get_details(), bg="grey")
                if top5Shown:
                    clicked_top_5()

        # Bind selection event to the Listbox
        listBox.bind("<<ListboxSelect>>", selectGame)

    # Create button that lists top 5 games and hides top 5 games when toggled and untoggled
    heap = createHeap(data)
    top5 = getTop5(heap)
    top5Shown = False

    def clicked_top_5():
        nonlocal top5Shown
        if not top5Shown:
            gameInfo.config(
                text="\n\n".join([game.get_details() for game in top5]),
                bg="grey"
            )
            top5Button.config(text="Hide Top 5 Rated Games")
        else:
            gameInfo.config(text="", bg="black")
            top5Button.config(text="Show Top 5 Rated Games")

        top5Shown = not top5Shown  # Toggle state

    def userNamePrompt():
        userName = name.get()
        if userName.isalpha():
            label.config(text=f"Welcome to the Game Search Engine, {userName}!", bg="black", fg="green")
            name.destroy()
            submitButton.destroy()
            listGames()

            global top5Button
            top5Button = tk.Button(root, text="Show Top 5 Rated Games", command=clicked_top_5)
            top5Button.pack(pady=10)
        else:
            label.config(text="Please enter your name", bg="black", fg="red")

    """visualize function that uses matplotlib to display certain data (e.g., how many games are on each platform)"""

    submitButton = tk.Button(root, text="Submit", command=userNamePrompt)
    submitButton.pack(pady=10)

    exitButton = tk.Button(root, text="Exit", command=root.quit)
    exitButton.pack(pady=10, side=tk.BOTTOM)

    root.mainloop()


def createHeap(games):
    heap = []
    for game in games:
        heapq.heappush(heap, game)
    return heap


def getTop5(heap):
    return [heapq.heappop(heap) for i in range(5)]


if __name__ == "__main__":
    data = main()
    gameWindow(data)
