# For the GUI
import tkinter as tk
import tkinter.ttk as ttk

# Data manipulation
import pandas as pd
import matplotlib.pyplot as mpl
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Data structure implementation
import heapq

import requests

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
    return games

def gameWindow(data):
    # tkinter rootwindow
    root = tk.Tk()
    root.title("Game Search Engine")
    root.geometry("1104x840")
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

    def userNamePrompt():
        userName = name.get()
        if userName.isalpha():
            label.config(text=f"Welcome to the Game Search Engine, {userName}!", bg="black", fg="green")
            name.destroy()
            submitButton.destroy()
            listGames()
            visualizeButton = tk.Button(root, text="Number of Games on Each Platform", command=platformCountVisualize)
            visualizeButton.place(relx=0.7, rely=0.7)
            genreButton = tk.Button(root, text="Count of Games in Each Genre", command=genreCountVisualize)
            genreButton.place(relx=0.7, rely=0.8)
            averageButton = tk.Button(root, text="Average Rating of Each Genre", command=averageVisualize)
            averageButton.place(relx=0.7, rely=0.9)
        else:
            label.config(text="Please enter your name", bg="black", fg="red")
    """visualize functions that uses matplotlib to display certain data (e.g., how many games are on each platform)"""
    # visualize the number of games on each platform
    def platformCountVisualize():
        visWindow = tk.Toplevel()
        visWindow.title("Platform Counts")
        visWindow.geometry("1984x1012")
        visWindow.configure(background="black")
        platformCount = {}
        for game in data:
            for platform in game.platform:
                if platform in platformCount:
                    platformCount[platform] += 1
                else:
                    platformCount[platform] = 1
        platforms = list(platformCount.keys())
        counts = list(platformCount.values())

        figure = mpl.figure(figsize=(12, 8))
        ax = figure.add_subplot(111)
        ax.barh(platforms, counts, color="blue")
        ax.set_xlabel("Number of Games")
        ax.set_ylabel("Platform")
        ax.set_title("Number of Games on Each Platform")
        mpl.show()

        canvas = FigureCanvasTkAgg(figure, master=visWindow)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        closeWindow = tk.Button(visWindow, text="Close", command=visWindow.destroy)
        closeWindow.pack(pady=10)
    # visualize number of games in each genre
    def genreCountVisualize():
        visWindow = tk.Toplevel()
        visWindow.title("Genre Counts")
        visWindow.geometry("1984x1012")
        visWindow.configure(background="black")
        genreCount = {}
        for game in data:
            for genre in game.genre:
                if genre in genreCount:
                    genreCount[genre] += 1
                else:
                    genreCount[genre] = 1
        genres = list(genreCount.keys())
        counts = list(genreCount.values())

        figure = mpl.figure(figsize=(12, 8))
        ax = figure.add_subplot(111)
        ax.barh(genres, counts, color="blue")
        ax.set_xlabel("Number of Games")
        ax.set_ylabel("Genre")
        ax.set_title("Number of Games in Each Genre")
        mpl.show()

        canvas = FigureCanvasTkAgg(figure, master=visWindow)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        closeWindow = tk.Button(visWindow, text="Close", command=visWindow.destroy)
        closeWindow.pack(pady=10)
    # average rating of each genre
    def averageVisualize():
        visWindow = tk.Toplevel()
        visWindow.title("Average Rating of Each Genre")
        visWindow.geometry("1984x1012")
        visWindow.configure(background="black")
        genreRating = {}
        for game in data:
            for genre in game.genre:
                if genre in genreRating:
                    genreRating[genre].append(game.rating)
                else:
                    genreRating[genre] = [game.rating]
        genres = list(genreRating.keys())
        averages = [sum(genreRating[genre]) / len(genreRating[genre]) for genre in genres]

        figure = mpl.figure(figsize=(12, 8))
        ax = figure.add_subplot(111)
        ax.barh(genres, averages, color="blue")
        ax.set_xlabel("Average Rating")
        ax.set_ylabel("Genre")
        ax.set_title("Average Rating of Each Genre")
        mpl.show()

        canvas = FigureCanvasTkAgg(figure, master=visWindow)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        closeWindow = tk.Button(visWindow, text="Close", command=visWindow.destroy)
        closeWindow.pack(pady=10)

    submitButton = tk.Button(root, text="Submit", command=userNamePrompt)
    submitButton.pack(pady=10)

    exitButton = tk.Button(root, text="Exit", command=root.quit)
    exitButton.pack(pady=10, side=tk.BOTTOM)

    root.mainloop()


if __name__ == "__main__":
    data = main()
    gameWindow(data)
