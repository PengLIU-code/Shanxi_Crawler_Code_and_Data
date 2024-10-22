import os
import subprocess
import docx
import numpy as np
import logging
import sys
sys.path.append('/home/bld/.local/lib/python3.8/site-packages')
from paddleocr import PaddleOCR
from pdf2image import convert_from_path
import pytesseract
from tika import parser



# 配置日志记录器
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
# 初始化 OCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch', debug=False, gpu_id=2,logger=logger)


def ocr_pdf(pdf_path: str):
    # 转换 PDF 为图像
    images = convert_from_path(pdf_path)
    total_text = ''
    # 识别每页的文字
    for i, image in enumerate(images):
        image_np = np.array(image)  # 转换为 numpy 数组
        result = ocr.ocr(image_np, cls=True)
        text = ''
        for line in result:
            if not line:
                continue
            for word in line:
                text += word[1][0]  # 打印识别出的文字
        total_text += text + '\n'
    return total_text


def read_doc(file_path):
    parsed = parser.from_file(file_path)
    text = parsed['content']
    return text

def read_docx(file_path):
    doc = docx.Document(file_path)
    text = ''
    for para in doc.paragraphs:
        text += para.text
    return text

def read_wps(file_path):
    # 将 WPS 文件转换为 TXT 文件
    txt_file_path = file_path.replace('.wps', '.txt')
    cmd = f'libreoffice --headless --convert-to txt:Text {file_path} --outdir {os.path.dirname(file_path)}'
    try:
        # 执行命令
        subprocess.check_output(cmd, shell=True)
        # 读取转换后的 TXT 文件内容
        with open(txt_file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        return text
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
        print(f"Output: {e.output.decode('utf-8')}")
        return None

