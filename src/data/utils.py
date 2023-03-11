import itertools


def generate_binary_strings(bit_count: int) -> list[str]:
    return ["".join(num_bin) for num_bin in itertools.product("01", repeat=bit_count)]


def is_chemical_result(column_name: str) -> bool:
    """
    Check if column name is a chemical result one
    :param column_name: column_name to check
    :return: Whether the column contains chemical results or not
    """
    return (
        "% ACTIVATION" in column_name or "% INHIBITION" in column_name
    ) and "(" not in column_name
