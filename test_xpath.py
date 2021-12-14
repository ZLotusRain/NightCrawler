import requests
import logging
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Host": "www.plap.cn",
}
response = requests.get(url="https://www.plap.cn/index/selectArticleNewsById.html?id=C2A2DD31275F40B5B9D5467BC284F569", headers=headers, verify=False)
response.text
print(response.text)