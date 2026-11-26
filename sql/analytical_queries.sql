-- 1. Count all URL records stored in the database.
SELECT COUNT(*) AS total_urls
FROM urls;

-- 2. Count URLs by their stored scheme prefix.
-- The "other" category includes strings without one of the four listed prefixes.
WITH classified AS (
    SELECT
        CASE
            WHEN url LIKE 'hxxp://%' THEN 'hxxp'
            WHEN url LIKE 'hxxps://%' THEN 'hxxps'
            WHEN url LIKE 'http://%' THEN 'http'
            WHEN url LIKE 'https://%' THEN 'https'
            ELSE 'other'
        END AS scheme
    FROM urls
),
scheme_counts AS (
    SELECT scheme, COUNT(*) AS url_count
    FROM classified
    GROUP BY scheme
),
schemes AS (
    SELECT 1 AS sort_order, 'hxxp' AS scheme
    UNION ALL SELECT 2, 'hxxps'
    UNION ALL SELECT 3, 'http'
    UNION ALL SELECT 4, 'https'
    UNION ALL SELECT 5, 'other'
)
SELECT schemes.scheme, COALESCE(scheme_counts.url_count, 0) AS url_count
FROM schemes
LEFT JOIN scheme_counts ON scheme_counts.scheme = schemes.scheme
ORDER BY schemes.sort_order;

-- 3. Summarize stored URL string lengths in characters.
SELECT
    MIN(LENGTH(url)) AS minimum_length,
    MAX(LENGTH(url)) AS maximum_length,
    ROUND(AVG(LENGTH(url)), 2) AS average_length
FROM urls;

-- 4. Count URLs in fixed character-length ranges; empty ranges remain visible.
WITH url_lengths AS (
    SELECT LENGTH(url) AS url_length
    FROM urls
),
bucket_counts AS (
    SELECT
        CASE
            WHEN url_length < 50 THEN 1
            WHEN url_length < 100 THEN 2
            WHEN url_length < 150 THEN 3
            WHEN url_length < 200 THEN 4
            ELSE 5
        END AS bucket_order,
        COUNT(*) AS url_count
    FROM url_lengths
    GROUP BY bucket_order
),
length_ranges AS (
    SELECT 1 AS bucket_order, '0-49' AS length_range
    UNION ALL SELECT 2, '50-99'
    UNION ALL SELECT 3, '100-149'
    UNION ALL SELECT 4, '150-199'
    UNION ALL SELECT 5, '200+'
)
SELECT
    length_ranges.length_range,
    COALESCE(bucket_counts.url_count, 0) AS url_count
FROM length_ranges
LEFT JOIN bucket_counts ON bucket_counts.bucket_order = length_ranges.bucket_order
ORDER BY length_ranges.bucket_order;

-- 5. Find the ten most frequent hosts.
-- The authority is isolated after the scheme and before a path/query/fragment.
-- A port is excluded; bracketed IPv6 literals remain intact. URLs without a path work too.
WITH without_scheme AS (
    SELECT
        CASE
            WHEN INSTR(url, '://') > 0
                THEN SUBSTR(url, INSTR(url, '://') + 3)
            ELSE url
        END AS authority
    FROM urls
),
authorities AS (
    SELECT
        CASE
            WHEN INSTR(authority, '/') > 0
                THEN SUBSTR(authority, 1, INSTR(authority, '/') - 1)
            WHEN INSTR(authority, '?') > 0
                THEN SUBSTR(authority, 1, INSTR(authority, '?') - 1)
            WHEN INSTR(authority, '#') > 0
                THEN SUBSTR(authority, 1, INSTR(authority, '#') - 1)
            ELSE authority
        END AS authority
    FROM without_scheme
),
hosts AS (
    SELECT
        LOWER(
            CASE
                WHEN SUBSTR(authority, 1, 1) = '[' AND INSTR(authority, ']') > 0
                    THEN SUBSTR(authority, 1, INSTR(authority, ']'))
                WHEN INSTR(authority, ':') > 0
                    THEN SUBSTR(authority, 1, INSTR(authority, ':') - 1)
                ELSE authority
            END
        ) AS host
    FROM authorities
)
SELECT host, COUNT(*) AS url_count
FROM hosts
WHERE host <> ''
GROUP BY host
ORDER BY url_count DESC, host
LIMIT 10;
