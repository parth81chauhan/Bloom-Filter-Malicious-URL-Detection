
import pandas as pd
import os

# Find the project directory
project_folder = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# CSV file location
file_path = os.path.join(
    project_folder, "data", "urlhaus.csv"
)

print("=" * 50)
print("       URLHAUS DATASET INSPECTION")
print("=" * 50)

# Check whether the file exists
if not os.path.exists(file_path):
    print("Error: urlhaus.csv not found!")
    exit()

# Find the actual CSV header line
header_line = None

with open(file_path, "r", encoding="utf-8") as file:
    for line_number, line in enumerate(file):
        if "id,dateadded,url,url_status" in line:
            header_line = line_number
            break

if header_line is None:
    print("Error: CSV header not found!")
    exit()

# Read CSV starting from the actual header
df = pd.read_csv(
    file_path,
    skiprows=header_line,
    encoding="utf-8"
)

# Remove the # symbol from the first column name
df.columns = (
    df.columns
    .str.strip()
    .str.lstrip("#")
    .str.strip()
)

# Basic dataset information
total_records = len(df)

# Extract and clean URL column
urls = df["url"].dropna().astype(str).str.strip()
urls = urls[urls != ""]

# Calculate statistics
unique_urls = urls.nunique()
duplicate_urls = len(urls) - unique_urls
missing_urls = df["url"].isna().sum()

# URL status information
status_counts = df["url_status"].value_counts()

# Display results
print("\n1. DATASET INFORMATION")
print("-" * 40)

print("Total records:", total_records)
print("Unique URLs:", unique_urls)
print("Duplicate URLs:", duplicate_urls)
print("Missing URLs:", missing_urls)

print("\n2. URL STATUS")
print("-" * 40)

print(status_counts.to_string())

print("\n3. FILE INFORMATION")
print("-" * 40)

file_size = os.path.getsize(file_path) / (1024 * 1024)
print(f"File size: {file_size:.2f} MB")

print("\n4. SAMPLE URLS")
print("-" * 40)

for url in urls.head(5):
    print(url)

print("\n5. COLUMN NAMES")
print("-" * 40)

print(df.columns.tolist())

print("\n" + "=" * 50)
print("       DATASET INSPECTION COMPLETED")
print("=" * 50)
