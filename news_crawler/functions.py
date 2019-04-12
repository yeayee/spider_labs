# -*- coding: UTF-8 -*-
import re
import requests
import cchardet
import traceback
import urllib.parse as urlparse


# ---------------------------------- 异步下载 ----------------------------------------
async def fetch(session, url, headers=None, timeout=9, binary=False):
    _headers = {
        "User-Agent": 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)',
    }
    if headers:
        _headers = headers
    try:
        async with session.get(url, headers=_headers, timeout=timeout) as response:
            status = response.status
            html = await response.read()
            if not binary:
                encoding = cchardet.detect(html)["encoding"]
                html = html.decode(encoding, errors="ignore")
            redirected_url = str(response.url)
    except Exception as e:
        msg = f'Failed download: {url} | exception: {str(type(e))}, {str(e)}'
        print(msg)
        status = 0
        if binary:
            html = b""
        else:
            html = ""
        redirected_url = url

    return status, html, redirected_url


# ------------------------------------- 同步下载 ---------------------------------------
def downloader(url, timeout=10, headers=None, debug=False, binary=False):
    # 默认返回str内容。URL链接的是图片等二进制内容时，注意调用时要设binary=True
    _headers = {
        "User-Agent": 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)'
    }
    redirected_url = url
    if headers:
        _headers = headers

    try:
        r = requests.get(url, headers=_headers, timeout=timeout)
        if binary:
            html = r.content
        else:
            encoding = cchardet.detect(r.content)['encoding']  # 探测文本编码格式
            html = r.content.decode(encoding)
        status = r.status_code
        redirected_url = r.url
    except:
        if debug:
            traceback.print_exc()
        msg = "failed download: {}".format(url)
        print(msg)
        if binary:
            html = b""
        else:
            html = ""
        status = 0

    return status, html, redirected_url


# -------------------------------------- 网址清洗 ---------------------------------------
g_bin_postfix = set([
    'exe', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'pdf',
    'jpg', 'png', 'bmp', 'jpeg', 'gif',
    'zip', 'rar', 'tar', 'bz2', '7z', 'gz',
    'flv', 'mp4', 'avi', 'wmv', 'mkv',
    'apk',
])

g_news_postfix = [
    '.html?', '.htm?', '.shtml?',
    '.shtm?',
]


def clean_url(url):
    # 1. 是否为合法的http url
    if not url.startswith('http'):
        return ''

    # 2. 去掉静态化url后面的参数
    for np in g_news_postfix:
        p = url.find(np)
        if p > -1:
            p = url.find('?')
            url = url[:p]
            return url

    # 3. 不下载二进制类内容的链接
    up = urlparse.urlparse(url)
    path = up.path
    if not path:
        path = '/'
    postfix = path.split('.')[-1].lower()
    if postfix in g_bin_postfix:
        return ''

    # 4. 去掉标识流量来源的参数
    good_queries = []
    for query in up.query.split('&'):
        qv = query.split('=')
        if qv[0].startswith('spm') or qv[0].startswith('utm_'):
            continue
        if len(qv) == 1:
            continue
        good_queries.append(query)
    query = '&'.join(good_queries)
    url = urlparse.urlunparse((
        up.scheme,
        up.netloc,
        path,
        up.params,
        query,
        ''  # crawler do not care fragment
    ))
    return url


# -------------------------------------- URL链接抽取 ---------------------------------------
g_pattern_tag_a = re.compile(r'<a[^>]*?href=[\'"]?([^> \'"]+)[^>]*?>(.*?)</a>', re.I | re.S | re.M)


def extract_links_re(url, html):
    newlinks = set()
    aa = g_pattern_tag_a.findall(html)
    for a in aa:
        link = a[0].strip()
        if not link:
            continue
        link = urlparse.urljoin(url, link)
        link = clean_url(link)
        if not link:
            continue
        newlinks.add(link)
    return newlinks


# -------------------------------------- 日志对象 ---------------------------------------
def init_file_logger(fname):
    import logging
    from logging.handlers import TimedRotatingFileHandler
    ch = TimedRotatingFileHandler(fname, when="midnight")
    ch.setLevel(logging.INFO)

    # create formatter
    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)

    # add formatter to ch
    ch.setFormatter(formatter)
    logger = logging.getLogger(fname)

    # add ch to logger
    logger.addHandler(ch)
    return logger


if __name__ == '__main__':
    url = "http://baijiahao.baidu.com/s?id=1628513197633598970"
    print(clean_url(url))
