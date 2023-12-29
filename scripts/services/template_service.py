import logging
import os

import bs4
from jinja2 import Environment, FileSystemLoader

from scripts import configs
from scripts.configs import path_define, FontConfig
from scripts.services.font_service import DesignContext
from scripts.utils import fs_util

logger = logging.getLogger('template-service')

_environment = Environment(
    trim_blocks=True,
    lstrip_blocks=True,
    loader=FileSystemLoader(path_define.templates_dir),
)


def make_alphabet_html_file(font_config: FontConfig, context: DesignContext, width_mode: str):
    alphabet = [c for c in context.get_alphabet(width_mode) if ord(c) >= 128]
    alphabet.sort()
    template = _environment.get_template('alphabet.html')
    html = template.render(
        configs=configs,
        font_config=font_config,
        width_mode=width_mode,
        alphabet=''.join(alphabet),
    )
    fs_util.make_dirs(path_define.outputs_dir)
    file_path = os.path.join(path_define.outputs_dir, font_config.get_alphabet_html_file_name(width_mode))
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info("Make alphabet html file: '%s'", file_path)


def _handle_demo_html_element(context: DesignContext, soup: bs4.BeautifulSoup, element: bs4.PageElement):
    if isinstance(element, bs4.element.Tag):
        for child_element in list(element.contents):
            _handle_demo_html_element(context, soup, child_element)
    elif isinstance(element, bs4.element.NavigableString):
        alphabet_monospaced = context.get_alphabet('monospaced')
        alphabet_proportional = context.get_alphabet('proportional')
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


def make_demo_html_file(font_config: FontConfig, context: DesignContext):
    content_file_path = os.path.join(path_define.templates_dir, 'demo-content.html')
    with open(content_file_path, 'r', encoding='utf-8') as file:
        content_html = file.read()
        content_html = ''.join(line.strip() for line in content_html.split('\n'))
    soup = bs4.BeautifulSoup(content_html, 'html.parser')
    _handle_demo_html_element(context, soup, soup)
    content_html = str(soup)

    template = _environment.get_template('demo.html')
    html = template.render(
        configs=configs,
        font_config=font_config,
        content_html=content_html,
    )
    fs_util.make_dirs(path_define.outputs_dir)
    file_path = os.path.join(path_define.outputs_dir, font_config.demo_html_file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info("Make demo html file: '%s'", file_path)


def make_index_html_file():
    template = _environment.get_template('index.html')
    html = template.render(configs=configs)
    fs_util.make_dirs(path_define.outputs_dir)
    file_path = os.path.join(path_define.outputs_dir, 'index.html')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info("Make index html file: '%s'", file_path)


def make_playground_html_file():
    template = _environment.get_template('playground.html')
    html = template.render(configs=configs)
    fs_util.make_dirs(path_define.outputs_dir)
    file_path = os.path.join(path_define.outputs_dir, 'playground.html')
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info("Make playground html file: '%s'", file_path)
