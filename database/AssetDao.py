import sqlite3


class AssetDao:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def clear(self):
        with self.connection:
            self.cursor.execute("DELETE FROM `asset`")

    def get_photo_id_by_name(self, file_name: str) -> str:
        with self.connection:
            return self.cursor.execute("SELECT `file_id` FROM `asset` WHERE file_name = ?", (file_name, )).fetchone()[0]

    def add_asset(self, file_id, filename):
        with self.connection:
            self.cursor.execute("INSERT INTO `asset` (`file_id`, `file_name`) VALUES (?, ?)", (file_id, filename))

    def close(self):
        self.cursor.close()
        self.connection.close()
