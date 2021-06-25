from timeit import timeit

base = timeit("for a in range(100000): pass", number=100)
print(f'time base {base}')

t = timeit("for a in range(100000): a * 8", number=100)
print(f'time mul_norm {t - base}')

t = timeit("for a in range(100000): a * 100", number=100)
print(f'time mul_norm(2) {t - base}')

t = timeit("for a in range(100000): a << 3", number=100)
print(f'time mul_bit {t - base}')

t = timeit("for a in range(100000): a // 4", number=100)
print(f'time div_norm {t - base}')

t = timeit("for a in range(100000): a >> 2", number=100)
print(f'time div_bit {t - base}')

t = timeit("for a in range(100000): a & 0x6", number=100)
print(f'time and_bit {t - base}')

t = timeit("for a in range(100000): a | 0x6", number=100)
print(f'time or_bit {t - base}')

t = timeit("for a in range(100000): ~a", number=100)
print(f'time not_bit {t - base}')

