characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
min_length = 4
max_length = 12


def id_to_key(n):
    """short id 로 short key 조회"""
    if n <= 0:
        raise ValueError("short_id는 1보다 작은 수 없습니다.")
    if n > 3279156381453602854576:
        # 최대 경우의 수 : sum([len(characters) ** length for length in range(min_length, max_length + 1)])
        raise ValueError("최대 경우의 수를 초과하였습니다")
    total = 0
    length = min_length
    for length in range(min_length, max_length + 1):
        combinations = len(characters) ** length
        if total + combinations >= n:
            break
        total += combinations
    n -= total + 1
    result = ""
    while length > 0:
        result = characters[n % len(characters)] + result
        n //= len(characters)
        length -= 1
    return result


def key_to_id(s):
    """short key 로 short id 조회"""
    if not (min_length <= len(s) <= max_length):
        raise ValueError("문자열의 길이가 올바르지 않습니다.")
    index = 0
    length = len(s)
    for i, char in enumerate(s):
        char_index = characters.index(char)
        index += char_index * (len(characters) ** (length - i - 1))
    total = 0
    for i in range(min_length, length):
        total += len(characters) ** i
    return total + index + 1
