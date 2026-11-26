
import csv
import os
import matplotlib.pyplot as plt


# ==========================================
# 1. FILE PATHS
# ==========================================

project_folder = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

input_file = os.path.join(
    project_folder, "data", "configuration_results.csv"
)

output_folder = os.path.join(
    project_folder, "results"
)

os.makedirs(output_folder, exist_ok=True)


# ==========================================
# 2. LOAD RESULTS
# ==========================================

results = []

with open(input_file, "r", encoding="utf-8") as file:

    reader = csv.DictReader(file)

    for row in reader:
        results.append({
            "target": float(row["target"]),
            "hashes": int(row["hashes"]),
            "memory": float(row["memory"]),
            "theoretical": float(row["theoretical"]),
            "observed": float(row["observed"])
        })


targets = [r["target"] for r in results]
hashes = [r["hashes"] for r in results]
memory = [r["memory"] for r in results]
theoretical = [r["theoretical"] for r in results]
observed = [r["observed"] for r in results]


# ==========================================
# 3. GRAPH 1: TARGET VS MEMORY
# ==========================================

plt.figure(figsize=(8, 5))

plt.plot(targets, memory, marker="o")

plt.xlabel("Target False Positive Rate (%)")
plt.ylabel("Memory Usage (KB)")
plt.title("False Positive Target vs Memory Usage")

plt.grid(True)
plt.tight_layout()

plt.savefig(
    os.path.join(output_folder, "memory_comparison.png"),
    dpi=300
)

plt.close()


# ==========================================
# 4. GRAPH 2: HASHES VS OBSERVED RATE
# ==========================================

plt.figure(figsize=(8, 5))

plt.plot(hashes, observed, marker="o")

plt.xlabel("Number of Hash Functions")
plt.ylabel("Observed False Positive Rate (%)")
plt.title("Hash Functions vs Observed False Positive Rate")

plt.grid(True)
plt.tight_layout()

plt.savefig(
    os.path.join(output_folder, "hash_comparison.png"),
    dpi=300
)

plt.close()


# ==========================================
# 5. GRAPH 3: THEORETICAL VS OBSERVED
# ==========================================

x = list(range(len(targets)))

width = 0.35

plt.figure(figsize=(9, 5))

plt.bar(
    [i - width / 2 for i in x],
    theoretical,
    width,
    label="Theoretical"
)

plt.bar(
    [i + width / 2 for i in x],
    observed,
    width,
    label="Observed"
)

plt.xticks(x, [str(t) + "%" for t in targets])

plt.xlabel("Target False Positive Rate")
plt.ylabel("False Positive Rate (%)")
plt.title("Theoretical vs Observed False Positive Rate")

plt.legend()
plt.grid(axis="y")
plt.tight_layout()

plt.savefig(
    os.path.join(output_folder, "theoretical_vs_observed.png"),
    dpi=300
)

plt.close()


# ==========================================
# 6. COMPLETION
# ==========================================

print("=" * 50)
print("       GRAPHS GENERATED SUCCESSFULLY")
print("=" * 50)

print("\nSaved graphs in:", output_folder)

print("\n1. memory_comparison.png")
print("2. hash_comparison.png")
print("3. theoretical_vs_observed.png")
