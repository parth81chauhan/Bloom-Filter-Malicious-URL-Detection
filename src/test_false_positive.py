
import csv
import os
from bloom_filter import BloomFilter


# ==========================================
# 1. FILE PATHS
# ==========================================

project_folder = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

training_file = os.path.join(
    project_folder, "data", "clean_urls.csv"
)

testing_file = os.path.join(
    project_folder, "data", "test_urls.csv"
)


print("=" * 55)
print("       FALSE POSITIVE RATE TESTING")
print("=" * 55)


# ==========================================
# 2. LOAD TRAINING URLS
# ==========================================

training_urls = []

with open(training_file, "r", encoding="utf-8-sig", newline="") as file:

    reader = csv.DictReader(file)

    for row in reader:
        url = row["url"].strip()

        if url:
            training_urls.append(url)


print("\nTraining URLs loaded:", len(training_urls))


# ==========================================
# 3. CREATE AND BUILD BLOOM FILTER
# ==========================================

bloom = BloomFilter(
    expected_items=len(training_urls),
    false_positive_rate=0.01
)

print("\nBuilding Bloom Filter...")

for url in training_urls:
    bloom.add(url)

print("Bloom Filter construction completed!")


# ==========================================
# 4. TEST ALL NON-INSERTED URLS
# ==========================================

print("\nTesting all non-inserted URLs...")

total_test_urls = 0
false_positives = 0
true_negatives = 0

with open(testing_file, "r", encoding="utf-8-sig", newline="") as file:

    reader = csv.DictReader(file)

    for row in reader:

        url = row["url"].strip()

        if not url:
            continue

        total_test_urls += 1

        if bloom.contains(url):
            false_positives += 1
        else:
            true_negatives += 1


# ==========================================
# 5. CALCULATE OBSERVED RATE
# ==========================================

if total_test_urls > 0:

    observed_rate = (
        false_positives / total_test_urls
    ) * 100

else:
    observed_rate = 0


theoretical_rate = (
    bloom.get_theoretical_false_positive_rate() * 100
)


# ==========================================
# 6. DISPLAY RESULTS
# ==========================================

print("\n" + "=" * 55)
print("       FALSE POSITIVE TEST RESULTS")
print("=" * 55)

print("\nDATASET INFORMATION")
print("-" * 40)

print("Training URLs:", len(training_urls))
print("Testing URLs:", total_test_urls)

print("\nCLASSIFICATION RESULTS")
print("-" * 40)

print("False positives:", false_positives)
print("True negatives:", true_negatives)

print("\nFALSE POSITIVE RATE")
print("-" * 40)

print(f"Theoretical rate: {theoretical_rate:.4f}%")
print(f"Observed rate:    {observed_rate:.4f}%")

print("\nBLOOM FILTER INFORMATION")
print("-" * 40)

print("Bit array size:", bloom.size)
print("Hash functions:", bloom.hash_count)
print("Set bits:", bloom.get_set_bits())

print("\n" + "=" * 55)
print("       TESTING COMPLETED")
print("=" * 55)
