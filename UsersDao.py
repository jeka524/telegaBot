import sqlite3


class UsersDao:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_users(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `users`").fetchall()

    def get_user(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id, )).fetchone()

    def users_exist(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id):
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`) VALUES (?)", (user_id,))

    def update_user(self, user_id, photo_position: int):
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `photo_position` = ? WHERE `user_id` = ?",
                                       (photo_position, user_id,))

    def close(self):
        self.cursor.close()
        self.connection.close()
