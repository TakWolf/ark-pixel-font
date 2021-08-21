import re

blocks_doc_url = 'https://www.unicode.org/Public/UNIDATA/Blocks.txt'


class UnicodeBlock:
    def __init__(self, name, name_cn, begin, end):
        self.name = name
        self.name_cn = name_cn
        self.begin = begin
        self.end = end
        self.capacity = end - begin + 1
        self.char_count = 0
        for code_point in range(begin, end + 1):
            c = chr(code_point)
            if c.isprintable():
                self.char_count += 1


def load_blocks_db(db_path):
    unicode_blocks = []
    with open(db_path, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            line = line.split('#', 1)[0].strip()
            if line != '':
                arr = re.split(r'\.\.|;\s', line)
                begin = int(arr[0], 16)
                end = int(arr[1], 16)
                name = arr[2]
                if len(arr) >= 4:
                    name_cn = arr[3]
                else:
                    name_cn = None
                unicode_blocks.append(UnicodeBlock(name, name_cn, begin, end))
    return unicode_blocks


def index_block_by_code_point(unicode_blocks, code_point):
    for i, unicode_block in enumerate(unicode_blocks):
        if unicode_block.begin <= code_point <= unicode_block.end:
            return i, unicode_block
    return -1, None
