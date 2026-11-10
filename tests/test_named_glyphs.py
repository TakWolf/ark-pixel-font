import re
from collections.abc import Callable
from itertools import chain

import pytest
from pixel_font_knife.named.context import NamedContext

from tools.config import options
from tools.config.font import FontConfig
from tools.config.glyph.bitmap import BitmapGlobalRules, BitmapSizeRules
from tools.config.glyph.metric import MetricSizeRules
from tools.config.options import FontSize, GlyphScope


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
@pytest.mark.parametrize('glyph_scope', options.GLYPH_SCOPES)
def test_default_flavor(
        load_named_context: Callable[[FontSize, GlyphScope], NamedContext],
        font_size: FontSize,
        glyph_scope: GlyphScope,
) -> None:
    context = load_named_context(font_size, glyph_scope)

    for name_key, glyph_variants in sorted(context.items()):
        assert None in glyph_variants, f'[{font_size}px] missing default flavor: {glyph_scope} {name_key}'


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
@pytest.mark.parametrize('glyph_scope', options.GLYPH_SCOPES)
def test_duplicate_glyph_bitmap(
        load_named_context: Callable[[FontSize, GlyphScope], NamedContext],
        font_size: FontSize,
        glyph_scope: GlyphScope,
) -> None:
    context = load_named_context(font_size, glyph_scope)

    for name_key, glyph_variants in sorted(context.items()):
        bitmap_strings = {}
        for glyph_file in set(glyph_variants.values()):
            bitmap_string = str(glyph_file.canvas.bitmap)
            assert bitmap_string not in bitmap_strings, f'[{font_size}px] duplicate glyph bitmap:\n{str(glyph_file.file_path)!r}\n{str(bitmap_strings[bitmap_string].file_path)!r}'
            bitmap_strings[bitmap_string] = glyph_file


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
@pytest.mark.parametrize('glyph_scope', options.GLYPH_SCOPES)
def test_top_and_right_padding(
        load_named_context: Callable[[FontSize, GlyphScope], NamedContext],
        bitmap_global_rules: BitmapGlobalRules,
        load_bitmap_size_rules: Callable[[FontSize], BitmapSizeRules],
        font_size: FontSize,
        glyph_scope: GlyphScope,
) -> None:
    context = load_named_context(font_size, glyph_scope)
    padding_global_rules = bitmap_global_rules.named_global_rules.padding_global_rules
    padding_size_rules = load_bitmap_size_rules(font_size).named_size_rules.padding_size_rules

    for name_key, glyph_variants in sorted(context.items()):
        for glyph_file in set(glyph_variants.values()):
            file_id = f'{glyph_scope}/{glyph_file.name_key}'
            if glyph_file.flavors:
                file_id = f'{file_id} {','.join(glyph_file.flavors)}'

            if (
                    name_key not in padding_global_rules.allow_no_top_and_right.name_keys and
                    name_key not in padding_global_rules.allow_no_top_only.name_keys and
                    file_id not in padding_size_rules.allow_no_top_and_right.file_ids and
                    file_id not in padding_size_rules.allow_no_top_only.file_ids
            ):
                assert glyph_file.canvas.is_blank or glyph_file.canvas.trimmed_padding.top >= 1, f'[{font_size}px] glyph has no 1px top padding: {str(glyph_file.file_path)!r}'

            if (
                    name_key not in padding_global_rules.allow_no_top_and_right.name_keys and
                    name_key not in padding_global_rules.allow_no_right_only.name_keys and
                    file_id not in padding_size_rules.allow_no_top_and_right.file_ids and
                    file_id not in padding_size_rules.allow_no_right_only.file_ids
            ):
                assert glyph_file.canvas.is_blank or glyph_file.canvas.trimmed_padding.right >= 1, f'[{font_size}px] glyph has no 1px right padding: {str(glyph_file.file_path)!r}'


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
def test_padding_size_rules(
        load_named_context: Callable[[FontSize, GlyphScope], NamedContext],
        load_bitmap_size_rules: Callable[[FontSize], BitmapSizeRules],
        font_size: FontSize,
) -> None:
    contexts = {
        glyph_scope: load_named_context(font_size, glyph_scope)
        for glyph_scope in options.GLYPH_SCOPES
    }
    padding_size_rules = load_bitmap_size_rules(font_size).named_size_rules.padding_size_rules
    file_id_regex = re.compile(r'[/\s,]')

    for file_id in chain(padding_size_rules.allow_no_top_and_right.file_ids, padding_size_rules.allow_no_top_only.file_ids):
        parts = file_id_regex.split(file_id)
        glyph_scope = parts[0]
        name_key = parts[1]
        flavors = parts[2:]
        flavor = flavors[0] if flavors else None
        glyph_file = contexts[glyph_scope][name_key].get(flavor, None)

        assert glyph_file is not None, f'[{font_size}px] invalid file-id in padding size rules: {file_id!r}, referenced glyph variant does not exist'
        assert glyph_file.flavors == flavors, f'[{font_size}px] incorrect flavors in padding size rules: {file_id!r}, expected {glyph_file.flavors!r}, got {flavors!r}'
        assert not glyph_file.canvas.is_blank and glyph_file.canvas.trimmed_padding.top == 0, f'[{font_size}px] unnecessary top padding exception in size rules: {file_id!r} ({str(glyph_file.file_path)!r})'

    for file_id in chain(padding_size_rules.allow_no_top_and_right.file_ids, padding_size_rules.allow_no_right_only.file_ids):
        parts = file_id_regex.split(file_id)
        glyph_scope = parts[0]
        name_key = parts[1]
        flavors = parts[2:]
        flavor = flavors[0] if flavors else None
        glyph_file = contexts[glyph_scope][name_key].get(flavor, None)

        assert glyph_file is not None, f'[{font_size}px] invalid file-id in padding size rules: {file_id!r}, referenced glyph variant does not exist'
        assert glyph_file.flavors == flavors, f'[{font_size}px] incorrect flavors in padding size rules: {file_id!r}, expected {glyph_file.flavors!r}, got {flavors!r}'
        assert not glyph_file.canvas.is_blank and glyph_file.canvas.trimmed_padding.right == 0, f'[{font_size}px] unnecessary right padding exception in size rules: {file_id!r} ({str(glyph_file.file_path)!r})'


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
@pytest.mark.parametrize('glyph_scope', options.GLYPH_SCOPES)
def test_glyph_bitmap_dimensions(
        load_font_config: Callable[[FontSize], FontConfig],
        load_named_context: Callable[[FontSize, GlyphScope], NamedContext],
        font_size: FontSize,
        glyph_scope: GlyphScope,
) -> None:
    canvas_height = load_font_config(font_size).canvas_height
    context = load_named_context(font_size, glyph_scope)

    for name_key, glyph_variants in sorted(context.items()):
        for glyph_file in set(glyph_variants.values()):
            if glyph_scope == 'common' or glyph_scope == 'monospaced':
                assert glyph_file.canvas.height % font_size == 0, f'[{font_size}px] glyph bitmap dimensions error: {str(glyph_file.file_path)!r}'
                assert glyph_file.canvas.width % (font_size / 2) == 0, f'[{font_size}px] glyph bitmap dimensions error: {str(glyph_file.file_path)!r}'

            if glyph_scope == 'proportional':
                assert glyph_file.canvas.height == canvas_height, f'[{font_size}px] glyph bitmap dimensions error: {str(glyph_file.file_path)!r}'


@pytest.mark.parametrize('font_size', options.FONT_SIZES)
def test_metric_size_rules(
        load_named_context: Callable[[FontSize, GlyphScope], NamedContext],
        load_metric_size_rules: Callable[[FontSize], MetricSizeRules],
        font_size: FontSize,
) -> None:
    contexts = {
        glyph_scope: load_named_context(font_size, glyph_scope)
        for glyph_scope in options.GLYPH_SCOPES
    }
    metric_size_rules = load_metric_size_rules(font_size).named_size_rules
    file_id_regex = re.compile(r'[/\s,]')

    for file_id in metric_size_rules.skip_vertical_adjustment.file_ids:
        parts = file_id_regex.split(file_id)
        glyph_scope = parts[0]
        name_key = parts[1]
        flavors = parts[2:]
        flavor = flavors[0] if flavors else None
        glyph_file = contexts[glyph_scope][name_key].get(flavor, None)

        assert glyph_file is not None, f'[{font_size}px] invalid file-id in metric size rules: {file_id!r}, referenced glyph variant does not exist'
        assert glyph_file.flavors == flavors, f'[{font_size}px] incorrect flavors in metric size rules: {file_id!r}, expected {glyph_file.flavors!r}, got {flavors!r}'
