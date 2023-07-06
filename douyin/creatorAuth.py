import json
import random
import string
import time

import execjs
import requests
from requests.cookies import RequestsCookieJar


def cookie_str_to_dict(str_cookie: str, sep=';'):
    cookie = {}
    for c in str_cookie.split(sep):
        item = c.split('=')
        if len(item) >= 2:
            cookie[item[0].strip()] = item[1].strip()
        else:
            cookie[item[0]] = ''
    return cookie


def cookiejar_to_cookie_str(cookie_jar: RequestsCookieJar):
    cookies = []
    for k, v in cookie_jar.items():
        cookies.append(f'{k}={v}')
    return ';'.join(cookies)


def stringRandom(n, specs=False, vrange='letters,upper,lower,digit,punc'):
    if specs:
        s = vrange
    else:
        s = ''
        options = vrange.split(',')
        if 'letters' in options:
            s = s + string.ascii_letters
        if 'upper' in options:
            s = s + string.ascii_uppercase
        if 'lower' in options:
            s = s + string.ascii_lowercase
        if 'digit' in options:
            s = s + string.digits
        if 'punc' in options:
            s = s + string.punctuation
    return ''.join(random.choices(s, k=n))


class DyCreatorWebAuth:

    def __init__(self, cookie=None):
        self.ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        cookie = cookie or {
            'ttcid': stringRandom(34, vrange='lower,digit'),
            '_tea_utm_cache_2906': 'undefined',
        }
        if isinstance(cookie, str):
            cookie = cookie_str_to_dict(cookie)
        self.session = requests.session()
        self.session.cookies = requests.utils.cookiejar_from_dict(cookie, cookiejar=None, overwrite=True)

    @staticmethod
    def get_tracks(distance, _y):
        """
        生成滑动轨迹
        """
        tracks = []
        y, v, t, current = 0, 0, 1, 0

        mid = distance * 3 / 4
        exceed = random.randint(40, 90)
        z = random.randint(30, 150)

        while current < (distance + exceed):
            a = 2 if current < mid / 2 else (3 if current < mid else -3)
            a /= 2
            v0 = v
            s = v0 * t + 0.5 * a * (t * t)
            current += int(s)
            v = v0 + a * t

            y += random.randint(-3, 3)
            z = z + random.randint(5, 10)
            tracks.append([min(current, (distance + exceed)), y, z])

        while exceed > 0:
            exceed -= random.randint(0, 5)
            y += random.randint(-3, 3)
            z = z + random.randint(5, 9)
            tracks.append([min(current, (distance + exceed)), y, z])

        return [{'x': x[0], 'y': _y, 'relative_time': x[2]} for x in tracks]

    @staticmethod
    def get_slide_distance(slideUrl, backUrl):
        """
        计算滑块移动距离
        :param slideUrl: 
        :param backUrl: 
        :return: 
        """
        data = {
            "slideUrl": slideUrl,
            "backUrl": backUrl,
            "backWidth": "268",
            "backHeight": "150"
        }
        res = requests.post('https://qq2094274135/slide', json=data)
        result = res.json()
        print(f'预测滑动距离： {result}')
        return result.get('data')[0]

    @staticmethod
    def get_encrypt_mobile(phone_number):
        try:
            with open(r'qq2094274135\dysms.js', 'r', encoding='utf-8') as ge:
                ctx1 = execjs.compile(ge.read())
            mobile = ctx1.call('get_encrypt_mobile', phone_number)
            print(f'mobile = {mobile}')
            return mobile
        except Exception as e:
            print(f'Get encrypted mobile failed!{e}')
            return ''

    @staticmethod
    def get_s_v_web_id():
        try:
            with open(r'F:qq2094274135\dysms.js', 'r', encoding='utf-8') as ge:
                ctx1 = execjs.compile(ge.read())
            s_v_webid = ctx1.call('create_s_v_web_id')
            print(f's_v_webid = {s_v_webid}')
            s_v_webid = s_v_webid.replace('verify_', '')
            return s_v_webid
        except Exception as e:
            print(f'Get s_v_webid failed!{e}')
            return ''

    def get_sign(self, unsignedUrl):
        data = {
            "unsignedUrl": unsignedUrl,
            "referer": 'https://creator.douyin.com/',
            "userAgent": self.ua,
            "signMode": 2,
            "signKind": 2,
        }
        res = requests.post('https://qq2094274135/sign', json=data)
        return res.json().get('data')

    def _check_ttwid(self):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://creator.douyin.com',
            'Pragma': 'no-cache',
            'Referer': 'https://creator.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        data = '{"aid":2906,"service":"creator.douyin.com","region":"cn","needFid":false,"union":true,"fid":"","migrate_priority":0}'

        response = self.session.post('https://creator.douyin.com/ttwid/check/', headers=headers, data=data)
        result = response.json()
        print(f'检查ttwid: {result}')
        return result

    def _register_ttwid(self):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://creator.douyin.com',
            'Pragma': 'no-cache',
            'Referer': 'https://creator.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        data = '{"aid":2906,"service":"creator.douyin.com","region":"cn","needFid":false,"union":true,"fid":""}'

        response = self.session.post('https://ttwid.bytedance.com/ttwid/union/register/', headers=headers, data=data)
        result = response.json()
        print(f'注册ttwid: {result}')
        return result

    def _ttwid_register_callback(self, callback_url):
        s_v_webid = self.get_s_v_web_id()
        self.session.cookies.update({
            's_v_web_id': s_v_webid
        })
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://creator.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        response = self.session.get(
            callback_url,
            headers=headers,
        )
        result = response.json()
        print(f'注册ttwid回调: {result}')
        return result

    def get_ttwid(self):
        check_result = self._check_ttwid()
        if check_result.get('status_code') != 0:
            reg_result = self._register_ttwid()
            if reg_result.get('status_code') == 0:
                redirect_url = reg_result.get('redirect_url')
                callback_result = self._ttwid_register_callback(redirect_url)

    def get_qrcode(self):
        s_v_webid = self.session.cookies.get('s_v_web_id')
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://creator.douyin.com',
            'Pragma': 'no-cache',
            'Referer': 'https://creator.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        response = self.session.get(
            f'https://sso.douyin.com/get_qrcode/?next=https:%2F%2Fcreator.douyin.com%2Fcreator-micro%2Fhome&aid=2906&service=https:%2F%2Fcreator.douyin.com&is_vcd=1&fp={s_v_webid}',
            headers=headers,
        )
        result = response.json()
        print(f'获取登陆验证码: {result}')
        return result

    def check_qrconnect(self, token):
        s_v_webid = self.session.cookies.get('s_v_web_id')
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://creator.douyin.com',
            'Pragma': 'no-cache',
            'Referer': 'https://creator.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        response = self.session.get(
            f'https://sso.douyin.com/check_qrconnect/?next=https:%2F%2Fcreator.douyin.com%2Fcreator-micro%2Fhome&token={token}&service=https:%2F%2Fcreator.douyin.com%2F%3Flogintype%3Duser%26loginapp%3Ddouyin%26jump%3Dhttps:%2F%2Fcreator.douyin.com%2Fcreator-micro%2Fhome&correct_service=https:%2F%2Fcreator.douyin.com%2F%3Flogintype%3Duser%26loginapp%3Ddouyin%26jump%3Dhttps:%2F%2Fcreator.douyin.com%2Fcreator-micro%2Fhome&aid=2906&is_vcd=1&fp={s_v_webid}',
            headers=headers,
        )
        result = response.json()
        print(f'检查qrconnect: {result}')
        return result

    def send_activate_code(self, mobile):
        s_v_webid = self.session.cookies.get('s_v_web_id')
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://creator.douyin.com',
            'Pragma': 'no-cache',
            'Referer': 'https://creator.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        url = f'https://sso.douyin.com/send_activation_code/v2/?mobile=%2B86{mobile}&type=24&is6Digits=1&aid=2906&service=https:%2F%2Fcreator.douyin.com&is_vcd=1&fp={s_v_webid}'
        sign_info = self.get_sign(url)
        signed_url = sign_info.get('signedUrl')
        print(signed_url)
        response = self.session.get(
            signed_url,
            headers=headers,
        )
        result = response.json()
        print(f'发送验证码: {result}')
        return result

    def get_slide_code(self):
        s_v_webid = self.session.cookies.get('s_v_web_id')
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://creator.douyin.com',
            'Pragma': 'no-cache',
            'Referer': 'https://creator.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        params = {
            'external': '',
            'fp': s_v_webid,
            'aid': '2906',
            'lang': 'zh',
            'app_name': 'aweme',
            'iid': '0',
            'vc': '1.0',
            'did': '0',
            'uid': '0',
            'ch': 'pc_slide',
            'os': '2',
            'challenge_code': '1105',
            'time': int(time.time() * 1000),
        }

        response = self.session.get('https://verify.snssdk.com/get', params=params, headers=headers)
        result = response.json()
        print(f'滑块验证码: {result}')
        return result

    def verify_slide_code(self, code_id, slide_url, back_url):
        s_v_webid = self.session.cookies.get('s_v_web_id')
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://creator.douyin.com',
            'Pragma': 'no-cache',
            'Referer': 'https://creator.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        params = {
            'os_name': 'windows',
            'platform': 'pc',
            'webdriver': 'false',
            'external': '',
            'fp': s_v_webid,
            'aid': '2906',
            'lang': 'zh',
            'app_name': 'aweme',
            'iid': '0',
            'vc': '1.0',
            'did': '0',
            'uid': '0',
            'ch': 'pc_slide',
            'os': '2',
            'challenge_code': '1105',
        }
        slide_distance = self.get_slide_distance(slide_url, back_url)
        reply = self.get_tracks(slide_distance, 65)
        x = {"x": 274.2179260253906, "y": 233.54348754882812, "time": int(time.time()*1000)}
        y = {"x": 70.21792602539062, "y": 275.5434875488281, "time": int(time.time()*1000)}
        z = [
            {"x": 263.2179260253906, "y": 240.54348754882812},
            {"x": 240.21792602539062, "y": 250.54348754882812},
            {"x": 218.21792602539062, "y": 259.5434875488281},
            {"x": 203.21792602539062, "y": 266.5434875488281},
            {"x": 193.21792602539062, "y": 270.5434875488281},
            {"x": 186.21792602539062, "y": 272.5434875488281},
            {"x": 171.21792602539062, "y": 275.5434875488281},
            {"x": 147.21792602539062, "y": 275.5434875488281},
            {"x": 120.21792602539062, "y": 275.5434875488281},
            {"x": 95.21792602539062, "y": 275.5434875488281},
            {"x": 78.21792602539062, "y": 275.5434875488281},
            {"x": 66.21792602539062, "y": 275.5434875488281},
            {"x": 56.217926025390625, "y": 273.5434875488281},
            {"x": 48.217926025390625, "y": 268.5434875488281},
            {"x": 45.217926025390625, "y": 263.5434875488281},
            {"x": 45.217926025390625, "y": 259.5434875488281},
            {"x": 56.217926025390625, "y": 259.5434875488281},
            {"x": 73.21792602539062, "y": 261.5434875488281},
            {"x": 96.21792602539062, "y": 266.5434875488281},
            {"x": 117.21792602539062, "y": 266.5434875488281},
            {"x": 130.21792602539062, "y": 266.5434875488281},
            {"x": 146.21792602539062, "y": 266.5434875488281},
            {"x": 155.21792602539062, "y": 266.5434875488281},
            {"x": 161.21792602539062, "y": 266.5434875488281},
            {"x": 166.21792602539062, "y": 266.5434875488281},
            {"x": 171.21792602539062, "y": 266.5434875488281},
            {"x": 177.21792602539062, "y": 266.5434875488281},
            {"x": 183.21792602539062, "y": 266.5434875488281},
            {"x": 188.21792602539062, "y": 266.5434875488281},
            {"x": 195.21792602539062, "y": 266.5434875488281},
            {"x": 200.21792602539062, "y": 266.5434875488281}
        ]
        for i in z:
            i['time'] = int(time.time()*1000)
            time.sleep(random.randint(10, 100)/1000)
        m = [
            {"x": 44.218, "y": 259.543},
            {"x": 45.218, "y": 259.543},
            {"x": 47.218, "y": 259.543},
            {"x": 48.218, "y": 259.543},
            {"x": 50.218, "y": 259.543},
            {"x": 53.218, "y": 259.543},
            {"x": 56.218, "y": 259.543},
            {"x": 58.218, "y": 261.543},
            {"x": 60.218, "y": 261.543},
            {"x": 64.218, "y": 261.543},
            {"x": 69.218, "y": 261.543},
            {"x": 73.218, "y": 261.543},
            {"x": 77.218, "y": 262.543},
            {"x": 81.218, "y": 262.543},
            {"x": 88.218, "y": 266.543},
            {"x": 90.218, "y": 266.543},
            {"x": 96.218, "y": 266.543},
            {"x": 99.218, "y": 266.543},
            {"x": 104.218, "y": 266.543},
            {"x": 107.218, "y": 266.543},
            {"x": 114.218, "y": 266.543},
            {"x": 117.218, "y": 266.543},
            {"x": 118.218, "y": 266.543},
            {"x": 121.218, "y": 266.543},
            {"x": 125.218, "y": 266.543},
            {"x": 127.218, "y": 266.543},
            {"x": 130.218, "y": 266.543},
            {"x": 138.218, "y": 266.543},
            {"x": 140.218, "y": 266.543},
            {"x": 143.218, "y": 266.543},
            {"x": 146.218, "y": 266.543},
            {"x": 146.218, "y": 266.543},
            {"x": 148.218, "y": 266.543},
            {"x": 150.218, "y": 266.543},
            {"x": 153.218, "y": 266.543},
            {"x": 154.218, "y": 266.543},
            {"x": 155.218, "y": 266.543},
            {"x": 156.218, "y": 266.543},
            {"x": 157.218, "y": 266.543},
            {"x": 159.218, "y": 266.543},
            {"x": 160.218, "y": 266.543},
            {"x": 161.218, "y": 266.543},
            {"x": 163.218, "y": 266.543},
            {"x": 163.218, "y": 266.543},
            {"x": 164.218, "y": 266.543},
            {"x": 165.218, "y": 266.543},
            {"x": 166.218, "y": 266.543},
            {"x": 167.218, "y": 266.543},
            {"x": 168.218, "y": 266.543},
            {"x": 169.218, "y": 266.543},
            {"x": 170.218, "y": 266.543},
            {"x": 171.218, "y": 266.543},
            {"x": 173.218, "y": 266.543},
            {"x": 174.218, "y": 266.543},
            {"x": 175.218, "y": 266.543},
            {"x": 176.218, "y": 266.543},
            {"x": 177.218, "y": 266.543},
            {"x": 178.218, "y": 266.543},
            {"x": 179.218, "y": 266.543},
            {"x": 180.218, "y": 266.543},
            {"x": 181.218, "y": 266.543},
            {"x": 183.218, "y": 266.543},
            {"x": 184.218, "y": 266.543},
            {"x": 185.218, "y": 266.543},
            {"x": 186.218, "y": 266.543},
            {"x": 187.218, "y": 266.543},
            {"x": 188.218, "y": 266.543},
            {"x": 189.218, "y": 266.543},
            {"x": 191.218, "y": 266.543},
            {"x": 193.218, "y": 266.543},
            {"x": 194.218, "y": 266.543},
            {"x": 195.218, "y": 266.543},
            {"x": 196.218, "y": 266.543},
            {"x": 197.218, "y": 266.543},
            {"x": 199.218, "y": 266.543},
            {"x": 199.218, "y": 266.543},
            {"x": 200.218, "y": 266.543},
            {"x": 201.218, "y": 266.543},
            {"x": 201.218, "y": 266.543},
            {"x": 203.218, "y": 265.543}
        ]
        for i in m:
            i['time'] = int(time.time()*1000)
            time.sleep(random.randint(10, 100)/1000)

        data = json.dumps({"modified_img_width": 268, "id": code_id, "mode": "slide",
                           "reply": reply, "webdriver": "false",
                           "cid": code_id, "os_name": "windows", "platform": "pc",
                           "models": {"x": x,
                                      "y": y,
                                      "z": z,
                                      "t": [],
                                      "m": m}
                           })

        response = self.session.post('https://verify.snssdk.com/verify', params=params, headers=headers, data=data)
        result = response.json()
        print(f'滑块验证结果: {result}')
        return result

    def quick_login(self, mobile, code):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://creator.douyin.com',
            'Pragma': 'no-cache',
            'Referer': 'https://creator.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': self.ua,
            'X-CSRFToken': 'null',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        encrypt_mobile = self.get_encrypt_mobile(f'+86 {mobile}')
        encrypt_code = self.get_encrypt_mobile(code)
        data = {
            'mobile': encrypt_mobile,
            'code': encrypt_code,
            'service': 'https://creator.douyin.com/?logintype=user&loginapp=douyin&jump=https://creator.douyin.com/',
            'aid': '2906',
            'mix_mode': '1',
            'is_vcd': '1',
            'fp': 'ljnnoijr_9guYqq2U_GY50_4jVx_8gL8_CitkaY5arl5G',
        }

        response = self.session.post('https://sso.douyin.com/quick_login/v2/', headers=headers, data=data)
        result = response.json()
        print(f'登陆结果: {result}')
        return result

    def login_and_get_cookie(self, url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://creator.douyin.com/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        response = self.session.get(url, headers=headers)
        if 'sessionid' not in self.session.cookies:
            raise Exception('获取cookie失败')
        return cookiejar_to_cookie_str(self.session.cookies)

    def auth(self):
        self.get_ttwid()
        print(self.session.cookies)
        qr_result = self.get_qrcode()
        token = qr_result.get('data').get('token')
        check_result = self.check_qrconnect(token)
        mobile = input('输入手机号码：')
        for _ in range(3):
            send_result = self.send_activate_code(mobile)
            if send_result.get('error_code') == 1105:
                verify_conf = json.loads(send_result.get('verify_center_decision_conf'))
                detail = verify_conf.get('detail')
                for _ in range(5):
                    get_slide_result = self.get_slide_code()
                    code_id = get_slide_result.get('data').get('id')
                    back_url = get_slide_result.get('data').get('question').get('url1')
                    front_url = get_slide_result.get('data').get('question').get('url2')
                    verify_result = self.verify_slide_code(code_id, front_url, back_url)
                    if verify_result and verify_result.get('msg_type') == 'success':
                        break
                    time.sleep(random.randint(1, 3))
                else:
                    raise Exception('滑块验证失败')
                send_result = self.send_activate_code(mobile)
            if send_result.get('error_code') == 0:
                print('sms验证通过')
                sms_code = input('请输入短信验证码：')
                login_result = self.quick_login(mobile, sms_code)
                if login_result and login_result.get('error_code') == 0:
                    redirect_url = login_result.get('redirect_url')
                    return self.login_and_get_cookie(redirect_url)
            time.sleep(random.randint(1, 3))
            print('sms验证失败，请重试！')


if __name__ == '__main__':
    cauth = DyCreatorWebAuth()
    print(cauth.auth())