import itertools

def generate_binary_strings(bit_count: int) -> list[str]:
    return ["".join(num_bin) for num_bin in itertools.product("01", repeat=bit_count)]