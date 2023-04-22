import time


def dec_to_base(number: int, base: int, digits: int = 4) -> str:
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"

    if number == 0:
        return "0" * digits

    digits_ = []
    while number or len(digits_) < digits:
        digits_.append(chars[int(number % base)])
        number //= base

    if base < 37:
        return "".join(digits_[::-1]).lower()

    return "".join(digits_[::-1])


def get_version():
    timestamp = time.time()

    return "-".join(
        [
            dec_to_base(int(timestamp), 36),
            dec_to_base(int(1000 * (timestamp - int(timestamp))), 36, 2),
        ]
    )
