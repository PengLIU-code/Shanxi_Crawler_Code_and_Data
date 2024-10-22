import os
import uuid
import requests
from document_convert import ocr_pdf, read_doc, read_docx, read_wps

headers = {
    'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'fgsjk.sxpc.gov.cn:8443',
    'Referer': 'http://fgsjk.sxpc.gov.cn:8443/document-detail?id=8650cf7a6009ae3b0b457f7a4412058c',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
}
#  url = f'http://fgsjk.sxpc.gov.cn:8443/prod-api/gx-attachment/attachment/obtain/download/{file_id}'

def download_file(file_id: str) -> str:
    params = {
        'module': 'gx-regulationdb-intranet',
        'id': file_id,
    }

    response = requests.get(
        'http://fgsjk.sxpc.gov.cn:8443/prod-api/gx-attachment/attachment/obtain/download',
        params=params,
        headers=headers,
        verify=False,
        timeout=10,
    )
    if response.status_code != 200:
        raise Exception(f'下载失败: {response.text}')
        # 获取文件名和后缀
    filename_final = response.headers.get('Content-Disposition')
    if filename_final:
        filename_final = filename_final.split('.')[-1].lower()
    else:
        filename_final = 'doc'

    file_path = f'/home/bld/data/data3/peng/Bridge/山西/tmp/{str(uuid.uuid4())}.{filename_final}'

    with open(file_path, 'wb') as f:
        f.write(response.content)
    
    if filename_final in ('doc', 'wps', 'docx','pdf','txt'): # 如果是 doc, wps, docx, pdf 文件
        # 如果是 doc文件，读取内容
        if filename_final == 'doc':
            text = read_doc(file_path)
        # 如果是 docx文件，读取内容
        elif filename_final == 'docx':
            text = read_docx(file_path)
        # 如果是 wps文件，读取内容
        elif filename_final == 'wps':
            text = read_wps(file_path)
        # 如果是 pdf文件，读取内容
        elif filename_final == 'pdf':
            text = ocr_pdf(file_path)
        elif filename_final == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        # os.remove(file_path) # 删除原文件
        return text