import random

import bs4
from jinja2 import Environment, FileSystemLoader
from loguru import logger

from tools import configs
from tools.configs import path_define, FontSize, WidthMode
from tools.configs.font import FontConfig
from tools.services.font_service import DesignContext

_environment = Environment(
    trim_blocks=True,
    lstrip_blocks=True,
    loader=FileSystemLoader(path_define.templates_dir),
)

_build_random_key = random.random()

_locale_to_language_flavor = {
    'en': 'latin',
    'zh-cn': 'zh_cn',
    'zh-hk': 'zh_hk',
    'zh-tw': 'zh_tw',
    'zh-tr': 'zh_tr',
    'ja': 'ja',
    'ko': 'ko',
}


def _make_html(template_name: str, file_name: str, params: dict[str, object] | None = None):
    params = {} if params is None else dict(params)
    params['build_random_key'] = _build_random_key
    params['width_modes'] = configs.width_modes
    params['locale_to_language_flavor'] = _locale_to_language_flavor

    html = _environment.get_template(template_name).render(params)

    path_define.outputs_dir.mkdir(parents=True, exist_ok=True)
    file_path = path_define.outputs_dir.joinpath(file_name)
    file_path.write_text(html, 'utf-8')
    logger.info("Make html: '{}'", file_path)


def make_alphabet_html(design_context: DesignContext, width_mode: WidthMode):
    _make_html('alphabet.html', f'alphabet-{design_context.font_size}px-{width_mode}.html', {
        'font_config': design_context.font_config,
        'width_mode': width_mode,
        'alphabet': ''.join(sorted(c for c in design_context.get_alphabet(width_mode) if ord(c) >= 128)),
    })


def _handle_demo_html_element(design_context: DesignContext, soup: bs4.BeautifulSoup, element: bs4.PageElement):
    if isinstance(element, bs4.element.Tag):
        for child_element in list(element.contents):
            _handle_demo_html_element(design_context, soup, child_element)
    elif isinstance(element, bs4.element.NavigableString):
        alphabet_monospaced = design_context.get_alphabet('monospaced')
        alphabet_proportional = design_context.get_alphabet('proportional')
        text = str(element)
        tmp_parent = soup.new_tag('div')
        last_status = None
        text_buffer = ''
        for c in text:
            if c == ' ':
                status = last_status
            elif c == '\n':
                status = 'all'
            elif c in alphabet_monospaced and c in alphabet_proportional:
                status = 'all'
            elif c in alphabet_monospaced:
                status = 'monospaced'
            elif c in alphabet_proportional:
                status = 'proportional'
            else:
                status = None
            if last_status != status:
                if text_buffer != '':
                    if last_status == 'all':
                        tmp_child = bs4.element.NavigableString(text_buffer)
                    else:
                        tmp_child = soup.new_tag('span')
                        tmp_child.string = text_buffer
                        if last_status == 'monospaced':
                            tmp_child['class'] = f'char-notdef-proportional'
                        elif last_status == 'proportional':
                            tmp_child['class'] = f'char-notdef-monospaced'
                        else:
                            tmp_child['class'] = f'char-notdef-monospaced char-notdef-proportional'
                    tmp_parent.append(tmp_child)
                    text_buffer = ''
                last_status = status
            text_buffer += c
        if text_buffer != '':
            if last_status == 'all':
                tmp_child = bs4.element.NavigableString(text_buffer)
            else:
                tmp_child = soup.new_tag('span')
                tmp_child.string = text_buffer
                if last_status == 'monospaced':
                    tmp_child['class'] = f'char-notdef-proportional'
                elif last_status == 'proportional':
                    tmp_child['class'] = f'char-notdef-monospaced'
                else:
                    tmp_child['class'] = f'char-notdef-monospaced char-notdef-proportional'
            tmp_parent.append(tmp_child)
        element.replace_with(tmp_parent)
        tmp_parent.unwrap()


def make_demo_html(design_context: DesignContext):
    content_html = path_define.templates_dir.joinpath('demo-content.html').read_text('utf-8')
    content_html = ''.join(line.strip() for line in content_html.split('\n'))
    soup = bs4.BeautifulSoup(content_html, 'html.parser')
    _handle_demo_html_element(design_context, soup, soup)
    content_html = str(soup)

    _make_html('demo.html', f'demo-{design_context.font_size}px.html', {
        'font_config': design_context.font_config,
        'content_html': content_html,
    })


def make_index_html(font_configs: dict[FontSize, FontConfig]):
    _make_html('index.html', 'index.html', {
        'font_configs': font_configs,
    })


def make_playground_html(font_configs: dict[FontSize, FontConfig]):
    _make_html('playground.html', 'playground.html', {
        'font_configs': font_configs,
    })
