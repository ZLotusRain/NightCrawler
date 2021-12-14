import time
import requests
from requests.utils import cookiejar_from_dict


def ntes_set_cookie_long(a, c):
    ts = str(time.time()).replace(".", "")[:13]
    ts = int(ts) + 1e3 * 60 * 60 * 24 * 365 * 100


url = "https://music.163.com/weapi/comment/resource/comments/get?csrf_token="
nmtid_url = "https://music.163.com/weapi/resource-exposure/config/batch?csrf_token="
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/96.0.4664.45 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
    # "Referer": "https://music.163.com/song?id=1900998233",
    "Host": "music.163.com",
    "Origin": "https://music.163.com"
}
cookies = {
    "JSESSIONID-WYYY": "RikXNY1EVslxWrGD%5C2q%5CfkDlblQwIFz0oiGj7%2FCX1lJiQgagsu1gdQ4HOi4PVkNa03OyEGfEXYxzSxq4ACsGJmzD2R"
                       "6unqolOC8XhRrHfpcxepynSM%5CaWd1iYFjDHrXe6MBUyR6d2%2FycHUZ%5Czk5%2B2X8z5MQ6MHFzIIjNBtxNpFeonAik%3"
                       "A1639130893370",
    "_iuqxldmzr_": 32,
    "_ntes_nnid": f'd84fa15c258db1f775e53d797096fdfa,{str(time.time()).replace(".", "")[:13]}',
    "_ntes_nuid": "d84fa15c258db1f775e53d797096fdfa"
}
cookies_res = ";".join([f"{key}={cookies[key]}" for key in cookies])
headers["Cookie"] = cookies_res
nmtid_body = "params=yr%2FjOeeE5eC9NseK9ynkAqnuWIFeWwk2%2F%2FeI%2BhQh3Hhr2OWIx1d6qppxBRjIGDvueHR%2BIILLkfjoxjWdhrHUJR%2FPrJ1uWXSr2HsuXsuyeIeoLAPtxll1yw3Nl4AxPGdd&encSecKey=86088e105685e8686da14bec4da9387abf980f85928e2ee0f885c60b36d7a8da986c98aac0ff58035341a458f0e40649cd2f12730332a79c3a28f6021a3528e58572b8663a84aed014700e712baad7b16ecec672feccd3060eee7f7f75b17ce40950c0aaf1e3ed5f7081dfdf5fb2af39c9de33586cdc8e3af45c0dc470d792be"
nmtid_response = requests.post(url=nmtid_url, headers=headers, data=nmtid_body, verify=False)


body = "params=vV2QKlGo7oJF56xhvnboHDyGdW1rtxIECF9xClLn9sLHdixRH8buGhtDBiy2JGqn0m%2BNn6MUH8lseLUbhaT57m3n%2F4PGdCo7aRORXhbCn8tZ023%2Bp5DJP%2B%2FcNHrGOSMrxp%2FnUG6QO7E2CYSHOocRgjNO3m%2BSZWKVZbzvZ1RYgUdPN7%2BwXnEJLBDhwLSV%2FqjW7h9ZODrZ7MOjMPq2Zk%2FdIxhI8tNVb6MMHFqwldp7S1dXjDG28FS%2BROGSOWczFFktzBeJSrOp7rM63rn0BphzzcQCXR5ZIUoigfImU75tvj4%3D&encSecKey=b100a1c9c94a5f4075bff8ad81acd9f2635a0f3aeed42019977334b718214d40b8d5cbe0e3112ef89c65d18dc69fd71e717ae2632a041f99492b70cf280c2e04be24ec46121b674f9dc7753ca42257dd4fba30898d8f9a04a97b2645b3c99a4fad069f201e65800bf7df130d7a77f56d8bb263ae5c494c2806600c9a8524970e"
# body = {
#     "encText": 'Ik+pMoJnTRwcgyD6e7l/RJjS1ZHm+aKaQM5eBVHhnTFXxLj7RqYdO8rl7+CFzpm+So419TvAor0RjYqCXxj+PTBBzn77oqAbsk8b7bcB6RvkS2ayvR3AjOdNv0Bx2j896P+gNGeqynAB70Zl7UTIWPAGeX6JV0AoR9NS6mQ8eNPDM05pfMRgV3Yv3XzgpT/ZlHzdMvEp6X9jDoAuYZCE6fAc28V9XpDLJMhA8ghKk/oFp0WeExi7IWj0+C1BUFgrJof3hEB2AAPYiPWnjaSsCdG4p48c2/xh2N+9/WcXhLA=',
#     "encSecKey": '6c5ef9b7c992484f7a3dda7affd1d7860ce1de70bfd083542f4b3aaf80841ad60890fcd75712029883e248c55b1f07cfd978fd74bedb27169d0ce794896627dcd811a7ec51ed4cddd3499a28de4498f657c7d3f42a99fa14d902007ece645739f327a1ba7da538b7a4850a07b2053a4ab932e6fa9587279ae5c25289a4f2b55c'
# }

cookies["NMTID"] = nmtid_response.cookies.get("NMTID")
cookies_res = ";".join([f"{key}={cookies[key]}" for key in cookies])
headers["Cookie"] = cookies_res
response = requests.post(url=url, headers=headers, data=body, verify=False)
print(response.text)