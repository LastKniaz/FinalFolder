class AnimeDatabaseManager:
    def __init__(self):
        self.anime_list = []

    def add_anime(self, anime):
        self.anime_list.append(anime)

    def remove_anime(self, anime):
        self.anime_list.remove(anime)

    def is_anime_in_database(self, anime_name):
        return anime_name in self.anime_list