import os.path
import requests
import pandas as pd
from download_file import download_file
from utils import save2file, read_cache, set_cache

SAVE_PATH = '/home/bld/data/data3/peng/Bridge/山西/data/detail.txt'

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': 'http://fgsjk.sxpc.gov.cn:8443/prod-api/extranet/regulation/search',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
}

def get_base_info(page_id: str) -> dict:
    url = f'http://fgsjk.sxpc.gov.cn:8443/prod-api/extranet/regulation/getById/{page_id}'
    print(f'开始爬取：{f"http://fgsjk.sxpc.gov.cn:8443/document-detail?id={page_id}&themeConfigId=undefined"}')
    response = requests.get(
        url,
        headers=headers,
        verify=False,
        timeout=10,
    )
    resp_json = response.json() 
    if resp_json.get('code', '') != 200:
        if 'Unmatched closing' in resp_json.get('msg', '') or 'Unclosed group near index' in resp_json.get('msg', ''):
            return {}
        raise Exception(f'获取详情失败: {resp_json}')
    
    file_id = None
    preferred_type = 'doc'
    fallback_type = 'pdf'

    # 优先选择 DOC 文件
    for file in resp_json['data']['regulationFiles']:
        if file['attType'] == preferred_type:
            file_id = file['attId']
            break

    # 如果没有找到 DOC 文件，再选择 PDF 文件
    if not file_id:
        for file in resp_json['data']['regulationFiles']:
            if file['attType'] == fallback_type:
                file_id = file['attId']
                break

    return {
    '文件标题': resp_json['data'].get('title', None),
    '法律效力位阶': resp_json['data'].get('filetypeVo', {}).get('name', None),
    '制定形式': resp_json['data'].get('formulateMode', None),
    '时效性': resp_json['data'].get('timeliness', None),
    '制定机关名称': resp_json['data']['officeVo']['name'] if resp_json['data']['officeVo'] else None,
    '发布日期': resp_json['data'].get('publishDate', None),
    '施行日期': resp_json['data'].get('expiryDate', None),
    '发文字号': resp_json['data'].get('releaseNum', None),
    '主题分类': resp_json['data'].get('tagNames', None),
    '通过日期': resp_json['data'].get('passDate', None),
    '页面地址': page_id,
    '文件地址': file_id
}


def spider_detail(row) -> dict:
    page_info = get_base_info(row['id'])
    if not page_info:
        # 这种就是页面报错的！！！
        return {
            'url': f'http://fgsjk.sxpc.gov.cn:8443/document-detail?id={row["id"]}&searchValue=',
            '标题': row['title'],
        }
    file_id = page_info.pop('文件地址', None)
    print(f'file_id: {file_id}')
    if file_id:
        try:
            doc_text = download_file(file_id)
        except Exception as e:
            print(e)
            doc_text = ''
    else:
        doc_text = ''
    _result = {
        'url': f'http://fgsjk.sxpc.gov.cn:8443/document-detail?id={row["id"]}&searchValue=',
        '标题': row['title'],
        **page_info, 
        '文件内容': doc_text.strip() if doc_text else '',
        'file_url': f'http://fgsjk.sxpc.gov.cn:8443/prod-api/gx-attachment/attachment/obtain/preview-word2pdf/{file_id}?module=gx-regulationdb-intranet' if file_id else None,
    }
    return _result


# results = []
# df = pd.read_csv('/home/bld/data/data3/peng/Bridge/山西/data/list.csv')
# for index, row in df.iterrows():
#     print(f'开始爬取第{index}条数据')
#     result = spider_detail(row)
#     results.append(result)
#     print(result)

# df = pd.DataFrame(results)
# df.to_csv('/home/bld/data/data3/peng/Bridge/山西/data/山西_results.csv', index=False)


results = []
df = pd.read_csv('/home/bld/data/data3/peng/Bridge/山西/data/list.csv')
batch_size = 500
batch_counter = 0
start_index = 550

for index, row in df.iterrows():
    if index < start_index:
        continue  # 跳过之前的行

    print(f'开始爬取第{index}条数据')
    result = spider_detail(row)
    results.append(result)
    print(result)
    
    batch_counter += 1
    if batch_counter == batch_size:
        # 保存当前批次结果
        df_results = pd.DataFrame(results)
        df_results.to_csv('/home/bld/data/data3/peng/Bridge/山西/data/山西_results_550.csv', mode='a', header=False, index=False)
        results = []  # 清空结果列表
        batch_counter = 0  # 重置计数器

# 保存剩余的结果
if results:
    df_results = pd.DataFrame(results)
    df_results.to_csv('/home/bld/data/data3/peng/Bridge/山西/data/山西_results_550.csv', mode='a', header=False, index=False)