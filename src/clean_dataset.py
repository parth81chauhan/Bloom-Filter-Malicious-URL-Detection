import re
import pandas as pd
import os

# ==========================================
# 1. FILE PATHS
# ==========================================

project_folder = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

input_file = os.path.join(
    project_folder, "data", "urlhaus.csv"
)

output_file = os.path.join(
    project_folder, "data", "clean_urls.csv"
)

test_file = os.path.join(
    project_folder, "data", "test_urls.csv"
)

print("=" * 55)
print("       URLHAUS DATASET CLEANING")
print("=" * 55)

# ==========================================
# 2. READ ORIGINAL DATASET
# ==========================================

header_line = None

with open(input_file, "r", encoding="utf-8") as file:
    for line_number, line in enumerate(file):
        if "id,dateadded,url,url_status" in line:
            header_line = line_number
            break

if header_line is None:
    raise ValueError("CSV header not found!")

df = pd.read_csv(
    input_file,
    skiprows=header_line,
    encoding="utf-8"
)

df.columns = (
    df.columns.str.strip()
    .str.lstrip("#")
    .str.strip()
)

print("\nOriginal records:", len(df))

# ==========================================
# 3. EXTRACT AND CLEAN URLS
# ==========================================

urls = df["url"].dropna().astype(str).str.strip()

# Remove empty URLs
urls = urls[urls != ""]

# Remove duplicate URLs
urls = urls.drop_duplicates()

print("Unique valid URL strings:", len(urls))

# ==========================================
# 4. CHECK MINIMUM DATA REQUIREMENT
# ==========================================

if len(urls) < 100000:
    raise ValueError(
        "Not enough unique URLs for the project!"
    )

# ==========================================
# 5. SHUFFLE DATASET
# ==========================================

urls = urls.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)

# ==========================================
# 6. SPLIT DATASET
# ==========================================

insertion_urls = urls.iloc[:100000]
testing_urls = urls.iloc[100000:]

# ==========================================
# 7. DEFANG URLS BEFORE STORAGE
# ==========================================

def defang_url(url):
    url = url.replace("https://", "hxxps://")
    url = url.replace("http://", "hxxp://")

    # Defang normal dots without changing existing [.]
    url = re.sub(r'(?<!\[)\.(?!\])', '[.]', url)

    return url
insertion_urls = insertion_urls.apply(defang_url)
testing_urls = testing_urls.apply(defang_url)


# ==========================================
# 8. SAVE BOTH DATASETS
# ==========================================

insertion_urls.to_csv(
    output_file,
    index=False,
    header=["url"]
)

testing_urls.to_csv(
    test_file,
    index=False,
    header=["url"]
)


# ==========================================
# 9. DISPLAY RESULTS
# ==========================================

print("\nDATASET SPLIT RESULTS")
print("-" * 40)

print("URLs for Bloom Filter:", len(insertion_urls))
print("URLs for testing:", len(testing_urls))

print("\nFILES CREATED")
print("-" * 40)

print("clean_urls.csv")
print("test_urls.csv")

print("\n" + "=" * 55)
print("       DATASET CLEANING COMPLETED")
print("=" * 55)