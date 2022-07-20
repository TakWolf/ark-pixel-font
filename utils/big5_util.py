
alphabet_other_count = 408
alphabet_level_1_count = 5401
alphabet_level_2_count = 7652
alphabet_count = alphabet_other_count + alphabet_level_1_count + alphabet_level_2_count


def query_block(c):
    """
    查询字符所在区块平面
    """
    try:
        raw = c.encode('big5')
    except UnicodeEncodeError:
        return None
    if len(raw) != 2:
        return None
    code = int(f'{raw[0]:02x}{raw[1]:02x}', 16)
    if 0xA140 <= code <= 0xA3BF:
        return 'other'
    elif 0xA440 <= code <= 0xC67E:
        return 'level-1'
    elif 0xC940 <= code <= 0xF9D5:
        return 'level-2'
    else:
        return None  # ext


def get_alphabet_other():
    """
    0xA140 ~ 0xA3BF
    标点符号、希腊字母、特殊符号，
    包括在 0xA259 ~ 0xA261 安放了九个计量用汉字：兙兛兞兝兡兣嗧瓩糎。
    """
    alphabet = []
    for code in range(0xA140, 0xA3BF + 1):
        try:
            c = bytes.fromhex(f'{code:X}').decode('big5')
            alphabet.append(c)
        except UnicodeDecodeError:
            pass
    assert len(alphabet) == alphabet_other_count
    return alphabet


def get_alphabet_level_1():
    """
    0xA440 ~ 0xC67E
    常用汉字（5401字），字集来源除教育部“常用国字标准字体表”所列4808字外，并优先收编国中、国小教科书中常用字587字及异体字6字。
    先按笔画再按部首排序。
    """
    alphabet = []
    for code in range(0xA440, 0xC67E + 1):
        try:
            c = bytes.fromhex(f'{code:X}').decode('big5')
            alphabet.append(c)
        except UnicodeDecodeError:
            pass
    assert len(alphabet) == alphabet_level_1_count
    return alphabet


def get_alphabet_level_2():
    """
    0xC940 ~ 0xF9D5
    次常用汉字（7652字），字集来源除教育部“次常用国字标准字体表”所列6330字外，并筛选编入教育部“罕用国字标准字体表”表中使用频率较高之1320字。
    先按笔画再按部首排序。
    """
    alphabet = []
    for code in range(0xC940, 0xF9D5 + 1):
        try:
            c = bytes.fromhex(f'{code:X}').decode('big5')
            alphabet.append(c)
        except UnicodeDecodeError:
            pass
    assert len(alphabet) == alphabet_level_2_count
    return alphabet


def get_alphabet():
    """
    不包括 ASCII
    """
    alphabet = get_alphabet_other() + get_alphabet_level_1() + get_alphabet_level_2()
    assert len(alphabet) == alphabet_count
    return alphabet
