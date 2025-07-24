import sqlite3
import os
from dotenv import load_dotenv

# Betölti a környezeti változókat a .env fájlból
load_dotenv()

class DatabaseManager:
    
    def __init__(self):
        self.database_file = os.getenv('DATABASE_FILE')
        if not self.database_file:
            raise ValueError("A 'DATABASE_FILE' környezeti változó nincs beállítva a .env fájlban.")
        self.conn = None
        self.cursor = None

    def connect(self):
        """
        Létrehozza a kapcsolatot az SQLite adatbázissal.
        """
        try:
            self.conn = sqlite3.connect(self.database_file, check_same_thread=False)
            self.cursor = self.conn.cursor()
            print(f"Sikeresen csatlakozva az adatbázishoz: {self.database_file}")
        except sqlite3.Error as e:
            print(f"Hiba az adatbázishoz való csatlakozáskor: {e}")
            self.conn = None
            self.cursor = None
    
    def close(self):
        """
        Bezárja az adatbázis kapcsolatot.
        """
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
            print("Adatbázis kapcsolat bezárva.")

    def execute(self, query, params=()):
        """
        Végrehajt egy SQL lekérdezést (pl. INSERT, UPDATE, DELETE, CREATE TABLE).
        :param query: A végrehajtandó SQL lekérdezés.
        :param params: A lekérdezéshez tartozó paraméterek tuple-ként.
        :return: True, ha sikeres, False, ha hiba történt.
        """
        if not self.conn:
            print("Nincs aktív adatbázis kapcsolat. Kérjük, először csatlakozzon.")
            return False
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Hiba a lekérdezés végrehajtásakor: {e}")
            return False
        
    def fetch_all(self, query, params=()):
        """
        Végrehajt egy SELECT lekérdezést, és visszaadja az összes eredményt.
        :param query: A végrehajtandó SQL SELECT lekérdezés.
        :param params: A lekérdezéshez tartozó paraméterek tuple-ként.
        :return: Az eredmények listája, vagy üres lista hiba esetén.
        """
        if not self.conn:
            print("Nincs aktív adatbázis kapcsolat. Kérjük, először csatlakozzon.")
            return []
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Hiba az adatok lekérdezésekor: {e}")
            return []

    def fetch_one(self, query, params=()):
        """
        Végrehajt egy SELECT lekérdezést, és visszaadja az első eredményt.
        :param query: A végrehajtandó SQL SELECT lekérdezés.
        :param params: A lekérdezéshez tartozó paraméterek tuple-ként.
        :return: Az első eredmény, vagy None hiba esetén.
        """
        if not self.conn:
            print("Nincs aktív adatbázis kapcsolat. Kérjük, először csatlakozzon.")
            return None
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Hiba az adat lekérdezésekor: {e}")
            return None