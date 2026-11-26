
import csv
import sqlite3
import os
import time
import statistics
import sys

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

database_file = os.path.join(
    project_folder, "database", "urlhaus.db"
)


# ==========================================
# 2. LOAD URL DATA
# ==========================================

def load_urls(file_path):

    urls = []

    with open(file_path, "r", encoding="utf-8-sig", newline="") as file:

        reader = csv.DictReader(file)

        for row in reader:

            url = (row.get("url") or "").strip()

            if url:
                urls.append(url)

    return urls


training_urls = load_urls(training_file)
testing_urls = load_urls(testing_file)

# Use the same 1,000 URLs for each method
positive_tests = training_urls[:1000]
negative_tests = testing_urls[:1000]


# ==========================================
# 3. BUILD BLOOM FILTER AND PYTHON SET
# ==========================================

bloom = BloomFilter(
    expected_items=len(training_urls),
    false_positive_rate=0.01
)

for url in training_urls:
    bloom.add(url)

python_set = set(training_urls)


# ==========================================
# 4. CONNECT TO SQLITE
# ==========================================

connection = sqlite3.connect(database_file)
cursor = connection.cursor()


# ==========================================
# 5. BENCHMARK FUNCTION
# ==========================================

def benchmark(method, test_urls, repetitions=5):

    times = []

    for _ in range(repetitions):

        start = time.perf_counter()

        for url in test_urls:
            method(url)

        end = time.perf_counter()

        times.append(
            (end - start) / len(test_urls) * 1000
        )

    return statistics.median(times)


# ==========================================
# 6. LOOKUP METHODS
# ==========================================

def bloom_lookup(url):
    return bloom.contains(url)


def set_lookup(url):
    return url in python_set


def database_lookup(url):

    cursor.execute(
        "SELECT 1 FROM urls WHERE url = ?",
        (url,)
    )

    return cursor.fetchone() is not None


methods = {
    "Bloom Filter": bloom_lookup,
    "Python Set": set_lookup,
    "SQLite": database_lookup
}


# ==========================================
# 7. RUN BENCHMARKS
# ==========================================

print("=" * 65)
print("             LOOKUP PERFORMANCE COMPARISON")
print("=" * 65)

print("\nTesting 1,000 existing and 1,000 absent URLs.")
print("Each benchmark is repeated 5 times.")

results = {}

for name, method in methods.items():

    positive_time = benchmark(method, positive_tests)
    negative_time = benchmark(method, negative_tests)

    results[name] = {
        "positive": positive_time,
        "negative": negative_time
    }


# ==========================================
# 8. DISPLAY PERFORMANCE RESULTS
# ==========================================

print("\nMEDIAN LOOKUP TIME")
print("-" * 65)

print("{:<18} {:<20} {:<20}".format(
    "Method", "Existing (ms)", "Absent (ms)"
))

for name, result in results.items():

    print("{:<18} {:<20.6f} {:<20.6f}".format(
        name,
        result["positive"],
        result["negative"]
    ))


# ==========================================
# 9. MEMORY COMPARISON
# ==========================================

set_memory = (
    sys.getsizeof(python_set)
    + sum(sys.getsizeof(url) for url in python_set)
)

bloom_memory = bloom.get_memory_usage()

database_memory = os.path.getsize(database_file)

print("\nMEMORY / STORAGE COMPARISON")
print("-" * 65)

print(f"Bloom Filter: {bloom_memory / 1024:.2f} KB")
print(f"Python Set:   {set_memory / 1024:.2f} KB (approximate)")
print(f"SQLite DB:    {database_memory / (1024 * 1024):.2f} MB")


# ==========================================
# 10. SAVE BENCHMARK RESULTS
# ==========================================

output_file = os.path.join(
    project_folder, "data", "benchmark_results.csv"
)

with open(output_file, "w", newline="", encoding="utf-8") as file:

    writer = csv.writer(file)

    writer.writerow([
        "Method",
        "Existing Lookup (ms)",
        "Absent Lookup (ms)"
    ])

    for name, result in results.items():

        writer.writerow([
            name,
            result["positive"],
            result["negative"]
        ])


connection.close()

print("\nResults saved to:", output_file)

print("\n" + "=" * 65)
print("             BENCHMARK COMPLETED")
print("=" * 65)
