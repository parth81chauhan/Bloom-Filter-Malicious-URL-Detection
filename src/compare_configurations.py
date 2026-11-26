
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


# ==========================================
# 2. LOAD DATASETS
# ==========================================

def load_urls(file_path):

    urls = []

    with open(file_path, "r", encoding="utf-8-sig", newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:
            url = row["url"].strip()

            if url:
                urls.append(url)

    return urls


training_urls = load_urls(training_file)
testing_urls = load_urls(testing_file)


# ==========================================
# 3. CONFIGURATIONS
# ==========================================

false_positive_targets = [
    0.10,
    0.05,
    0.01,
    0.005,
    0.001
]

results = []


# ==========================================
# 4. RUN EXPERIMENTS
# ==========================================

print("=" * 75)
print("             BLOOM FILTER CONFIGURATION COMPARISON")
print("=" * 75)

for target in false_positive_targets:

    bloom = BloomFilter(
        expected_items=len(training_urls),
        false_positive_rate=target
    )

    for url in training_urls:
        bloom.add(url)

    false_positives = 0

    for url in testing_urls:

        if bloom.contains(url):
            false_positives += 1

    observed_rate = (
        false_positives / len(testing_urls)
    ) * 100

    theoretical_rate = (
        bloom.get_theoretical_false_positive_rate() * 100
    )

    memory_kb = bloom.get_memory_usage() / 1024

    results.append({
        "target": target * 100,
        "bits": bloom.size,
        "hashes": bloom.hash_count,
        "memory": memory_kb,
        "false_positives": false_positives,
        "theoretical": theoretical_rate,
        "observed": observed_rate
    })


# ==========================================
# 5. DISPLAY RESULTS
# ==========================================

print("\n{:<10} {:<12} {:<10} {:<12} {:<12}".format(
    "Target %", "Bits", "Hashes", "Memory KB", "False Pos."
))

print("-" * 75)

for result in results:

    print("{:<10.2f} {:<12} {:<10} {:<12.2f} {:<12}".format(
        result["target"],
        result["bits"],
        result["hashes"],
        result["memory"],
        result["false_positives"]
    ))


print("\nFALSE POSITIVE RATE COMPARISON")
print("-" * 75)

print("{:<12} {:<18} {:<18}".format(
    "Target %", "Theoretical %", "Observed %"
))

for result in results:

    print("{:<12.2f} {:<18.4f} {:<18.4f}".format(
        result["target"],
        result["theoretical"],
        result["observed"]
    ))


# ==========================================
# 6. SAVE RESULTS
# ==========================================

output_file = os.path.join(
    project_folder, "data", "configuration_results.csv"
)

with open(output_file, "w", newline="", encoding="utf-8") as file:

    fieldnames = [
        "target",
        "bits",
        "hashes",
        "memory",
        "false_positives",
        "theoretical",
        "observed"
    ]

    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(results)


print("\nResults saved to:", output_file)

print("\n" + "=" * 75)
print("             EXPERIMENT COMPLETED")
print("=" * 75)
