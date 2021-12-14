import re
import time
import base64
import execjs
import urllib3
import logging
import requests
import cchardet
import requests.utils
from urllib3.util import parse_url
from Crypto.Cipher import AES, DES
from binascii import b2a_hex, a2b_hex
from Crypto.Util.Padding import pad, unpad


class TryRequestException(Exception):
    def __init__(self, method, url, **kwargs):
        self.url = url
        self.method = method
        self.headers = kwargs.pop("headers", None)
        self.cookies = kwargs.pop("cookies", None)
        self.params = kwargs.pop("params", None)
        self.data = kwargs.pop("data", None)
        self.json = kwargs.pop("json", None)

    def __str__(self):
        return f"{self.method} <{self.url}> failed!"


class Explorer:
    def __init__(self, target=None, proxy_params=None, tunnel_proxy=None):
        self.target = target

        default_proxy_params = {
            "proxy_type": "taiyang",
            "user": "nacao",
            "switch_type": ("http", "qy")
        }
        self.proxy_params = proxy_params or default_proxy_params
        self.tunnel_proxy = tunnel_proxy

        self.proxy_result = {}
        self.oss_auth = None

    @staticmethod
    def parse_url_params(url=None, query=None):
        params = {}

        query = query or parse_url(url).query or ""
        query = query.split("&")
        for each in query:
            if "=" not in each:
                continue
            key, value = each.split("=", maxsplit=1)
            params[key] = value

        return params

    @staticmethod
    def parse_url_host(url):
        host = ""
        try:
            host = parse_url(url).host
            port = parse_url(url).port
            host = f"{host}:{port}" if port else host
        except urllib3.exceptions.LocationParseError as e:
            logging.error(f">>> url解析失败[{e}]: {url}")
        return host or ""

    def try_request(self, url, method="GET", session=None, use_proxy=0, sleep_time=None, retry_times=3, **kwargs):
        """same kwargs as <requests.request>."""

        kwargs["headers"] = kwargs.get("headers") or {}
        kwargs["timeout"] = kwargs.get("timeout", 10)
        kwargs["allow_redirects"] = kwargs.get("allow_redirects", False)
        kwargs["verify"] = kwargs.get("verify", False)

        for _ in range(retry_times):
            kwargs["proxies"] = kwargs.get("proxies")
            if use_proxy == 1:
                if self.tunnel_proxy:
                    kwargs["proxies"] = self.tunnel_proxy
                else:
                    pass
                    # self.build_proxy()
                    # proxies = copy.copy(self.proxy_result["proxy_dict"])
                    # kwargs["proxies"] = proxies

            response = None
            try:
                module = session or requests
                response = module.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except requests.exceptions.InvalidURL as e:
                logging.exception(f">>> 无效的url[{e}]: {url}")
                break
            except requests.HTTPError as e:
                logging.error(f">>> 非法的状态码[{e.response.status_code}]: {url}")
                # 中国政府采购网404是因为代理问题
                # if e.response.status_code == 404:
                #     break
                if e.response.status_code in [429, 503]:
                    time.sleep(2.5)
                if e.response.status_code in [400, 521]:
                    return response
            except requests.exceptions.ProxyError as e:
                logging.error(f">>> 代理请求失败[{e}]: {url}")
            except requests.exceptions.ReadTimeout as e:
                logging.error(f">>> 请求超时[{e}]: {url}")
            except requests.exceptions.ConnectionError as e:
                logging.error(f">>> 连接错误[{e}]: {url}")
            except requests.RequestException:
                logging.exception(f">>> 请求url失败, 重试中: {url}")
            # except httpx.RequestError as e:
            #     logging.error(f">>> httpx模式请求url失败, 重试中[{e}]: {url}")
            except UnicodeError as e:
                logging.error(f">>> 编码错误[{e}]: {url}")
                break
            except Exception as e:
                logging.exception(f">>> 未知异常[{e}]: {url}")
                break
            self.proxy_result = {}
            if response:
                response.close()
            if sleep_time:
                time.sleep(sleep_time)
        raise TryRequestException(method, url, **kwargs)

    @staticmethod
    def decode_resp_content(response, encoding=None):
        response_text = ""
        if response is None:
            return response_text
        # encoding_method = encoding or response.apparent_encoding or "utf-8"
        try:
            content = response.content  # requests.RequestException
            encoding_method = encoding or cchardet.detect(content)["encoding"] or "utf-8"
            response_text = content.decode(encoding_method, errors="replace")
        except Exception as e:
            logging.exception(f">>> 解析content编码失败[{e}]")
            response_text = ""
        return response_text

    @staticmethod
    def get_content_length(headers):
        content_length = headers.get("Content-Length") or headers.get("Content-length") or headers.get("content-length")
        return int(content_length) if isinstance(content_length, str) and content_length.isdigit() else content_length

    @staticmethod
    def get_content_disposition(headers):
        return headers.get("Content-Disposition") or headers.get("Content-disposition") or headers.get("content-disposition")

    @staticmethod
    def get_pre_jsl_cookie(response_text):
        cookie_jar = None
        try:
            js_codes = re.findall("document.cookie=(.*?);location", response_text)
            if js_codes:
                cookie_dict = {}
                cookies = execjs.eval(js_codes[0])
                for each in cookies.split(";"):
                    k, v = each.split("=", maxsplit=1)
                    cookie_dict[k] = v
                cookie_jar = requests.utils.cookiejar_from_dict(cookie_dict)
        except Exception as e:
            logging.exception(f">>> 获取__jsl_clearance失败: {e}")
        return cookie_jar

    def get_jsl_clearance_cookie(self, response_text):
        js_codes = response_text.replace("<script>", "").replace("</script>", "").replace("\0", "")
        if js_codes.find('"vt":"3600"'):
            go_params = re.findall(r";go\((.*?)\)", js_codes)
            body = go_params[0] if go_params else ""
        else:
            if js_codes.endswith("return x["):
                js_codes += "f(y, z) - 1]}));"
            elif js_codes.endswith(";</"):
                js_codes = js_codes.replace(";</", ";")
            body = js_codes
        api = "http://spider-session-encryptor.ms2.qixin.com/?domain_url=http://www.gsxt.gov.cn/"
        headers = {
            "Content-Type": "text/html;charset=utf-8",
        }
        try:
            response = self.try_request(method="POST", url=api, headers=headers, data=body)
            result = response.text
            print(result)
        except TryRequestException:
            logging.error(f">>> 接口获取__jsl_clearance失败")

    @staticmethod
    def encrypt(source, key, method, mode="ECB", iv=None, block_size=16, style="pkcs7", encoding="base64"):
        if not isinstance(source, bytes):
            source = source.encode("utf-8")
        if not isinstance(key, bytes):
            key = key.encode("utf-8")
        if iv and not isinstance(iv, bytes):
            iv = iv.encode("utf-8")

        generator = None
        result = ""
        try:
            if method == "AES":
                if mode == "ECB":
                    generator = AES.new(key, AES.MODE_ECB)
                elif mode == "CBC":
                    generator = AES.new(key, AES.MODE_CBC, iv)
            elif method == "DES":
                if mode == "ECB":
                    generator = DES.new(key, DES.MODE_ECB)  # 创建一个aes对象
                elif mode == "CBC":
                    generator = DES.new(key, DES.MODE_CBC, iv)
            if not generator:
                return result
            result = generator.encrypt(pad(source, block_size, style))  # 加密明文
            if encoding == "base64":
                result = base64.b64encode(result)  # 将返回的字节型数据转进行base64编码
                result = result.decode("utf-8")  # 将字节型数据转换成python中的字符串类型
            else:
                result = b2a_hex(result).decode()
                # result = result.hex()
        except ValueError as e:
            logging.error(f">>> {method}加密失败[{e}]")
        return result

    @staticmethod
    def decrypt(source, key, method, mode="ECB", iv=None, block_size=16, style="pkcs7", encoding="base64"):
        if not isinstance(source, bytes):
            if encoding == "base64":
                source = source.encode("utf-8")
                source = base64.b64decode(source)
            else:
                source = a2b_hex(source)
        if not isinstance(key, bytes):
            key = key.encode("utf-8")
        if iv and not isinstance(iv, bytes):
            iv = iv.encode("utf-8")

        generator = None
        result = ""
        try:
            if method == "AES":
                if mode == "ECB":
                    generator = AES.new(key, AES.MODE_ECB)
                elif mode == "CBC":
                    generator = AES.new(key, AES.MODE_CBC, iv)
            elif method == "DES":
                if mode == "ECB":
                    generator = DES.new(key, DES.MODE_ECB)  # 创建一个aes对象
                elif mode == "CBC":
                    generator = DES.new(key, DES.MODE_CBC, iv)
            if not generator:
                return result
            result = generator.decrypt(source)  # 解密
            result = unpad(result, block_size, style)
            result = result.decode("utf-8")
        except ValueError as e:
            logging.error(f">>> {method}加密失败[{e}]")
        return result

    def draw_ext_from_headers(self, headers):
        ext_name = ""
        content_disposition = self.get_content_disposition(headers)
        if content_disposition:
            filename = list(filter(lambda x: "filename=" in x or "fileName" in x, content_disposition.split(";")))
            filename = filename[0] if filename else ""
            ext_name = filename.split(".")[-1].strip('"').strip("'")
        else:
            content_type = headers.get("Content-Type", "")
            maybe_ext_name = list(filter(lambda x: x.startswith("."), content_type.split(";")))
            if maybe_ext_name:
                ext_name = maybe_ext_name[0].split(".")[-1]
            elif "application/msword" in content_type:
                ext_name = "doc"
            elif "application/ms-download" in content_type:
                ext_name = "pdf"
            elif "application/" in content_type:
                ext_name = list(filter(lambda x: "application/" in x, content_type.split(";")))[0].split("/")[-1]
        return ext_name
