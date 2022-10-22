
_block_offset = 0xA0

alphabet_other_count = 987
alphabet_syllable_count = 2350
alphabet_word_count = 4888
alphabet_count = 8225


def query_chr(zone_1, zone_2):
    """
    按照 KS-X-1001 分区规则查询字符串
    """
    return bytes([zone_1 + _block_offset, zone_2 + _block_offset]).decode('ksx1001')


def query_block(c):
    """
    查询字符所在区块平面
    """
    try:
        raw = c.encode('ksx1001')
    except UnicodeEncodeError:
        return None
    if len(raw) != 2:
        return None
    zone_1 = raw[0] - _block_offset
    if 1 <= zone_1 <= 12:
        return 'other'
    elif 16 <= zone_1 <= 40:
        return 'syllable'
    elif 42 <= zone_1 <= 93:
        return 'word'
    else:
        raise Exception(f'impossible zone_1: {zone_1}')


def _get_alphabet_by_range(zone_start, zone_end):
    alphabet = []
    for zone_1 in range(zone_start, zone_end + 1):
        for zone_2 in range(1, 94 + 1):
            try:
                alphabet.append(query_chr(zone_1, zone_2))
            except UnicodeDecodeError:
                pass
    return alphabet


def get_alphabet_other():
    alphabet = _get_alphabet_by_range(1, 12)
    assert len(alphabet) == alphabet_other_count
    return alphabet


def get_alphabet_syllable():
    alphabet = _get_alphabet_by_range(16, 40)
    assert len(alphabet) == alphabet_syllable_count
    return alphabet


def get_alphabet_word():
    alphabet = _get_alphabet_by_range(42, 93)
    assert len(alphabet) == alphabet_word_count
    return alphabet


def get_alphabet():
    """
    不包括 ASCII
    """
    alphabet = get_alphabet_other() + get_alphabet_syllable() + get_alphabet_word()
    assert len(alphabet) == alphabet_count
    return alphabet
