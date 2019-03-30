import requests
import cchardet

def downloader(url, timeout=10, headers=None, debug=False):
    # 默认返回str内容。URL链接的是图片等二进制内容时，注意调用时要设binary=True
    _headers = {
        "User-Agent": 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0)',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7'
    }
    if headers:
        _headers = headers

    try:
        r = requests.get(url, headers=_headers, timeout=timeout)

        encoding = cchardet.detect(r.content)['encoding']  # 探测文本编码格式
        html = r.content.decode(encoding)
    except Exception as e:
        msg = "failed download: {}".format(url)
        print(msg)
        html = None

    return html

if __name__ == "__main__":
    url = "http://www.baidu.com"
    html = downloader(url)
    print(html)