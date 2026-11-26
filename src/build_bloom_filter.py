
import csv
import os

from bloom_filter import BloomFilter


# ==========================================
# 1. FILE PATH
# ==========================================

project_folder = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

csv_file = os.path.join(
    project_folder, "data", "clean_urls.csv"
)

test_file = os.path.join(
    project_folder, "data", "test_urls.csv"
)


print("=" * 55)
print("       BLOOM FILTER IMPLEMENTATION")
print("=" * 55)


# ==========================================
# 2. LOAD INSERTION URLS
# ==========================================

urls = []

with open(csv_file, "r", encoding="utf-8") as file:

    reader = csv.DictReader(file)

    for row in reader:
        url = row["url"].strip()

        if url:
            urls.append(url)


print("\nTotal URLs loaded:", len(urls))


# ==========================================
# 3. CREATE BLOOM FILTER
# ==========================================

bloom = BloomFilter(
    expected_items=len(urls),
    false_positive_rate=0.01
)

print("\nBLOOM FILTER CONFIGURATION")
print("-" * 40)

print("Expected items:", bloom.expected_items)
print("Bit array size:", bloom.size)
print("Hash functions:", bloom.hash_count)


# ==========================================
# 4. INSERT URLS
# ==========================================

print("\nInserting URLs into Bloom Filter...")

for url in urls:
    bloom.add(url)

print("Insertion completed!")


# ==========================================
# 5. TEST INSERTED URLS
# ==========================================

print("\nINSERTED URL TEST")
print("-" * 40)

present_url = urls[0]

if bloom.contains(present_url):
    print("Inserted URL: FOUND")
else:
    print("Inserted URL: NOT FOUND")



# ==========================================
# 6. TEST URL NOT INSERTED
# ==========================================

print("\nNON-INSERTED URL TEST")
print("-" * 40)

if not os.path.isfile(test_file):
    print("Testing file not found!")
    print("Expected location:", repr(test_file))

else:
    with open(
        test_file,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        test_row = next(reader, None)

        if test_row is None:
            print("Testing dataset is empty!")

        else:
            test_url = test_row["url"].strip()

            result = bloom.contains(test_url)

            if result:
                print("Non-inserted URL: PROBABLY PRESENT")
                print("This may be a false positive.")

            else:
                print("Non-inserted URL: DEFINITELY NOT PRESENT")


# ==========================================
# 7. BLOOM FILTER STATISTICS
# ==========================================

print("\nBLOOM FILTER STATISTICS")
print("-" * 40)

print("Inserted items:", bloom.item_count)

print("Set bits:", bloom.get_set_bits())

print(
    "Bit array memory:",
    f"{len(bloom.bit_array):,} bytes"
)

print(
    "Python object memory:",
    f"{bloom.get_memory_usage():,} bytes"
)

print(
    "Theoretical false-positive rate:",
    f"{bloom.get_theoretical_false_positive_rate() * 100:.4f}%"
)


print("\n" + "=" * 55)
print("       BLOOM FILTER TEST COMPLETED")
print("=" * 55)
