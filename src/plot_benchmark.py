
import csv
import os
import matplotlib.pyplot as plt


project_folder = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

input_file = os.path.join(
    project_folder, "data", "benchmark_results.csv"
)

output_folder = os.path.join(
    project_folder, "results"
)

os.makedirs(output_folder, exist_ok=True)


# Load benchmark results
methods = []
existing_times = []
absent_times = []

with open(input_file, "r", encoding="utf-8") as file:

    reader = csv.DictReader(file)

    for row in reader:
        methods.append(row["Method"])
        existing_times.append(
            float(row["Existing Lookup (ms)"])
        )
        absent_times.append(
            float(row["Absent Lookup (ms)"])
        )


# Graph 1: Existing URL lookup
plt.figure(figsize=(8, 5))

plt.bar(methods, existing_times)

plt.xlabel("Lookup Method")
plt.ylabel("Time (milliseconds)")
plt.title("Existing URL Lookup Performance")

plt.tight_layout()

plt.savefig(
    os.path.join(output_folder, "existing_lookup_comparison.png"),
    dpi=300
)

plt.close()


# Graph 2: Absent URL lookup
plt.figure(figsize=(8, 5))

plt.bar(methods, absent_times)

plt.xlabel("Lookup Method")
plt.ylabel("Time (milliseconds)")
plt.title("Absent URL Lookup Performance")

plt.tight_layout()

plt.savefig(
    os.path.join(output_folder, "absent_lookup_comparison.png"),
    dpi=300
)

plt.close()


print("=" * 50)
print("BENCHMARK GRAPHS GENERATED")
print("=" * 50)

print("\nSaved in:", output_folder)

print("1. existing_lookup_comparison.png")
print("2. absent_lookup_comparison.png")
