# Data Quality Log

**Project:** Bloom Filter for Malicious URL Detection  
**Source file:** `data/urlhaus.csv`  
**Cleaning procedure:** `src/clean_dataset.py`  
**Validation approach:** Read-only checks; URLs were treated as text and were not opened, visited, or requested.

## Dataset Source and Description

The project dataset is the URLhaus CSV feed, containing URL records and associated metadata. The original file has nine columns: `id`, `dateadded`, `url`, `url_status`, `last_online`, `threat`, `tags`, `urlhaus_link`, and `reporter`.

The generated training and testing files retain only the URL string. The SQLite database likewise stores the training URL strings in its `urls` table.

## Original Dataset Characteristics

The values below were previously reported as the output of the cleaning run. They were also independently rechecked against the current files without rerunning the dataset-writing script.

| Check | Result |
|---|---:|
| Original records | 174,790 |
| Normalized original CSV columns | 9 |
| Nonblank URL values | 174,790 |
| Unique trimmed URL strings | 174,790 |

The source header was found using the same marker as the cleaning script and normalized by stripping whitespace and the leading `#` from the first column name.

## Missing-Value Analysis

Missing values below were counted as pandas parses the source CSV using the cleaning script's `read_csv` approach.

| Original column | Missing values |
|---|---:|
| `id` | 0 |
| `dateadded` | 0 |
| `url` | 0 |
| `url_status` | 0 |
| `last_online` | 5,443 |
| `threat` | 0 |
| `tags` | 8,086 |
| `urlhaus_link` | 0 |
| `reporter` | 0 |

No URL value was null or blank after trimming. The generated `clean_urls.csv` and `test_urls.csv` each have a single `url` column, with no empty URL values.

## Duplicate Analysis

| Check | Result |
|---|---:|
| Duplicate nonblank URL occurrences in original | 0 |
| Duplicate complete rows in original | 0 |
| Duplicate URLs in training file | 0 |
| Duplicate URLs in testing file | 0 |
| Training/testing overlap | 0 |

The original URL duplicate check was performed after trimming, matching the cleaning script's treatment of URL strings.

## Invalid-Record Analysis

A non-network structural check parsed each original URL and each generated URL after reversing the defanging replacements in memory. A URL was considered structurally valid if it had an `http`, `https`, or `ftp` scheme, a nonempty hostname, and a parseable port when present.

| Check | Result |
|---|---:|
| Original nonblank URLs failing the structural check | 0 |
| Generated URLs failing the structural check after in-memory refanging | 0 |

The original scheme counts were 46,098 `http`, 128,675 `https`, and 17 `ftp`. The 17 FTP records are valid under this check; they are not treated as invalid merely because the cleaning script only rewrites HTTP and HTTPS schemes.

This is a syntax/structure check only. It does not determine whether a URL is reachable, safe, or currently active.

## URL Defanging and Normalization

The cleaning script performs these operations, in order:

1. Locates the CSV header, reads the source, and strips whitespace and the leading `#` from column names.
2. Selects `url`, drops null values, converts remaining values to strings, and strips surrounding whitespace.
3. Removes blank URL strings and exact duplicate URL strings.
4. Shuffles the unique values with `sample(frac=1, random_state=42)`.
5. Replaces `https://` with `hxxps://` and `http://` with `hxxp://`.
6. Replaces ordinary dots with `[.]` using `(?<!\[)\.(?!\])`, leaving existing `[.]` markers unchanged.
7. Saves each output with a single `url` column.

The generated files contain 46,098 `hxxp` URLs, 128,675 `hxxps` URLs, and 17 URLs retaining the `ftp` scheme. No generated URL starts with plain `http://` or `https://`; no generated value contains an unbracketed dot or a nested `[[.]]` marker.

The shuffle, split, and defanging steps were reproduced in memory using the same pandas procedure and random seed. Both generated files matched that reproduction exactly, row for row. The cleaning script itself was not run, and no dataset file was rewritten.

## Training/Testing Split

| Output | Records |
|---|---:|
| `data/clean_urls.csv` (training) | 100,000 |
| `data/test_urls.csv` (testing) | 74,790 |
| Combined | 174,790 |

The first 100,000 entries after the deterministic shuffle form the training set; the remaining entries form the testing set. The current files have the expected `url` headers, are internally unique, have no overlap, and contain 174,790 distinct URLs in total.

## Database Consistency

The existing `database/urlhaus.db` was opened in read-only mode. Its `urls` table contains 100,000 records. Comparing URLs ordered by database `id` with `clean_urls.csv` showed:

| Check | Result |
|---|---:|
| Database URLs equal training URLs as sets | Yes |
| Database URLs equal training URLs in the same order | Yes |
| Database-only URLs | 0 |
| Training-only URLs | 0 |

## Final Data-Quality Summary

The previously reported record and split counts match the current files. All URL values are present, unique, structurally valid under the stated non-network check, and correctly divided between training and testing with no overlap. Generated strings match the cleaning script's deterministic in-memory reproduction, and the database matches the training file exactly.

### Limitations

- `last_online` and `tags` contain missing metadata values; the URL column has none.
- Structural URL parsing does not verify reachability, current status, threat classification, or safety.
- The database stores only the cleaned URL strings; it does not retain the original metadata columns.
- The 17 FTP URLs are preserved because the cleaning script changes only HTTP and HTTPS schemes.
