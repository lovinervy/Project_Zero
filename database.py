import os
import sqlite3


class DB:
    DATABASE_PATH = 'DATABASE'

    def __init__(self) -> None:
        if not os.path.isdir(self.DATABASE_PATH):
            os.makedirs(self.DATABASE_PATH)
        self.connect = sqlite3.connect(f'{self.DATABASE_PATH}/DATABASE.db', check_same_thread=False)
        self.cursor = self.connect.cursor()
        self.initDB()
        self.cursor.execute('PRAGMA foreign_keys = ON')

    def initDB(self):
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS youtube('\
                        'id INTEGER PRIMARY KEY AUTOINCREMENT, '\
                        'url TEXT NOT NULL' \
                        ');'
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS translates(' \
                        'id INTEGER PRIMARY KEY AUTOINCREMENT, '\
                        'youtube_id INTEGER NOT NULL, '\
                        'language TEXT, '\
                        'FOREIGN KEY (youtube_id) REFERENCES youtube(id) ' \
                        'ON DELETE CASCADE'\
                        ');'
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS subtitles(' \
                        'id INTEGER PRIMARY KEY AUTOINCREMENT, '\
                        'translates_id INTEGER NOT NULL, '\
                        'name TEXT NOT NULL, '\
                        'FOREIGN KEY (translates_id) REFERENCES translates(id) '\
                        'ON DELETE CASCADE'\
                        ');'
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS voiceovers(' \
                        'id INTEGER PRIMARY KEY AUTOINCREMENT, '\
                        'translates_id INTEGER NOT NULL, '\
                        'name TEXT NOT NULL, '\
                        'FOREIGN KEY (translates_id) REFERENCES translates(id) '\
                        'ON DELETE CASCADE'\
                        ');'
        )
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS video(' \
                        'id INTEGER PRIMARY KEY AUTOINCREMENT, '\
                        'youtube_id INTEGER NOT NULL, '\
                        'name TEXT,'\
                        'FOREIGN KEY (youtube_id) REFERENCES youtube(id) '\
                        'ON DELETE CASCADE'\
                        ');'
        )
        self.connect.commit()

    def insert_youtube(self, url: str) -> tuple:
        sql = ''' INSERT INTO youtube(url) VALUES(?); '''
        self.cursor.execute(sql, (url,))
        self.connect.commit()
        return self.cursor.lastrowid

    def get_youtube_id(self, url: str) -> tuple | None:
        sql = "SELECT id FROM youtube WHERE url = ?;"
        self.cursor.execute(sql, (url,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None
    
    def update_youtube(self, youtube_id: int, url: str):
        sql = ''' UPDATE youtube set url = ? WHERE id = ?; '''
        self.cursor.execute(sql, (url, youtube_id))
        self.connect.commit()

    def delete_youtube(self, youtube_id: int):
        sql = ''' DELETE FROM youtube WHERE id = ? ;'''
        self.cursor.execute(sql, (youtube_id, ))
        self.connect.commit()

    def insert_translates(self, youtube_id: int, language: str):
        sql = ''' INSERT INTO translates(youtube_id, language) VALUES(?, ?); '''
        self.cursor.execute(sql, (youtube_id, language))
        self.connect.commit()
        return self.cursor.lastrowid

    def select_translates(self, youtube_id: int):
        sql = ''' SELECT * FROM translates WHERE youtube_id = ?; '''
        self.cursor.execute(sql, (youtube_id,))
        result = self.cursor.fetchall()
        return result

    def update_translates(self, translates_id: int, language: str):
        sql = ''' UPDATE translates SET language = ? WHERE id = ?; '''
        self.cursor.execute(sql, (language, translates_id))
        self.connect.commit()

    def delete_translates(self, translates_id: int):
        sql = ''' DELETE FROM translates WHERE id = ?; '''
        self.cursor.execute(sql, (translates_id,))
        self.connect.commit()

    def insert_subtitles(self, translates_id: int, name: str):
        sql = ''' INSERT INTO subtitles(translates_id, name) VALUES(?, ?); '''
        self.cursor.execute(sql, (translates_id, name))
        self.connect.commit()
        return self.cursor.lastrowid

    def select_subtitles(self, translates_id: int):
        sql = ''' SELECT * FROM subtitles WHERE translates_id = ?;'''
        self.cursor.execute(sql, (translates_id,))
        result = self.cursor.fetchone()
        return result

    def update_subtitles(self, subtitles_id: int, name: str):
        sql = ''' UPDATE subtitles SET name = ? WHERE id = ?;'''
        self.cursor.execute(sql, (name, subtitles_id))
        self.connect.commit()

    def delete_subtitles(self, subtitles_id: int):
        sql = ''' DELETE FROM subtitles WHERE id = ?; '''
        self.cursor.execute(sql, (subtitles_id,))
        self.connect.commit()

    def insert_voiceovers(self, translates_id: int, name: str):
        sql = ''' INSERT INTO voiceovers(translates_id, name) VALUES(?, ?) '''
        self.cursor.execute(sql, (translates_id, name))
        self.connect.commit()
        return self.cursor.lastrowid

    def select_voiceovers(self, translates_id: int) -> tuple | None:
        sql = ''' SELECT * FROM voiceovers WHERE translates_id = ?;'''
        self.cursor.execute(sql, (translates_id,))
        result = self.cursor.fetchone()
        return result

    def update_voiceovers(self, voiceovers_id: int, name: str):
        sql = ''' UPDATE voiceovers SET name = ? WHERE id = ?;'''
        self.cursor.execute(sql, (name, voiceovers_id))
        self.connect.commit()

    def delete_voiceovers(self, voiceovers_id: int):
        sql = ''' DELETE FROM voiceovers WHERE id = ?; '''
        self.cursor.execute(sql, (voiceovers_id,))
        self.connect.commit()

    def insert_video(self, youtube_id: int, name: str):
        sql = ''' INSERT INTO video(youtube_id, name) VALUES(?, ?); '''
        self.cursor.execute(sql, (youtube_id, name))
        self.connect.commit()
        return self.cursor.lastrowid

    def select_video(self, youtube_id: int) -> tuple:
        sql = ''' SELECT * FROM video WHERE youtube_id = ?; '''
        self.cursor.execute(sql, (youtube_id,))
        result = self.cursor.fetchone()
        return result
    
    def update_video(self, video_id: int, name: str):
        sql = ''' UPDATE  video SET name = ? WHERE id = video_id; '''
        self.cursor.execute(sql, (name, video_id))
        self.connect.commit()
    
    def delete_video(self, video_id: int):
        sql = ''' DELETE FROM video WHERE id = ?; '''
        self.cursor.execute(sql, (video_id,))
        self.connect.commit()
    

if __name__ == '__main__':
    db = DB()
    breakpoint()