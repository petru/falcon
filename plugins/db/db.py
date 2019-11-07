import sqlite3
import datetime

class Database:

    def __init__(self, db='testy.db'):
        self._conn = sqlite3.connect(db)
        self._cursor = self._conn.cursor()
        self._cursor.execute('CREATE TABLE IF NOT EXISTS definitions (date text, author text, term text, definition text)')


    def save(self):
        self._conn.commit()
        # self._conn.close()
        return

    def add_term(self, author, term, definition):
        q = (datetime.datetime.now().timestamp(), author, term, definition)
        self._cursor.execute("INSERT INTO definitions VALUES (?,?,?,?)", q)
        self.save()
        return

    def remove_term(self, term):
        q = (term,)
        self._cursor.execute('DELETE FROM definitions WHERE term=?', q)
        self.save()
        return

    def lookup(self, query):
        q = (query,)
        self._cursor.execute('SELECT definition FROM definitions WHERE term LIKE ?', q)
        result = self._cursor.fetchall()
        return result
        

    def update(self, term, definition):
        return

    def append(self, term, definition):
        return