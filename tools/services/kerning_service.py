from io import StringIO

from pixel_font_builder.opentype import FeatureFile
from pixel_font_knife.glyph_file_util import GlyphFlavorGroup
from pixel_font_knife.mono_bitmap import MonoBitmap

from tools.configs import path_define, FontSize


def _get_latin_alphabet() -> set[int]:
    alphabet = set()

    # 0000-007F Basic Latin
    for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"\',-.:;':
        alphabet.add(ord(c))

    # 0080-00FF Latin-1 Supplement
    for code_point in range(0x00C0, 0x00D6 + 1):
        alphabet.add(code_point)
    for code_point in range(0x00D8, 0x00F6 + 1):
        alphabet.add(code_point)
    for code_point in range(0x00F8, 0x00FF + 1):
        alphabet.add(code_point)

    # TODO

    # 1E00-1EFF Latin Extended Additional
    for code_point in range(0x1E00, 0x1EFF + 1):
        alphabet.add(code_point)

    return alphabet


def _get_greek_and_coptic_alphabet() -> set[str]:
    alphabet = set()

    # TODO

    return alphabet


def _get_cyrillic_alphabet() -> set[str]:
    alphabet = set()

    # TODO

    return alphabet


_alphabets = [
    _get_latin_alphabet(),
    _get_greek_and_coptic_alphabet(),
    _get_cyrillic_alphabet(),
]


def _calculate_kerning(alphabet: set[int], context: dict[int, GlyphFlavorGroup]) -> dict[tuple[str, str], int]:
    pairs = {}
    for left_code_point in alphabet:
        if left_code_point not in context:
            continue
        left_glyph_file = context[left_code_point][None]
        if '1' not in str(left_glyph_file.mask):
            continue

        for right_code_point in alphabet:
            if right_code_point not in context:
                continue
            right_glyph_file = context[right_code_point][None]

            mask = left_glyph_file.mask.resize(right=right_glyph_file.width).plus(MonoBitmap.create(right_glyph_file.width, right_glyph_file.height, filled=True), x=left_glyph_file.width)
            offset = 0
            while True:
                test_mask = mask.plus(right_glyph_file.bitmap, x=left_glyph_file.width + offset - 1)
                if mask != test_mask:
                    break
                offset -= 1
                if offset <= -(right_glyph_file.width - 1):
                    break
            if offset < 0:
                pairs[(left_glyph_file.glyph_name, right_glyph_file.glyph_name)] = offset
    return pairs


def _build_kerning_feature(pairs: dict[tuple[str, str], int]) -> str:
    text = StringIO()
    text.write('languagesystem DFLT dflt;\n')
    text.write('languagesystem latn dflt;\n')
    text.write('\n')
    text.write('feature kern {\n')
    for (left_glyph_name, right_glyph_name), offset in sorted(pairs.items()):
        text.write(f'    position {left_glyph_name} {right_glyph_name} {offset * 100};\n')
    text.write('} kern;\n')
    return text.getvalue()


def make_kerning_feature_file(font_size: FontSize, context: dict[int, GlyphFlavorGroup]) -> FeatureFile:
    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)

    pairs = {}
    for alphabet in _alphabets:
        pairs.update(_calculate_kerning(alphabet, context))
    text = _build_kerning_feature(pairs)
    file_path = path_define.outputs_dir.joinpath(f'kerning-{font_size}px.fea')
    file_path.write_text(text, 'utf-8')
    return FeatureFile(text, file_path)
