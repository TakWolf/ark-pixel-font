
_block_offset = 0xA0

alphabet_other_count = 682
alphabet_level_1_count = 3755
alphabet_level_2_count = 3008
alphabet_count = 682 + 6763


def query_chr(zone_1, zone_2):
    """
    按照 GB2312 分区规则查询字符串
    """
    return bytes([zone_1 + _block_offset, zone_2 + _block_offset]).decode('gb2312')


def query_block(c):
    """
    查询字符所在区块平面
    """
    try:
        raw = c.encode('gb2312')
    except UnicodeEncodeError:
        return None
    if len(raw) == 1:
        return None  # ascii
    else:
        zone_1 = raw[0] - _block_offset
        if 1 <= zone_1 <= 9:
            return 'other'
        elif 16 <= zone_1 <= 55:
            return 'level-1'
        elif 56 <= zone_1 <= 87:
            return 'level-2'
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
    alphabet = _get_alphabet_by_range(1, 9)
    assert len(alphabet) == alphabet_other_count
    return alphabet


def get_alphabet_level_1():
    alphabet = _get_alphabet_by_range(16, 55)
    assert len(alphabet) == alphabet_level_1_count
    return alphabet


def get_alphabet_level_2():
    alphabet = _get_alphabet_by_range(56, 87)
    assert len(alphabet) == alphabet_level_2_count
    return alphabet


def get_alphabet():
    """
    不包括 ASCII
    """
    alphabet = get_alphabet_other() + get_alphabet_level_1() + get_alphabet_level_2()
    assert len(alphabet) == alphabet_count
    return alphabet
