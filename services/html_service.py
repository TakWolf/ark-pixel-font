import logging
import os

import bs4
import minify_html

import configs
from configs import path_define
from utils import fs_util

logger = logging.getLogger('html-service')


def make_alphabet_html_file(font_config, alphabet):
    template = configs.template_env.get_template('alphabet.html')
    html = template.render(
        font_config=font_config,
        language_specifics=configs.language_specifics,
        alphabet=''.join([c for c in alphabet if ord(c) >= 128]),
    )
    html = minify_html.minify(html, minify_css=True, minify_js=True)
    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    html_file_path = os.path.join(path_define.outputs_dir, font_config.alphabet_html_file_name)
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info(f'make {html_file_path}')


def _handle_demo_html_element(soup, element, alphabet):
    element_type = type(element)
    if element_type == bs4.element.Tag:
        for child_element in list(element.contents):
            _handle_demo_html_element(soup, child_element, alphabet)
    elif element_type == bs4.element.NavigableString:
        text = str(element)
        temp_parent = soup.new_tag('span')
        current_status = True
        text_buffer = ''
        for c in text:
            status = c in alphabet or not c.isprintable()
            if current_status != status:
                if text_buffer != '':
                    if current_status:
                        temp_child = bs4.element.NavigableString(text_buffer)
                    else:
                        temp_child = soup.new_tag('span')
                        temp_child['class'] = 'char-notdef'
                        temp_child.string = text_buffer
                    temp_parent.append(temp_child)
                current_status = status
                text_buffer = ''
            text_buffer += c
        if text_buffer != '':
            if current_status:
                temp_child = bs4.element.NavigableString(text_buffer)
            else:
                temp_child = soup.new_tag('span')
                temp_child['class'] = 'char-notdef'
                temp_child.string = text_buffer
            temp_parent.append(temp_child)
        element.replace_with(temp_parent)
        temp_parent.unwrap()


def make_demo_html_file(font_config, alphabet):
    template = configs.template_env.get_template('demo.html')
    html = template.render(
        font_config=font_config,
        language_specifics=configs.language_specifics,
    )
    soup = bs4.BeautifulSoup(html, 'html.parser')
    elements = soup.select('.page')
    for element in elements:
        _handle_demo_html_element(soup, element, alphabet)
    html = str(soup)
    html = minify_html.minify(html, minify_css=True, minify_js=True)
    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    html_file_path = os.path.join(path_define.outputs_dir, font_config.demo_html_file_name)
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info(f'make {html_file_path}')


def make_index_html_file():
    template = configs.template_env.get_template('index.html')
    html = template.render(
        font_configs=configs.font_configs,
        language_specifics=configs.language_specifics,
    )
    html = minify_html.minify(html, minify_css=True, minify_js=True)
    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    html_file_path = os.path.join(path_define.outputs_dir, 'index.html')
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info(f'make {html_file_path}')


def make_playground_html_file():
    template = configs.template_env.get_template('playground.html')
    html = template.render(
        font_configs=configs.font_configs,
        language_specifics=configs.language_specifics,
    )
    html = minify_html.minify(html, minify_css=True, minify_js=True)
    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    html_file_path = os.path.join(path_define.outputs_dir, 'playground.html')
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info(f'make {html_file_path}')
