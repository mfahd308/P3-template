# For the GUI
import tkinter as tk
import tkinter.ttk as ttk

# Data manipulation
import pandas as pd
import matplotlib as mpl
import matplotlib.backends.backend_tkagg

# Data structure implementation
import heapq

# IGN Dataset
from bridges.bridges import *
from bridges.data_src_dependent.data_source import *


# Game Class Object
class Game:
    def __init__(self, title, platform, rating, genre):
        self.title = title
        self.platform = platform
        self.rating = rating
        self.genre = genre

    def get_details(self):
        return f"Title: {self.title}\nPlatform: {self.platform}\nRating: {self.rating}\nGenre: {self.genre}"


# Function to get the game data
def main():
    # Create the bridges object
    """figure out a way to either have the user get their bridges info or hide mine"""
    bridges = Bridges(0, "paapa", "1501703593714")

    my_list = get_game_data()

    """Need to sort the list after initializing the game objects"""
    # List of all game objects
    games = []
    for game in my_list:
        games.append(Game(game.title, game.platform, game.rating, game.genre))
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
        else:
            label.config(text="Please enter your name", bg="black", fg="red")
    """visualize function that uses matplotlib to display certain data (e.g., how many games are on each platform)"""

    submitButton = tk.Button(root, text="Submit", command=userNamePrompt)
    submitButton.pack(pady=10)

    exitButton = tk.Button(root, text="Exit", command=root.quit)
    exitButton.pack(pady=10, side=tk.BOTTOM)

    root.mainloop()


if __name__ == "__main__":
    data = main()
    gameWindow(data)
