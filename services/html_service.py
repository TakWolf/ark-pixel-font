import logging
import os

import bs4
import minify_html

import configs
from configs import path_define
from utils import fs_util

logger = logging.getLogger('html-service')


def make_alphabet_html_file(font_config, width_mode, alphabet):
    template = configs.template_env.get_template('alphabet.html')
    html = template.render(
        configs=configs,
        font_config=font_config,
        width_mode=width_mode,
        alphabet=''.join([c for c in alphabet if ord(c) >= 128]),
    )
    html = minify_html.minify(html, minify_css=True, minify_js=True)
    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    html_file_path = os.path.join(path_define.outputs_dir, font_config.get_alphabet_html_file_name(width_mode))
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info(f'make {html_file_path}')


def _handle_demo_html_element(soup, element, alphabet, width_mode):
    element_type = type(element)
    if element_type == bs4.element.Tag:
        for child_element in list(element.contents):
            _handle_demo_html_element(soup, child_element, alphabet, width_mode)
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
                        temp_child['class'] = f'char-notdef-{width_mode}'
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
                temp_child['class'] = f'char-notdef-{width_mode}'
                temp_child.string = text_buffer
            temp_parent.append(temp_child)
        element.replace_with(temp_parent)
        temp_parent.unwrap()


def make_demo_html_file(font_config, alphabet_group):
    template = configs.template_env.get_template('demo.html')
    html = template.render(
        configs=configs,
        font_config=font_config,
    )
    soup = bs4.BeautifulSoup(html, 'html.parser')
    elements = soup.select('#page')
    for width_mode in configs.width_modes:
        alphabet = alphabet_group[width_mode]
        for element in elements:
            _handle_demo_html_element(soup, element, alphabet, width_mode)
    html = str(soup)
    # FIXME 这里样式压缩会造成语言标签失效
    html = minify_html.minify(html, minify_css=False, minify_js=True)
    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    html_file_path = os.path.join(path_define.outputs_dir, font_config.demo_html_file_name)
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info(f'make {html_file_path}')


def make_index_html_file():
    template = configs.template_env.get_template('index.html')
    html = template.render(configs=configs)
    # FIXME 这里样式压缩会造成背景动画闪烁
    html = minify_html.minify(html, minify_css=False, minify_js=True)
    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    html_file_path = os.path.join(path_define.outputs_dir, 'index.html')
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info(f'make {html_file_path}')


def make_playground_html_file():
    template = configs.template_env.get_template('playground.html')
    html = template.render(configs=configs)
    html = minify_html.minify(html, minify_css=True, minify_js=True)
    fs_util.make_dirs_if_not_exists(path_define.outputs_dir)
    html_file_path = os.path.join(path_define.outputs_dir, 'playground.html')
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(html)
    logger.info(f'make {html_file_path}')
