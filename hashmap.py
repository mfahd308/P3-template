
class GameHashMap:
    def __init__(self, games):
        """initialize hash map with given data"""

        self.game_map = {}
        self._create_game_hash_map(games)

    def _create_game_hash_map(self, games):
        """fill hash map"""

        for game in games:

            self.game_map[game.title] = {
                "genre": game.genre,
                "rating": game.rating,
                "platform": game.platform
            }

    def search_game_by_title(self, title):
        """search for game with title"""

        title_lower = title.lower()

        for key in self.game_map.keys():

            if key.lower() == title_lower:  # case-insensitive match for search

                return self.game_map[key]

        return None
