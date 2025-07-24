from app.utils.db_manager import DatabaseManager

db = DatabaseManager()
db.connect()

def tables():
    # ----- links táblázat létrehozása -----
    db.execute("""CREATE TABLE IF NOT EXISTS links (
                LinkID INTEGER PRIMARY KEY AUTOINCREMENT,
                Link TEXT NOT NULL,
                Title TEXT NOT NULL,
                LastUpdate DATETIME DEFAULT CURRENT_TIMESTAMP,
                Added DATETIME DEFAULT CURRENT_TIMESTAMP
            );""")
    
    db.execute("""CREATE TRIGGER IF NOT EXISTS update_links_lastupdate
                AFTER UPDATE ON links
                FOR EACH ROW
                BEGIN
                    UPDATE links
                    SET LastUpdate = CURRENT_TIMESTAMP
                    WHERE LinkID = OLD.LinkID;
            END;""")
    # ----- ##### -----

tables()