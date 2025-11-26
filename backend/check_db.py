import sqlite3
from pathlib import Path

# Pfad zur Datenbank
db_path = Path("viralytics.db")

if not db_path.exists():
    print("❌ FEHLER: Die Datei 'viralytics.db' existiert noch nicht.")
else:
    print(f"✅ Die Datenbank wurde gefunden: {db_path.absolute()}")
    
    # Verbindung herstellen
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Die letzten 5 Einträge abrufen
        cursor.execute("SELECT id, created_at, video_filename, score, label FROM analyses ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        
        if not rows:
            print("ℹ️ Die Tabelle ist noch leer.")
        else:
            print(f"\nGefundene Einträge: {len(rows)}")
            print("-" * 60)
            print(f"{'ID':<5} | {'Datum':<20} | {'Score':<10} | {'Label':<10} | {'Datei'}")
            print("-" * 60)
            for row in rows:
                print(f"{row[0]:<5} | {row[1][:19]:<20} | {row[3]:<10.4f} | {row[4]:<10} | {row[2]}")
                
    except sqlite3.OperationalError:
        print("❌ FEHLER: Die Tabelle 'analyses' wurde noch nicht erstellt.")
        
    conn.close()