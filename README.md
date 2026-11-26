# Bloom Filter for Malicious URL Detection

## 1. Project Overview

This project implements a **Bloom Filter** to check whether a URL may exist in a known collection of malicious URLs.

A Bloom Filter is a space-efficient probabilistic data structure that supports fast membership checking. It can determine that an item is definitely not present or that it may be present.

The project compares Bloom Filter performance with Python Set and SQLite database lookups.

## 2. Objectives

- Implement a Bloom Filter from scratch.
- Use SHA-256-based double hashing.
- Store URL data in a bit array.
- Measure theoretical and observed false-positive rates.
- Compare different Bloom Filter configurations.
- Analyze memory consumption and lookup time.
- Compare Bloom Filter, Python Set, and SQLite performance.
- Study the probability calculations behind Bloom Filters.

## 3. Dataset

**Dataset source:** URLhaus

Dataset inspection results:

| Information | Result |
|---|---:|
| Total records | 174,790 |
| Unique URLs | 174,790 |
| Duplicate URLs | 0 |
| Missing URLs | 0 |
| Online URLs | 116,772 |
| Offline URLs | 58,018 |
| Original dataset size | 41.76 MiB |

File sizes in this table use binary units (1 MiB = 1,048,576 bytes).

The dataset is cleaned and defanged before processing.

### Dataset split

| Dataset | Number of URLs |
|---|---:|
| Training URLs | 100,000 |
| Testing URLs | 74,790 |
| Total | 174,790 |

The Bloom Filter is built using the 100,000 training URLs. The remaining 74,790 URLs are used for false-positive testing.

**Safety:** The URLs are treated only as text. They are not visited, opened, or executed.

## 4. Technologies Used

- Python
- SQLite
- SHA-256 hashing
- Matplotlib
- CSV data processing

## 5. Project Structure

```text
Bloom Filter project/
│
├── data/
│   ├── urlhaus.csv
│   ├── clean_urls.csv
│   ├── test_urls.csv
│   ├── configuration_results.csv
│   └── benchmark_results.csv
│
├── app.py
├── templates/
│   └── index.html
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── images/
│
├── database/
│   └── urlhaus.db
│
├── results/
│   ├── memory_comparison.png
│   ├── hash_comparison.png
│   ├── theoretical_vs_observed.png
│   ├── existing_lookup_comparison.png
│   └── absent_lookup_comparison.png
│
├── src/
│   ├── inspect_dataset.py
│   ├── clean_dataset.py
│   ├── create_database.py
│   ├── bloom_filter.py
│   ├── build_bloom_filter.py
│   ├── test_false_positive.py
│   ├── compare_configurations.py
│   ├── plot_results.py
│   ├── benchmark_lookup.py
│   ├── plot_benchmark.py
│   └── probability_analysis.py
│
├── notebooks/
│   └── bloom_filter_analysis.ipynb
│
├── reports/
│   ├── data_quality_log.md
│   ├── er_diagram.mmd
│   ├── er_diagram.png
│   └── Untitled Diagram.drawio (1).png
│
├── sql/
│   ├── analytical_queries.sql
│   └── create_tables.sql
│
├── README.md
└── requirements.txt
```

## 6. Installation

Install Python and open the project directory in PowerShell or a terminal.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### Run the analysis notebook

From the project root, launch the notebook with:

```bash
jupyter notebook notebooks/bloom_filter_analysis.ipynb
```

In VS Code, you can instead open `notebooks/bloom_filter_analysis.ipynb`,
select a Python kernel, and run the cells from top to bottom.

### Run the web dashboard

From the project root, run:

```bash
python app.py
```

Open the local address printed by Flask. The dashboard includes a local URL
checker, data-backed filter statistics, false-positive/configuration analytics,
and lookup performance comparisons. It reads the existing CSV results and
SQLite file; entered URLs are only checked as text and are never opened or
requested. A positive Bloom Filter result means “possibly present,” not a
confirmed match.

## 7. How to Run the Project

Run these commands from the project root directory, in this order.

> **Warning:** These scripts can overwrite existing generated files.
> `clean_dataset.py` rewrites the training and testing CSVs;
> `create_database.py` deletes and rebuilds the `urls` table;
> `compare_configurations.py` overwrites `configuration_results.csv`;
> `benchmark_lookup.py` overwrites `benchmark_results.csv`; and the plotting
> scripts overwrite graph images in `results/`. Back up any files you need to
> preserve before running them.

### Step 1: Inspect the dataset

```bash
python src/inspect_dataset.py
```

### Step 2: Clean and split the dataset

```bash
python src/clean_dataset.py
```

This generates:
- `clean_urls.csv`
- `test_urls.csv`

### Step 3: Create the SQLite database

```bash
python src/create_database.py
```

This creates the database containing the 100,000 training URLs.

### Step 4: Build the Bloom Filter

```bash
python src/build_bloom_filter.py
```

This calculates the filter size, number of hash functions, and memory usage.

### Step 5: Test the false-positive rate

```bash
python src/test_false_positive.py
```

This compares theoretical and observed false-positive rates.

### Step 6: Compare configurations

```bash
python src/compare_configurations.py
```

This evaluates different target false-positive rates.

### Step 7: Generate configuration graphs

```bash
python src/plot_results.py
```

### Step 8: Benchmark lookup performance

```bash
python src/benchmark_lookup.py
```

This compares Bloom Filter, Python Set, and SQLite.

### Step 9: Generate benchmark graphs

```bash
python src/plot_benchmark.py
```

### Step 10: Perform probability analysis

```bash
python src/probability_analysis.py
```

## 8. Bloom Filter Implementation

The implementation uses:

- A bytearray as the bit array.
- SHA-256 for hashing.
- Double hashing to generate multiple bit positions.
- Seven hash functions for the 1% target configuration.

### Main formulas

**Optimal Bloom Filter size:**

\[
m = -\frac{n\ln(p)}{(\ln 2)^2}
\]

**Optimal number of hash functions:**

\[
k = \frac{m}{n}\ln 2
\]

**Theoretical false-positive probability:**

\[
P(FP) = \left(1-e^{-kn/m}\right)^k
\]

Where:

- \(m\) = number of bits
- \(n\) = number of inserted items
- \(k\) = number of hash functions
- \(p\) = target false-positive probability

## 9. Bloom Filter Results

For the 1% target configuration:

| Measurement | Result |
|---|---:|
| Training URLs | 100,000 |
| Filter size | 958,506 bits |
| Hash functions | 7 |
| Memory usage | 117.06 KB |
| Set bits | 496,981 |
| Theoretical false-positive rate | 1.0039% |
| Observed false-positive rate | 1.0496% |
| False positives | 785 |
| True negatives | 74,005 |

The observed false-positive rate is close to the theoretical result.

## 10. Configuration Comparison

| Target FP rate | Hash functions | Memory (KB) | Observed FP rate |
|---|---:|---:|---:|
| 10% | 3 | 58.56 | 10.1137% |
| 5% | 4 | 76.17 | 4.9766% |
| 1% | 7 | 117.06 | 1.0496% |
| 0.5% | 8 | 134.67 | 0.5054% |
| 0.1% | 10 | 175.56 | 0.0842% |

A lower target false-positive rate requires more memory and generally more hash functions.

## 11. Probability Analysis

For the 1% configuration:

| Measurement | Result |
|---|---:|
| Probability a bit is unset | 0.481763 |
| Probability a bit is set | 0.518237 |
| Optimal theoretical hash count | 6.6439 |
| Implemented hash count | 7 |

The implementation uses seven hash functions because the optimal calculated value is approximately 6.64.

The binomial model is also used to study how many of the seven selected bit positions are set. This provides an approximate probability explanation for false positives.

## 12. Lookup Performance Comparison

The benchmark tests 1,000 existing URLs and 1,000 absent URLs. Each benchmark is repeated five times.

### Updated benchmark results

| Method | Existing lookup (ms) | Absent lookup (ms) |
|---|---:|---:|
| Bloom Filter | 0.017449899998609908 | 0.007089400001859758 |
| Python Set | 0.0002648999980010558 | 0.0002893999990192242 |
| SQLite | 0.11177320000206237 | 0.1219414000006509 |

### Memory and storage comparison

| Method | Memory / Storage |
|---|---:|
| Bloom Filter | 117.06 KB |
| Python Set | 18,386.23 KB |
| SQLite | 22.31 MiB |

### Observations

- Python Set was faster than the Bloom Filter in both measured lookup tests.
- Bloom Filter used significantly less memory than Python Set.
- SQLite provided persistent storage and exact membership checks.
- Bloom Filter may report false positives, while Python Set and SQLite perform exact membership checks.

Memory figures represent different measurements: Bloom Filter bit-array memory, approximate Python Set memory including stored strings, and SQLite database file size.

## 13. Generated Graphs

The `results/` directory contains:

1. `memory_comparison.png` - Memory usage across Bloom Filter configurations.
2. `hash_comparison.png` - Number of hash functions across configurations.
3. `theoretical_vs_observed.png` - Comparison of theoretical and observed false-positive rates.
4. `existing_lookup_comparison.png` - Existing URL lookup performance.
5. `absent_lookup_comparison.png` - Absent URL lookup performance.

## 14. Conclusion

This project demonstrates how a Bloom Filter can efficiently check membership in a large collection of URLs while using very little memory.

The experiments show that Bloom Filters provide a useful balance between memory efficiency and lookup performance. Python Set was faster in the measured tests, while SQLite offered persistent storage and exact lookups.

The project also demonstrates the relationship between filter size, hash functions, memory consumption, and false-positive probability.

## 15. Limitations

- Bloom Filters can produce false positives.
- Standard Bloom Filters do not support direct deletion.
- Lookup timings depend on the computer and testing conditions.
- Benchmark measurements are based on a sample of 1,000 existing and 1,000 absent URLs.
- The Bloom Filter is a membership-checking component, not a complete malware detection system.
