import csv
import math
import os
import re
import sys

from flask import Flask, jsonify, render_template, request

from src.bloom_filter import BloomFilter


PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
DATA_FOLDER = os.path.join(PROJECT_FOLDER, "data")
TRAINING_FILE = os.path.join(DATA_FOLDER, "clean_urls.csv")
TESTING_FILE = os.path.join(DATA_FOLDER, "test_urls.csv")
BENCHMARK_FILE = os.path.join(DATA_FOLDER, "benchmark_results.csv")
CONFIGURATION_FILE = os.path.join(DATA_FOLDER, "configuration_results.csv")
DATABASE_FILE = os.path.join(PROJECT_FOLDER, "database", "urlhaus.db")

TARGET_FALSE_POSITIVE_RATE = 0.01
MAX_URL_LENGTH = 4096


def normalize_url(url):
    url = url.replace("https://", "hxxps://").replace("http://", "hxxp://")
    return re.sub(r"(?<!\[)\.(?!\])", "[.]", url)


def load_urls(file_path, dataset_name):
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"{dataset_name} data file is missing.")

    urls = []
    with open(file_path, "r", encoding="utf-8-sig", newline="") as dataset_file:
        reader = csv.DictReader(dataset_file)
        if not reader.fieldnames or "url" not in reader.fieldnames:
            raise ValueError(f"{dataset_name} data must contain a 'url' column.")

        for row in reader:
            url = (row.get("url") or "").strip()
            if url:
                urls.append(url)

    if not urls:
        raise ValueError(f"{dataset_name} data contains no usable URLs.")
    return urls


def load_benchmark_results(file_path):
    expected_columns = (
        "Method",
        "Existing Lookup (ms)",
        "Absent Lookup (ms)",
    )
    results = []

    with open(file_path, "r", encoding="utf-8-sig", newline="") as results_file:
        reader = csv.DictReader(results_file)
        if not reader.fieldnames or not all(
            column in reader.fieldnames for column in expected_columns
        ):
            raise ValueError("Benchmark data has an unexpected format.")

        for row in reader:
            try:
                existing_ms = float(row["Existing Lookup (ms)"])
                absent_ms = float(row["Absent Lookup (ms)"])
            except (TypeError, ValueError) as error:
                raise ValueError("Benchmark times must be numeric.") from error

            if (
                not row["Method"]
                or not math.isfinite(existing_ms)
                or not math.isfinite(absent_ms)
                or existing_ms < 0
                or absent_ms < 0
            ):
                raise ValueError("Benchmark data contains invalid values.")

            results.append({
                "method": row["Method"],
                "existing_ms": existing_ms,
                "absent_ms": absent_ms,
            })

    if not results:
        raise ValueError("Benchmark data contains no results.")

    max_existing = max(result["existing_ms"] for result in results) or 1
    max_absent = max(result["absent_ms"] for result in results) or 1
    for result in results:
        result["existing_width"] = result["existing_ms"] / max_existing * 100
        result["absent_width"] = result["absent_ms"] / max_absent * 100
    return results


def load_configurations(file_path):
    expected_columns = (
        "target",
        "bits",
        "hashes",
        "memory",
        "false_positives",
        "theoretical",
        "observed",
    )
    configurations = []

    with open(file_path, "r", encoding="utf-8-sig", newline="") as results_file:
        reader = csv.DictReader(results_file)
        if not reader.fieldnames or not all(
            column in reader.fieldnames for column in expected_columns
        ):
            raise ValueError("Configuration data has an unexpected format.")

        for row in reader:
            try:
                result = {
                    "target": float(row["target"]),
                    "bits": int(row["bits"]),
                    "hashes": int(row["hashes"]),
                    "memory_kb": float(row["memory"]),
                    "false_positives": int(row["false_positives"]),
                    "theoretical": float(row["theoretical"]),
                    "observed": float(row["observed"]),
                }
            except (TypeError, ValueError) as error:
                raise ValueError("Configuration data contains invalid values.") from error

            if (
                not all(math.isfinite(result[key]) for key in ("target", "memory_kb", "theoretical", "observed"))
                or result["target"] <= 0
                or result["bits"] <= 0
                or result["hashes"] <= 0
                or result["memory_kb"] <= 0
                or result["false_positives"] < 0
            ):
                raise ValueError("Configuration data contains invalid values.")
            configurations.append(result)

    if not configurations:
        raise ValueError("Configuration data contains no results.")

    max_rate = max(
        max(row["theoretical"], row["observed"])
        for row in configurations
    ) or 1
    for row in configurations:
        row["theoretical_width"] = row["theoretical"] / max_rate * 100
        row["observed_width"] = row["observed"] / max_rate * 100
    return configurations


def build_memory_comparison(urls, bloom_filter):
    values = [{
        "label": "Bloom Filter",
        "value_kb": bloom_filter.get_memory_usage() / 1024,
        "note": "bit array memory",
        "kind": "bloom",
    }]

    python_set = set(urls)
    set_memory = sys.getsizeof(python_set) + sum(
        sys.getsizeof(url) for url in python_set
    )
    values.append({
        "label": "Python Set",
        "value_kb": set_memory / 1024,
        "note": "approximate in-memory size",
        "kind": "set",
    })

    if os.path.isfile(DATABASE_FILE):
        values.append({
            "label": "SQLite",
            "value_kb": os.path.getsize(DATABASE_FILE) / 1024,
            "note": "database file size on disk",
            "kind": "sqlite",
        })

    maximum = max(value["value_kb"] for value in values) or 1
    for value in values:
        value["width"] = value["value_kb"] / maximum * 100
    return values


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

    urls = []
    testing_count = None
    bloom_filter = None
    benchmark_results = []
    configurations = []
    data_issues = []

    try:
        urls = load_urls(TRAINING_FILE, "Training")
        bloom_filter = BloomFilter(
            expected_items=len(urls),
            false_positive_rate=TARGET_FALSE_POSITIVE_RATE,
        )
        for url in urls:
            bloom_filter.add(url)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        app.logger.warning("Training data unavailable (%s).", type(error).__name__)
        data_issues.append(
            "Training data is unavailable. Restore data/clean_urls.csv to enable URL checks."
        )

    try:
        testing_count = len(load_urls(TESTING_FILE, "Testing"))
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        app.logger.warning("Testing data unavailable (%s).", type(error).__name__)
        data_issues.append(
            "Testing URL count is unavailable because data/test_urls.csv could not be read."
        )

    try:
        benchmark_results = load_benchmark_results(BENCHMARK_FILE)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        app.logger.warning("Benchmark data unavailable (%s).", type(error).__name__)
        data_issues.append(
            "Performance charts are unavailable because benchmark results could not be read."
        )

    try:
        configurations = load_configurations(CONFIGURATION_FILE)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        app.logger.warning("Configuration data unavailable (%s).", type(error).__name__)
        data_issues.append(
            "Configuration analytics are unavailable because configuration results could not be read."
        )

    memory_comparison = (
        build_memory_comparison(urls, bloom_filter)
        if bloom_filter is not None
        else []
    )
    target_configuration = next(
        (
            row for row in configurations
            if math.isclose(row["target"], TARGET_FALSE_POSITIVE_RATE * 100)
        ),
        None,
    )
    theoretical_rate = (
        target_configuration["theoretical"]
        if target_configuration is not None
        else (
            bloom_filter.get_theoretical_false_positive_rate() * 100
            if bloom_filter is not None
            else None
        )
    )

    best_existing = (
        min(benchmark_results, key=lambda row: row["existing_ms"])["method"]
        if benchmark_results else None
    )
    best_absent = (
        min(benchmark_results, key=lambda row: row["absent_ms"])["method"]
        if benchmark_results else None
    )

    stats = {
        "training_count": len(urls) if bloom_filter is not None else None,
        "testing_count": testing_count,
        "target_false_positive_rate": TARGET_FALSE_POSITIVE_RATE * 100,
        "hash_count": bloom_filter.hash_count if bloom_filter is not None else None,
        "filter_size": bloom_filter.size if bloom_filter is not None else None,
        "memory_kb": (
            bloom_filter.get_memory_usage() / 1024
            if bloom_filter is not None else None
        ),
        "theoretical_rate": theoretical_rate,
        "observed_rate": (
            target_configuration["observed"]
            if target_configuration is not None else None
        ),
    }

    def render_dashboard(feedback=None, entered_url=""):
        return render_template(
            "index.html",
            stats=stats,
            benchmark_results=benchmark_results,
            configurations=configurations,
            memory_comparison=memory_comparison,
            data_issues=data_issues,
            best_existing=best_existing,
            best_absent=best_absent,
            lookup_available=bloom_filter is not None,
            feedback=feedback,
            entered_url=entered_url,
        )

    @app.get("/")
    def index():
        return render_dashboard()

    @app.post("/check")
    def check_url():
        url = request.form.get("url", "").strip()
        feedback = None
        status = 200

        if not bloom_filter:
            feedback = {
                "kind": "error",
                "message": "URL lookup is unavailable because training data is not loaded.",
                "detail": "Restore the training dataset and restart the dashboard.",
            }
            status = 503
        elif not url:
            feedback = {
                "kind": "error",
                "message": "Enter a URL to check.",
                "detail": "The input cannot be empty or contain only whitespace.",
            }
            status = 400
        elif len(url) > MAX_URL_LENGTH:
            feedback = {
                "kind": "error",
                "message": f"Input must be {MAX_URL_LENGTH} characters or fewer.",
                "detail": "Shorten the URL text and try again.",
            }
            status = 400
        elif bloom_filter.contains(normalize_url(url)):
            feedback = {
                "kind": "warning",
                "message": "Possibly present in the training dataset.",
                "detail": (
                    "A positive result does not confirm that the URL is malicious "
                    "or definitely present. Bloom Filters can produce false positives."
                ),
            }
        else:
            feedback = {
                "kind": "success",
                "message": "Definitely not present in the training dataset.",
                "detail": (
                    "A negative result means this normalized URL text is not present "
                    "in the inserted training dataset."
                ),
            }

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(feedback), status
        return render_dashboard(feedback=feedback, entered_url=url), status

    @app.errorhandler(413)
    def request_too_large(_error):
        feedback = {
            "kind": "error",
            "message": "The submitted request is too large.",
            "detail": f"URL text must be {MAX_URL_LENGTH} characters or fewer.",
        }
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify(feedback), 413
        return render_dashboard(feedback=feedback), 413

    return app


app = create_app()


if __name__ == "__main__":
    app.run()
