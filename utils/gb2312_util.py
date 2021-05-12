
def query_chr(zone_1, zone_2):
    """
    按照 GB2312 区域规则查询字符串
    """
    offset = 0xA0
    return bytes.fromhex(f'{zone_1 + offset:02x}{zone_2 + offset:02x}').decode("gb2312")


def _get_alphabet_by_range(zone_start, zone_end):
    alphabet = []
    for zone_1 in range(zone_start, zone_end):
        for zone_2 in range(1, 95):
            try:
                alphabet.append(query_chr(zone_1, zone_2))
            except UnicodeDecodeError:
                pass
    return alphabet


def get_alphabet_other():
    alphabet = _get_alphabet_by_range(1, 10)
    assert len(alphabet) == 682
    return alphabet


def get_alphabet_level_1():
    alphabet = _get_alphabet_by_range(16, 56)
    assert len(alphabet) == 3755
    return alphabet


def get_alphabet_level_2():
    alphabet = _get_alphabet_by_range(56, 88)
    assert len(alphabet) == 3008
    return alphabet


def get_alphabet():
    alphabet = get_alphabet_other() + get_alphabet_level_1() + get_alphabet_level_2()
    assert len(alphabet) == 682 + 6763
    return alphabet
