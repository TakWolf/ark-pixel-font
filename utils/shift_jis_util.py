import itertools

alphabet_single_ascii_count = 95 + 2
alphabet_single_other_count = 63
alphabet_double_basic_count = 524
alphabet_double_word_count = 6355
alphabet_count = alphabet_single_ascii_count + alphabet_single_other_count + alphabet_double_basic_count + alphabet_double_word_count


def query_block(c):
    """
    查询字符所在区块平面
    """
    try:
        raw = c.encode('shift-jis')
    except UnicodeEncodeError:
        return None
    if len(raw) == 1:
        code = raw[0]
        if 0x20 <= code <= 0x7E:
            return 'single-ascii'
        elif 0xA1 <= code <= 0xDF:
            return 'single-other'
        else:
            raise Exception(f'impossible code: {code}')
    else:
        code_1 = raw[0]
        code_2 = raw[1]
        if 0x81 <= code_1 <= 0x87 or (code_1 == 0x88 and code_2 <= 0x9E):
            return 'double-basic'
        elif (code_1 == 0x88 and code_2 >= 0x9F) or 0x89 <= code_1 <= 0x9F or 0xE0 <= code_1 <= 0xEF:
            return 'double-word'
        else:
            raise Exception(f'impossible codes: {code_1} - {code_2}')


def get_alphabet_single_ascii():
    """
    一个字节：ASCII 可打印字符，0x20-0x7E
    """
    alphabet = []
    for code in range(0x20, 0x7E + 1):
        try:
            c = bytes([code]).decode('shift-jis')
            alphabet.append(c)
        except UnicodeDecodeError:
            pass
    alphabet.append('¥') # 0xA5
    alphabet.append('‾') # 0x203E
    assert len(alphabet) == alphabet_single_ascii_count
    return alphabet


def get_alphabet_single_other():
    """
    一个字节：JIS X 0201标准内的半角标点及片假名，0xA1-0xDF
    """
    alphabet = []
    for code in range(0xA1, 0xDF + 1):
        try:
            c = bytes([code]).decode('shift-jis')
            alphabet.append(c)
        except UnicodeDecodeError:
            pass
    assert len(alphabet) == alphabet_single_other_count
    return alphabet


"""
两个字节：
JIS X 0208字集的所有字符
第一位字节使用 0x81-0x9F、0xE0-0xEF（共47个）
第二位字节使用 0x40-0x7E、0x80-0xFC（共188个）
"""


def get_alphabet_double_basic():
    """
    两个字节：
    第一位字节使用 0x81-0x87，第二位字节使用 0x40-0x7E、0x80-0xFC
    第一位字节使用 0x88，第二位字节使用 0x40-0x7E、0x80-0x9E
    """
    alphabet = []
    for code_1 in range(0x81, 0x88 + 1):
        for code_2 in range(0x40, 0x7E + 1):
            try:
                c = bytes([code_1, code_2]).decode('shift-jis')
                alphabet.append(c)
            except UnicodeDecodeError:
                pass
        for code_2 in range(0x80, (0x9E if code_1 == 0x88 else 0xFC) + 1):
            try:
                c = bytes([code_1, code_2]).decode('shift-jis')
                alphabet.append(c)
            except UnicodeDecodeError:
                pass
    assert len(alphabet) == alphabet_double_basic_count
    return alphabet


def get_alphabet_double_word():
    """
    两个字节：
    第一位字节使用 0x88，第二位字节使用 0x9F-0xFC
    第一位字节使用 0x89-0x9F、0xE0-0xEF，第二位字节使用 0x40-0x7E、0x80-0xFC
    """
    alphabet = []
    for code_1 in itertools.chain(range(0x88, 0x9F + 1), range(0xE0, 0xEF + 1)):
        if code_1 >= 0x89:
            for code_2 in range(0x40, 0x7E + 1):
                try:
                    c = bytes([code_1, code_2]).decode('shift-jis')
                    alphabet.append(c)
                except UnicodeDecodeError:
                    pass
        for code_2 in range(0x9F if code_1 == 0x88 else 0x80, 0xFC + 1):
            try:
                c = bytes([code_1, code_2]).decode('shift-jis')
                alphabet.append(c)
            except UnicodeDecodeError:
                pass
    assert len(alphabet) == alphabet_double_word_count
    return alphabet


def get_alphabet():
    alphabet = get_alphabet_single_ascii() + get_alphabet_single_other() + get_alphabet_double_basic() + get_alphabet_double_word()
    assert len(alphabet) == alphabet_count
    return alphabet
