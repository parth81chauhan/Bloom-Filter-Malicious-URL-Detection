
import csv
import sqlite3
import os

# ==========================================
# 1. FILE PATHS
# ==========================================

project_folder = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

csv_file = os.path.join(
    project_folder, "data", "clean_urls.csv"
)

database_folder = os.path.join(
    project_folder, "database"
)

database_file = os.path.join(
    database_folder, "urlhaus.db"
)

print("=" * 55)
print("       URLHAUS SQLITE DATABASE CREATION")
print("=" * 55)

# ==========================================
# 2. CHECK CSV FILE
# ==========================================

if not os.path.exists(csv_file):
    raise FileNotFoundError("clean_urls.csv not found!")

# Create database folder if it doesn't exist
os.makedirs(database_folder, exist_ok=True)

# ==========================================
# 3. CONNECT TO SQLITE DATABASE
# ==========================================

connection = sqlite3.connect(database_file)
cursor = connection.cursor()

print("\nDatabase connection successful!")

# ==========================================
# 4. CREATE TABLE
# ==========================================

cursor.execute("""
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL UNIQUE
    )
""")

# Clear previous records if running again
cursor.execute("DELETE FROM urls")

print("URLs table created successfully!")

# ==========================================
# 5. READ CSV AND INSERT URLS
# ==========================================

batch = []
inserted_count = 0

with open(csv_file, "r", encoding="utf-8", newline="") as file:

    reader = csv.DictReader(file)

    if not reader.fieldnames or "url" not in reader.fieldnames:
        raise ValueError("The CSV must contain a 'url' column!")

    for row in reader:

        url = (row.get("url") or "").strip()

        if url:
            batch.append((url,))

        # Insert in batches of 5000
        if len(batch) >= 5000:

            cursor.executemany(
                "INSERT OR IGNORE INTO urls (url) VALUES (?)",
                batch
            )

            inserted_count += cursor.rowcount
            batch.clear()

    # Insert remaining URLs
    if batch:

        cursor.executemany(
            "INSERT OR IGNORE INTO urls (url) VALUES (?)",
            batch
        )

        inserted_count += cursor.rowcount

# ==========================================
# 6. COMMIT CHANGES
# ==========================================

connection.commit()

# ==========================================
# 7. VERIFY DATABASE RECORDS
# ==========================================

cursor.execute("SELECT COUNT(*) FROM urls")

total_records = cursor.fetchone()[0]

# ==========================================
# 8. TEST A DATABASE LOOKUP
# ==========================================

cursor.execute("SELECT url FROM urls LIMIT 1")

sample = cursor.fetchone()

if sample:
    cursor.execute(
        "SELECT 1 FROM urls WHERE url = ?",
        (sample[0],)
    )

    lookup_result = cursor.fetchone()

    print("\nDatabase lookup test: SUCCESS")

else:
    print("\nDatabase lookup test: NO RECORDS FOUND")

# ==========================================
# 9. DISPLAY RESULTS
# ==========================================

database_size = os.path.getsize(database_file) / (1024 * 1024)

print("\nDATABASE INFORMATION")
print("-" * 40)

print("Inserted records:", inserted_count)
print("Total database records:", total_records)
print(f"Database size: {database_size:.2f} MB")

print("\nDatabase location:")
print(database_file)

print("\n" + "=" * 55)
print("       DATABASE CREATION COMPLETED")
print("=" * 55)

# ==========================================
# 10. CLOSE CONNECTION
# ==========================================

connection.close()
