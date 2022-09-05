import json
import sqlite3
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print(f"Use: {sys.argv[0]} data_dir db_name")
    exit(1)

data_dir = Path(sys.argv[1])

db = sqlite3.connect(sys.argv[2])
db.execute("""
CREATE TABLE IF NOT EXISTS signs (
    number INTEGER PRIMARY KEY,
    gloss TEXT NOT NULL DEFAULT "" COLLATE NOCASE,
    notation TEXT NOT NULL DEFAULT "",
    modified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_by TEXT NOT NULL
)""")

for info_file in data_dir.glob('**/*.json'):
    info = json.loads(info_file.read_text())
    cuts = info.get('cuts')
    if cuts is None or len(cuts)<1:
        continue
    db.cursor().executemany("""INSERT OR IGNORE
        INTO signs(number, gloss, modified_by)
        VALUES (?,?,?)
    """, [(c["number"], c["gloss"], "system")
        for c in cuts
        if "gloss" in c and c["gloss"] != "Toma falsa"])

db.commit()
