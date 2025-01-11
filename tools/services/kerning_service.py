import unicodedata

import unidata_blocks
from pixel_font_knife.glyph_file_util import GlyphFlavorGroup
from unidata_blocks import UnicodeBlock

_common_marks = {ord(c) for c in '"\',.'}


def _get_alphabet(blocks: list[UnicodeBlock]) -> set[int]:
    alphabet = set(_common_marks)
    for block in blocks:
        for code_point in range(block.code_start, block.code_end + 1):
            if unicodedata.category(chr(code_point)) in ('Lu', 'Ll'):
                alphabet.add(code_point)
    return alphabet


_alphabets = [
    _get_alphabet([
        unidata_blocks.get_block_by_name('Basic Latin'),
        unidata_blocks.get_block_by_name('Latin-1 Supplement'),
        unidata_blocks.get_block_by_name('Latin Extended-A'),
        unidata_blocks.get_block_by_name('Latin Extended-B'),
        unidata_blocks.get_block_by_name('Latin Extended-C'),
        unidata_blocks.get_block_by_name('Latin Extended-D'),
        unidata_blocks.get_block_by_name('Latin Extended-E'),
        unidata_blocks.get_block_by_name('Latin Extended-F'),
        unidata_blocks.get_block_by_name('Latin Extended-G'),
        unidata_blocks.get_block_by_name('Latin Extended Additional'),
    ]),
    _get_alphabet([
        unidata_blocks.get_block_by_name('Greek and Coptic'),
        unidata_blocks.get_block_by_name('Greek Extended'),
        unidata_blocks.get_block_by_name('Coptic'),
    ]),
    _get_alphabet([
        unidata_blocks.get_block_by_name('Cyrillic'),
        unidata_blocks.get_block_by_name('Cyrillic Supplement'),
        unidata_blocks.get_block_by_name('Cyrillic Extended-A'),
        unidata_blocks.get_block_by_name('Cyrillic Extended-B'),
        unidata_blocks.get_block_by_name('Cyrillic Extended-C'),
        unidata_blocks.get_block_by_name('Cyrillic Extended-D'),
    ]),
]


def calculate_kerning_pairs(context: dict[int, GlyphFlavorGroup]) -> dict[tuple[str, str], int]:
    kerning_pairs = {}
    for alphabet in _alphabets:
        for left_code_point in alphabet:
            if left_code_point not in context:
                continue
            left_glyph_file = context[left_code_point][None]

            if all(mask_row[-1] == 0 for mask_row in left_glyph_file.mask):
                continue
            mask = left_glyph_file.mask

            for right_code_point in alphabet:
                if right_code_point not in context:
                    continue
                right_glyph_file = context[right_code_point][None]

                bitmap = right_glyph_file.bitmap
                if right_glyph_file.code_point in _common_marks:
                    padding = bitmap.calculate_left_padding()
                    bitmap = bitmap.resize(left=-padding, right=padding)

                offset = 0
                while True:
                    if mask != mask.plus(bitmap, x=left_glyph_file.width + offset - 1):
                        break
                    offset -= 1
                    if offset <= -(right_glyph_file.width - 1):
                        break
                if offset < 0:
                    kerning_pairs[(left_glyph_file.glyph_name, right_glyph_file.glyph_name)] = offset
    return kerning_pairs
