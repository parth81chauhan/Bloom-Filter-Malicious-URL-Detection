
import math
from bloom_filter import BloomFilter


# ==========================================
# 1. CONFIGURATION
# ==========================================

n = 100000
target_rate = 0.01

bloom = BloomFilter(
    expected_items=n,
    false_positive_rate=target_rate
)

m = bloom.size
k = bloom.hash_count


# ==========================================
# 2. BIT PROBABILITY
# ==========================================

probability_unset = (
    1 - (1 / m)
) ** (k * n)

probability_set = 1 - probability_unset


# ==========================================
# 3. FALSE POSITIVE PROBABILITY
# ==========================================

false_positive_probability = (
    probability_set ** k
)


# ==========================================
# 4. OPTIMAL HASH FUNCTIONS
# ==========================================

optimal_k = (
    (m / n) * math.log(2)
)


# ==========================================
# 5. BINOMIAL PROBABILITY
# ==========================================

# Probability that exactly j of k selected
# bit positions are set.

print("=" * 60)
print("             BLOOM FILTER PROBABILITY ANALYSIS")
print("=" * 60)

print("\nCONFIGURATION")
print("-" * 40)

print("Number of inserted items (n):", n)
print("Bit array size (m):", m)
print("Number of hash functions (k):", k)

print("\nBIT PROBABILITIES")
print("-" * 40)

print(f"Probability bit remains unset: {probability_unset:.6f}")
print(f"Probability bit becomes set:   {probability_set:.6f}")

print("\nFALSE POSITIVE PROBABILITY")
print("-" * 40)

print(
    f"Theoretical probability: "
    f"{false_positive_probability * 100:.4f}%"
)

print("\nOPTIMAL HASH FUNCTIONS")
print("-" * 40)

print(f"Calculated optimal k: {optimal_k:.4f}")
print(f"Implemented hash count: {k}")

print("\nBINOMIAL PROBABILITY REASONING")
print("-" * 40)

print(
    "Let X be the number of set bits among "
    "the k selected positions."
)

print("X follows an approximate Binomial(k, p) model,")
print("where p is the probability that a bit is set.")

for j in range(k + 1):

    probability = (
        math.comb(k, j)
        * (probability_set ** j)
        * (probability_unset ** (k - j))
    )

    print(
        f"P(X = {j}) = {probability:.8f}"
    )


print("\nFalse positive occurs when X = k.")

print("\n" + "=" * 60)
print("             ANALYSIS COMPLETED")
print("=" * 60)
