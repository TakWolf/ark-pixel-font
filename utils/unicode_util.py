import re


class UnicodeBlock:
    def __init__(self, name, begin, end):
        self.name = name
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
                unicode_blocks.append(UnicodeBlock(name, begin, end))
    return unicode_blocks


def load_block_name_translations(file_path):
    unicode_block_name_translations = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file.readlines():
            line = line.split('#', 1)[0].strip()
            if line != '':
                arr = line.split('; ')
                unicode_block_name_translations[arr[0]] = arr[1]
    return unicode_block_name_translations
