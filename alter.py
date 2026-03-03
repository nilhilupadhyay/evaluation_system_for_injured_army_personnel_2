import sqlite3
import os


db_path = os.path.join('instance', 'projectdata.db')


conn = sqlite3.connect(db_path)
cursor = conn.cursor()


cursor.execute("PRAGMA table_info(impact_health)")
columns = cursor.fetchall()


if len(columns) > 0:
    #cursor.execute("ALTER TABLE impact_health ADD COLUMN latitude REAL")
    cursor.execute("ALTER TABLE impact_health ADD COLUMN diagnosis_result VARCHAR(100)  ")
else:
    print("Table 'impact_health' does not exist.")


conn.commit()
conn.close()
