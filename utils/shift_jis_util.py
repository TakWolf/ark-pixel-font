
def get_alphabet():
    alphabet = []
    # 一个字节：ASCII 可打印字符，0x20-0x7E
    for code in range(0x20, 0x7E + 1):
        try:
            c = bytes([code]).decode('shift-jis')
            alphabet.append(c)
        except UnicodeDecodeError:
            pass
    # 一个字节：JIS X 0201标准内的半角标点及片假名，0xA1-0xDF
    for code in range(0xA1, 0xDF + 1):
        try:
            c = bytes([code]).decode('shift-jis')
            alphabet.append(c)
        except UnicodeDecodeError:
            pass
    # 两个字节：
    # JIS X 0208字集的所有字符
    # 第一位字节使用 0x81-0x9F、0xE0-0xEF（共47个）
    # 第二位字节使用 0x40-0x7E、0x80-0xFC（共188个）
    for code_1 in list(range(0x81, 0x9F + 1)) + list(range(0xE0, 0xEF + 1)):
        for code_2 in list(range(0x40, 0x7E + 1)) + list(range(0x80, 0xFC + 1)):
            try:
                c = bytes([code_1, code_2]).decode('shift-jis')
                alphabet.append(c)
            except UnicodeDecodeError:
                pass
    # 返回
    return alphabet


def is_chr_include(c):
    try:
        c.encode('shift-jis')
        return True
    except UnicodeEncodeError:
        return False
