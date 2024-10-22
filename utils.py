#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/8/28 16:36
# @File    : utils.py
import json
import os
import time
import hmac

import requests

from hashlib import sha256
from docx import Document


headers = {
    'Accept': 'text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    "Accept-Encoding": "gzip, deflate",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
}


server_url = 'http://192.168.31.6:5008/convert'
# server_url = 'http://doc.lt.com/convert'


def covert_doc2docx(filepath: str, origin_type: str, to_type: str = 'txt') -> (bool, str):
    files = {'file': open(filepath, 'rb')}
    response = requests.post(server_url, headers=headers, files=files, data={'to_type': to_type}, timeout=60)

    new_path = filepath.replace(f'.{origin_type}', f'.{to_type}')
    if response.status_code == 200:
        with open(new_path, 'wb') as f:
            f.write(response.content)
    else:
        print(response.text)
        return False, ''
    return True, new_path


def save2file(file_path: str, row_data: dict):
    with open(file_path, 'a+', encoding='utf-8') as f:
        f.write(json.dumps(row_data, ensure_ascii=False, separators=(',', ':')))
        f.write('\n')


def extract_text_from_docx(file_path, rety=0) -> str:
    if rety >= 3:
        raise Exception('解析word失败，重试了3次还是不行')
    if not os.path.exists(file_path):
        time.sleep(0.1)
        return extract_text_from_docx(file_path, rety + 1)
    doc = Document(file_path)
    full_text = []

    for para in doc.paragraphs:
        full_text.append(para.text)
    os.remove(file_path)
    return '\n'.join(full_text)


def read_cache(cache_file: str) -> list:
    if not os.path.exists(cache_file):
        return []
    with open(cache_file, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines() if line]


def set_cache(key: str, cache_file: str):
    with open(cache_file, 'a+', encoding='utf-8') as f:
        f.write(f'{key}\n')


def get_sign(key='8800c670ccc54bb0a9724ff05549f208', data='1724860143-POST-/statute/bigdata/list-0'):
    data = data.encode('utf-8')
    return hmac.new(key.encode('utf-8'), data, digestmod=sha256).hexdigest()


if __name__ == '__main__':
    print(covert_doc2docx('./湖南省/tmp/87540403-3264-4a77-bb5c-1be3617ca57b.doc', 'doc', 'txt'))
    # print(get_sign('8800c670ccc54bb0a9724ff05549f208', '1724860143-POST-/statute/bigdata/list-0'))
