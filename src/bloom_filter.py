
import math
import hashlib
import sys
from numbers import Integral, Real


class BloomFilter:

    def __init__(self, expected_items, false_positive_rate=0.01):

        if (
            isinstance(expected_items, bool)
            or not isinstance(expected_items, Integral)
            or expected_items <= 0
        ):
            raise ValueError("expected_items must be a positive integer.")

        if (
            isinstance(false_positive_rate, bool)
            or not isinstance(false_positive_rate, Real)
            or not 0 < false_positive_rate < 1
            or not math.isfinite(false_positive_rate)
        ):
            raise ValueError(
                "false_positive_rate must be a finite number strictly between 0 and 1."
            )

        # Store configuration
        self.expected_items = expected_items
        self.false_positive_rate = false_positive_rate

        # Calculate optimal bit array size
        self.size = math.ceil(
            -(expected_items * math.log(false_positive_rate))
            / (math.log(2) ** 2)
        )

        # Calculate optimal number of hash functions
        self.hash_count = round(
            (self.size / expected_items) * math.log(2)
        )

        # Create bit array
        self.bit_array = bytearray(
            (self.size + 7) // 8
        )

        # Count inserted items
        self.item_count = 0

    # ======================================
    # GENERATE HASH POSITIONS
    # ======================================

    def get_hash_positions(self, item):

        # Convert URL into bytes
        item_bytes = item.encode("utf-8")

        # Generate SHA-256 digest
        digest = hashlib.sha256(item_bytes).digest()

        # Extract two independent hash values
        hash1 = int.from_bytes(digest[:16], "big")
        hash2 = int.from_bytes(digest[16:], "big")

        # Ensure the second hash is non-zero
        hash2 = hash2 | 1

        # Generate positions using double hashing
        for i in range(self.hash_count):

            position = (
                hash1 + i * hash2
            ) % self.size

            yield position

    # ======================================
    # SET A BIT
    # ======================================

    def set_bit(self, position):

        byte_index = position // 8
        bit_index = position % 8

        self.bit_array[byte_index] |= (
            1 << bit_index
        )

    # ======================================
    # CHECK A BIT
    # ======================================

    def get_bit(self, position):

        byte_index = position // 8
        bit_index = position % 8

        return (
            self.bit_array[byte_index]
            & (1 << bit_index)
        ) != 0

    # ======================================
    # INSERT AN ITEM
    # ======================================

    def add(self, item):

        for position in self.get_hash_positions(item):
            self.set_bit(position)

        self.item_count += 1

    # ======================================
    # CHECK MEMBERSHIP
    # ======================================

    def contains(self, item):

        for position in self.get_hash_positions(item):

            if not self.get_bit(position):
                return False

        return True

    # ======================================
    # CALCULATE BIT ARRAY STATISTICS
    # ======================================

    def get_set_bits(self):

        return sum(
            bin(byte).count("1")
            for byte in self.bit_array
        )

    def get_memory_usage(self):

        return sys.getsizeof(self.bit_array)

    def get_theoretical_false_positive_rate(self):

        probability = (
            1 - math.exp(
                -(self.hash_count * self.item_count)
                / self.size
            )
        )

        return probability ** self.hash_count

