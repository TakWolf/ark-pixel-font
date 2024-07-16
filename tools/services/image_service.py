import math

from PIL import Image, ImageFont, ImageDraw
from PIL.ImageFont import FreeTypeFont
from loguru import logger

from tools.configs import path_define, FontSize, WidthMode, LanguageFlavor
from tools.configs.font import FontConfig
from tools.services.font_service import DesignContext


def _load_font(font_size: FontSize, width_mode: WidthMode, language_flavor: LanguageFlavor, scale: int = 1) -> FreeTypeFont:
    file_path = path_define.outputs_dir.joinpath(f'ark-pixel-{font_size}px-{width_mode}-{language_flavor}.woff2')
    return ImageFont.truetype(file_path, font_size * scale)


def _draw_text(
        image: Image.Image,
        xy: tuple[float, float],
        text: str,
        font: FreeTypeFont,
        text_color: tuple[int, int, int, int] = (0, 0, 0, 255),
        shadow_color: tuple[int, int, int, int] | None = None,
        line_height: int | None = None,
        line_gap: int = 0,
        is_horizontal_centered: bool = False,
        is_vertical_centered: bool = False,
):
    draw = ImageDraw.Draw(image)
    x, y = xy
    default_line_height = sum(font.getmetrics())
    if line_height is None:
        line_height = default_line_height
    y += (line_height - default_line_height) / 2
    spacing = line_height + line_gap - font.getbbox('A')[3]
    if is_horizontal_centered:
        x -= draw.textbbox((0, 0), text, font=font)[2] / 2
    if is_vertical_centered:
        y -= line_height / 2
    if shadow_color is not None:
        draw.text((x + 1, y + 1), text, fill=shadow_color, font=font, spacing=spacing)
    draw.text((x, y), text, fill=text_color, font=font, spacing=spacing)


def _draw_text_background(
        image: Image.Image,
        alphabet: list[str],
        step: int,
        box_size: int,
        font: FreeTypeFont,
        text_color: tuple[int, int, int, int],
):
    draw = ImageDraw.Draw(image)
    alphabet_index = 0
    for index, c in enumerate(alphabet):
        code_point = ord(c)
        if code_point >= 0x4E00:
            alphabet_index = index
            break
    count_x = math.ceil(image.width / box_size)
    count_y = math.ceil(image.height / box_size)
    offset_x = (image.width - count_x * box_size) / 2 + (box_size - font.size) / 2
    offset_y = (image.height - count_y * box_size) / 2 + (box_size - sum(font.getmetrics())) / 2
    for y in range(count_y):
        for x in range(count_x):
            draw.text((offset_x + x * box_size, offset_y + y * box_size), alphabet[alphabet_index], fill=text_color, font=font)
            alphabet_index += step


def make_preview_image(font_config: FontConfig):
    font_latin = _load_font(font_config.font_size, 'proportional', 'latin')
    font_zh_cn = _load_font(font_config.font_size, 'proportional', 'zh_cn')
    font_zh_tr = _load_font(font_config.font_size, 'proportional', 'zh_tr')
    font_ja = _load_font(font_config.font_size, 'proportional', 'ja')

    image = Image.new('RGBA', (font_config.font_size * 27, font_config.font_size * 2 + font_config.line_height * 9), (255, 255, 255, 255))
    _draw_text(image, (font_config.font_size, font_config.font_size), '方舟像素字体 / Ark Pixel Font', font_zh_cn)
    _draw_text(image, (font_config.font_size, font_config.font_size + font_config.line_height), '我们度过的每个平凡的日常，也许就是连续发生的奇迹。', font_zh_cn)
    _draw_text(image, (font_config.font_size, font_config.font_size + font_config.line_height * 2), '我們度過的每個平凡的日常，也許就是連續發生的奇蹟。', font_zh_tr)
    _draw_text(image, (font_config.font_size, font_config.font_size + font_config.line_height * 3), '日々、私たちが過ごしている日常は、', font_ja)
    _draw_text(image, (font_config.font_size, font_config.font_size + font_config.line_height * 4), '実は奇跡の連続なのかもしれない。', font_ja)
    _draw_text(image, (font_config.font_size, font_config.font_size + font_config.line_height * 5), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_latin)
    _draw_text(image, (font_config.font_size, font_config.font_size + font_config.line_height * 6), 'the quick brown fox jumps over a lazy dog.', font_latin)
    _draw_text(image, (font_config.font_size, font_config.font_size + font_config.line_height * 7), '0123456789', font_latin)
    _draw_text(image, (font_config.font_size, font_config.font_size + font_config.line_height * 8), '★☆☺☹♠♡♢♣♤♥♦♧☀☼♩♪♫♬☂☁⚓✈⚔☯', font_latin)
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath(f'preview-{font_config.font_size}px.png')
    image.save(file_path)
    logger.info("Make preview image: '{}'", file_path)


def make_readme_banner(design_contexts: dict[FontSize, DesignContext]):
    font_config = design_contexts[12].font_config
    font_x1 = _load_font(font_config.font_size, 'proportional', 'zh_cn')
    font_x2 = _load_font(font_config.font_size, 'proportional', 'zh_cn', 2)
    alphabet = sorted(design_contexts[12].get_alphabet('proportional'))
    box_size = 14
    text_color = (255, 255, 255, 255)
    shadow_color = (80, 80, 80, 255)

    image_background = Image.open(path_define.images_dir.joinpath('readme-banner-background.png'))
    image = Image.new('RGBA', (image_background.width, image_background.height), (0, 0, 0, 0))
    _draw_text_background(image, alphabet, 50, box_size, font_x1, (200, 200, 200, 255))
    image.paste(image_background, mask=image_background)
    _draw_text(image, (image.width / 2, 28), '方舟像素字体', font_x2, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 28 + font_config.line_height * 2 + 4), '★ 开源的泛中日韩像素字体 ★', font_x1, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath('readme-banner.png')
    image.save(file_path)
    logger.info("Make readme banner: '{}'", file_path)


def make_github_banner(design_contexts: dict[FontSize, DesignContext]):
    font_config = design_contexts[12].font_config
    font_title = _load_font(font_config.font_size, 'proportional', 'zh_cn', 2)
    font_latin = _load_font(font_config.font_size, 'proportional', 'latin')
    font_zh_cn = _load_font(font_config.font_size, 'proportional', 'zh_cn')
    font_zh_tr = _load_font(font_config.font_size, 'proportional', 'zh_tr')
    font_ja = _load_font(font_config.font_size, 'proportional', 'ja')
    alphabet = sorted(design_contexts[12].get_alphabet('proportional'))
    box_size = 14
    text_color = (255, 255, 255, 255)
    shadow_color = (80, 80, 80, 255)

    image_background = Image.open(path_define.images_dir.joinpath('github-banner-background.png'))
    image = Image.new('RGBA', (image_background.width, image_background.height), (0, 0, 0, 0))
    _draw_text_background(image, alphabet, 12, box_size, font_zh_cn, (200, 200, 200, 255))
    image.paste(image_background, mask=image_background)
    _draw_text(image, (image.width / 2, 40 + font_config.line_height), '方舟像素字体 / Ark Pixel Font', font_title, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + font_config.line_height * 3), '★ 开源的泛中日韩像素字体 ★', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + font_config.line_height * 5), '我们度过的每个平凡的日常，也许就是连续发生的奇迹。', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + font_config.line_height * 6), '我們度過的每個平凡的日常，也許就是連續發生的奇蹟。', font_zh_tr, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + font_config.line_height * 7), '日々、私たちが過ごしている日常は、実は奇跡の連続なのかもしれない。', font_ja, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + font_config.line_height * 8), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + font_config.line_height * 9), 'the quick brown fox jumps over a lazy dog.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + font_config.line_height * 10), '0123456789', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 40 + font_config.line_height * 11), '★☆☺☹♠♡♢♣♤♥♦♧☀☼♩♪♫♬☂☁⚓✈⚔☯', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath('github-banner.png')
    image.save(file_path)
    logger.info("Make github banner: '{}'", file_path)


def make_itch_io_banner(design_contexts: dict[FontSize, DesignContext]):
    font_config = design_contexts[12].font_config
    font_x1 = _load_font(font_config.font_size, 'proportional', 'zh_cn')
    font_x2 = _load_font(font_config.font_size, 'proportional', 'zh_cn', 2)
    alphabet = sorted(design_contexts[12].get_alphabet('proportional'))
    box_size = 14
    text_color = (255, 255, 255, 255)
    shadow_color = (80, 80, 80, 255)

    image_background = Image.open(path_define.images_dir.joinpath('itch-io-banner-background.png'))
    image = Image.new('RGBA', (image_background.width, image_background.height), (0, 0, 0, 0))
    _draw_text_background(image, alphabet, 38, box_size, font_x1, (200, 200, 200, 255))
    image.paste(image_background, mask=image_background)
    _draw_text(image, (image.width / 2, 32), '方舟像素字体 / Ark Pixel Font', font_x2, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 32 + font_config.line_height * 2 + 4), '★ 开源的泛中日韩像素字体 ★', font_x1, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath('itch-io-banner.png')
    image.save(file_path)
    logger.info("Make itch.io banner: '{}'", file_path)


def make_itch_io_background(design_contexts: dict[FontSize, DesignContext]):
    font_config = design_contexts[12].font_config
    font = _load_font(font_config.font_size, 'proportional', 'zh_cn')
    alphabet = sorted(design_contexts[12].get_alphabet('proportional'))
    box_size = 14

    image = Image.new('RGBA', (box_size * 50, box_size * 50), (0, 0, 0, 0))
    _draw_text_background(image, alphabet, 5, box_size, font, (30, 30, 30, 255))
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath('itch-io-background.png')
    image.save(file_path)
    logger.info("Make itch.io background: '{}'", file_path)


def make_itch_io_cover(font_configs: dict[FontSize, FontConfig]):
    font_config = font_configs[12]
    font_title = _load_font(font_config.font_size, 'proportional', 'zh_cn', 2)
    font_latin = _load_font(font_config.font_size, 'proportional', 'latin')
    font_zh_cn = _load_font(font_config.font_size, 'proportional', 'zh_cn')
    font_zh_tr = _load_font(font_config.font_size, 'proportional', 'zh_tr')
    font_ja = _load_font(font_config.font_size, 'proportional', 'ja')
    text_color = (255, 255, 255, 255)
    shadow_color = (80, 80, 80, 255)

    image = Image.open(path_define.images_dir.joinpath('itch-io-cover-background.png'))
    _draw_text(image, (image.width / 2, 6), '方舟像素字体', font_title, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + font_config.line_height * 2), 'Ark Pixel Font', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + font_config.line_height * 4), '我们度过的每个平凡的日常，也许就是连续发生的奇迹。', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + font_config.line_height * 5), '我們度過的每個平凡的日常，也許就是連續發生的奇蹟。', font_zh_tr, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + font_config.line_height * 6), '日々、私たちが過ごしている日常は、', font_ja, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + font_config.line_height * 7), '実は奇跡の連続なのかもしれない。', font_ja, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + font_config.line_height * 8), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + font_config.line_height * 9), 'the quick brown fox jumps over a lazy dog.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + font_config.line_height * 10), '0123456789', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + font_config.line_height * 11), '★☆☺☹♠♡♢♣♤♥♦♧', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 6 + font_config.line_height * 12), '☀☼♩♪♫♬☂☁⚓✈⚔☯', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath('itch-io-cover.png')
    image.save(file_path)
    logger.info("Make itch.io cover: '{}'", file_path)


def make_afdian_cover(font_configs: dict[FontSize, FontConfig]):
    font_config = font_configs[12]
    font_title = _load_font(font_config.font_size, 'proportional', 'zh_cn', 2)
    font_latin = _load_font(font_config.font_size, 'proportional', 'latin')
    font_zh_cn = _load_font(font_config.font_size, 'proportional', 'zh_cn')
    font_zh_tr = _load_font(font_config.font_size, 'proportional', 'zh_tr')
    font_ja = _load_font(font_config.font_size, 'proportional', 'ja')
    text_color = (255, 255, 255, 255)
    shadow_color = (80, 80, 80, 255)

    image = Image.open(path_define.images_dir.joinpath('afdian-cover-background.png'))
    _draw_text(image, (image.width / 2, 12), '方舟像素字体', font_title, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 12 + font_config.line_height * 2), 'Ark Pixel Font', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + font_config.line_height * 3), '★ 开源的泛中日韩像素字体 ★', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + font_config.line_height * 5), '我们度过的每个平凡的日常，也许就是连续发生的奇迹。', font_zh_cn, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + font_config.line_height * 6), '我們度過的每個平凡的日常，也許就是連續發生的奇蹟。', font_zh_tr, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + font_config.line_height * 7), '日々、私たちが過ごしている日常は、', font_ja, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + font_config.line_height * 8), '実は奇跡の連続なのかもしれない。', font_ja, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + font_config.line_height * 10), 'THE QUICK BROWN FOX JUMPS OVER A LAZY DOG.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + font_config.line_height * 11), 'the quick brown fox jumps over a lazy dog.', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + font_config.line_height * 12), '0123456789', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + font_config.line_height * 13), '★☆☺☹♠♡♢♣♤♥♦♧', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    _draw_text(image, (image.width / 2, 18 + font_config.line_height * 14), '☀☼♩♪♫♬☂☁⚓✈⚔☯', font_latin, text_color=text_color, shadow_color=shadow_color, is_horizontal_centered=True)
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath('afdian-cover.png')
    image.save(file_path)
    logger.info("Make afdian cover: '{}'", file_path)
