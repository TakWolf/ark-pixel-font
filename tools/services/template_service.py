from collections.abc import Mapping, Collection
from typing import Sequence

import bs4
from jinja2 import Environment, FileSystemLoader
from loguru import logger

from tools.config import path_define, project, manifest, options
from tools.config.font import FontConfig
from tools.config.options import WidthMode

_environment = Environment(
    trim_blocks=True,
    lstrip_blocks=True,
    loader=FileSystemLoader(path_define.TEMPLATES_DIR),
)


def _make_html(template_name: str, file_name: str, params: Mapping[str, object] | None = None) -> None:
    params = dict(params) if params is not None else {}
    params['project'] = project
    params['manifest'] = manifest
    params['options'] = options

    html = _environment.get_template(template_name).render(params)

    path_define.OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = path_define.OUTPUTS_DIR.joinpath(file_name)
    file_path.write_text(html, 'utf-8')
    logger.info("Make html: '{}'", file_path)


def make_alphabet_html(font_config: FontConfig, width_mode: WidthMode, alphabet: Sequence[str]) -> None:
    _make_html('alphabet.html', f'alphabet-{font_config.font_size}px-{width_mode}.html', {
        'font_config': font_config,
        'width_mode': width_mode,
        'alphabet': ''.join(c for c in alphabet if ord(c) >= 128),
    })


def _handle_demo_html_element(
        soup: bs4.BeautifulSoup,
        element: bs4.PageElement,
        alphabets: Mapping[WidthMode, Collection[str]],
) -> None:
    if isinstance(element, bs4.element.Tag):
        for child_element in element.contents:
            _handle_demo_html_element(soup, child_element, alphabets)
    elif isinstance(element, bs4.element.NavigableString):
        text = str(element)
        tmp_parent = soup.new_tag('div')
        last_status = None
        text_buffer = ''
        for c in text:
            if c == ' ':
                status = last_status
            elif c == '\n':
                status = 'all'
            elif c in alphabets['monospaced'] and c in alphabets['proportional']:
                status = 'all'
            elif c in alphabets['monospaced']:
                status = 'monospaced'
            elif c in alphabets['proportional']:
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


def make_demo_html(font_config: FontConfig, alphabets: Mapping[WidthMode, Sequence[str]]) -> None:
    alphabets = {
        width_mode: set(alphabet)
        for width_mode, alphabet in alphabets.items()
    }

    content_html = path_define.TEMPLATES_DIR.joinpath('demo-content.html').read_text('utf-8')
    soup = bs4.BeautifulSoup(content_html, 'html.parser')
    _handle_demo_html_element(soup, soup, alphabets)
    content_html = str(soup).strip()

    _make_html('demo.html', f'demo-{font_config.font_size}px.html', {
        'font_config': font_config,
        'content_html': content_html,
    })


def make_index_html() -> None:
    _make_html('index.html', 'index.html')


def make_playground_html() -> None:
    _make_html('playground.html', 'playground.html')
