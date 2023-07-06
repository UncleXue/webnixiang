import base64
import random
import time

import execjs
import requests
import cv2
import numpy as np
from threading import Thread


def cookie_str_to_dict(str_cookie: str, sep=';'):
    cookie = {}
    for c in str_cookie.split(sep):
        item = c.split('=')
        if len(item) >= 2:
            cookie[item[0].strip()] = item[1].strip()
        else:
            cookie[item[0]] = ''
    return cookie


class DyWebAuth:

    def __init__(self, cookie=None):
        self.ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        cookie = cookie or {}
        if isinstance(cookie, str):
            cookie = cookie_str_to_dict(cookie)
        self.session = requests.session()
        self.session.cookies = requests.utils.cookiejar_from_dict(cookie, cookiejar=None, overwrite=True)
        self.verifyFp = self.get_verify_fp()

    def show_qrcode(self, qr_bs64):
        img_data = base64.b64decode(qr_bs64)
        img_array = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)
        cv2.imshow('Qr code', img)
        cv2.waitKey()
        cv2.destroyAllWindows()

    def get_signature(self, unsignedUrl, ac_nounce=None):
        url = 'https://qq2094274135/sign'
        data = {
            "unsignedUrl": unsignedUrl,
            "referer": "https://www.douyin.com/",
            "userAgent": self.ua,
            "acNounce": ac_nounce
        }
        r = requests.post(url, json=data)
        result = r.json()
        return result.get('data')

    def get_verify_fp(self):
        url = 'https://qq2094274135/verifyFp'
        r = requests.get(url)
        result = r.json()
        return result.get('data')

    def open_douyin(self):
        headers = {
            'Host': 'www.douyin.com',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': self.ua,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        url = 'https://www.douyin.com/'
        for i in range(2):
            response = self.session.get(url, headers=headers)
            ac_nounce = self.session.cookies.get('__ac_nonce')
            print('__ac_nonce', ac_nounce)
            ttwid = self.session.cookies.get('ttwid')
            print('ttwid', ttwid)
            if ttwid:
                break
            ac_signature = self.get_signature(url, ac_nounce).get('ac_signature')
            # time.sleep(1)
            self.session.cookies.update({
                '__ac_signature': ac_signature,
                '__ac_referer': '__ac_blank',
            })
            headers['Referer'] = 'https://www.douyin.com/'
            headers['Sec-Fetch-Site'] = 'same-origin'
        if not self.session.cookies.get('ttwid'):
            raise Exception('获取ttwid失败')

    def check_login(self):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Origin': 'https://www.douyin.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        response = self.session.get(
            'https://sso.douyin.com/check_login/?service=https:%2F%2Fwww.douyin.com&aid=6383&account_sdk_source=sso&language=zh&sdk_version=2.1.3',
            headers=headers,
        )
        print(f'检查登陆： {response.json()}')
        print(self.session.cookies.get('passport_csrf_token'))

    def get_qr_code(self):
        csrf_token = self.session.cookies.get('passport_csrf_token')
        msToken = self.session.cookies.get('msToken')
        headers = {
            'Accept': 'application/json, text/javascript',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.douyin.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-tt-passport-csrf-token': csrf_token,
        }
        url = f'https://sso.douyin.com/get_qrcode/?service=https%3A%2F%2Fwww.douyin.com&need_logo=false&need_short_url=false&device_platform=web_app&aid=6383&account_sdk_source=sso&sdk_version=2.2.5&language=zh&verifyFp={self.verifyFp}&fp={self.verifyFp}&msToken={msToken}'
        x_bogus = self.get_signature(url).get('x_bogus')
        print('x-bogus', x_bogus)
        url = url + f'&X-Bogus={x_bogus}'
        response = self.session.get(
            url,
            headers=headers,
        )
        result = response.json()
        return result

    def check_qr_code(self, token):
        csrf_token = self.session.cookies.get('passport_csrf_token')
        headers = {
            'Accept': 'application/json, text/javascript',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.douyin.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-tt-passport-csrf-token': csrf_token,
        }
        frontier = 'true'
        while True:
            msToken = self.session.cookies.get('msToken')
            url = f'https://sso.douyin.com/check_qrconnect/?service=https%3A%2F%2Fwww.douyin.com&token={token}&need_logo=false&is_frontier={frontier}&need_short_url=false&device_platform=web_app&aid=6383&account_sdk_source=sso&sdk_version=2.2.5&language=zh&verifyFp={self.verifyFp}&fp={self.verifyFp}&msToken={msToken}'
            x_bogus = self.get_signature(url).get('x_bogus')
            print('x-bogus', x_bogus)
            url = url + f'&X-Bogus={x_bogus}'
            response = self.session.get(
                url,
                headers=headers,
            )
            result = response.json()
            if result.get('data', {}).get('status') == '1':
                print(f'等待扫码：{result}')
                time.sleep(5)
            elif result.get('data', {}).get('status') == '2':
                print(f'等待确认：{result}')
                frontier = 'true'
                time.sleep(1)
            elif result.get('data', {}).get('status') == '3':
                print(f'扫码成功：{result}')
                return result
            elif result.get('data', {}).get('status') == '5':
                print(f'状态异常： {result}')
                print(f'新二维码： {result.get("data").get("qrcode")}')
                time.sleep(30)
            else:
                print(f'状态异常： {result}')
                time.sleep(30)

    def login(self, url):
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://www.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        response = self.session.get(url, headers=headers)
        if response.status_code == 302:
            location = response.headers.get('Location')
            print(f'跳转： {location}')

            headers = {
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Pragma': 'no-cache',
                'Referer': 'https://www.douyin.com/',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': self.ua,
                'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            response = self.session.get(location, headers=headers)
            if response.status_code == 302:
                location = response.headers.get('Location')
                print(f'跳转2： {location}')

                headers = {
                    'Host': 'www.douyin.com',
                    'Connection': 'keep-alive',
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache',
                    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                    'Accept': 'application/json, text/plain, */*',
                    'sec-ch-ua-mobile': '?0',
                    'User-Agent': self.ua,
                    'sec-ch-ua-platform': '"Windows"',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Dest': 'empty',
                    'Referer': 'https://www.douyin.com/',
                    # 'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                }

                response = self.session.get(location, headers=headers)
                if response.status_code == 200:
                    print('登陆成功')
                    return self.cookiejar2cookiestr()
            else:
                print('登陆失败！')
        elif response.status_code == 200:
            print(f'最终地址： {response.url}')
            print(f'设置cooKie： {response.cookies}')
            print(f'登陆成功: {self.session.cookies}')
            return self.cookiejar2cookiestr()

    def cookiejar2cookiestr(self):
        cookies = []
        for k, v in self.session.cookies.items():
            cookies.append(f'{k}={v}')
        return ';'.join(cookies)

    def auth(self):
        self.open_douyin()
        self.check_login()
        qr_info = self.get_qr_code()
        token = qr_info.get('data').get('token')
        qr_code = qr_info.get('data').get('qrcode')
        print(f'二维码： {qr_code}')
        show_code_thread = Thread(target=self.show_qrcode, args=(qr_code, ), daemon=True)
        show_code_thread.start()
        result = self.check_qr_code(token)
        login_url = result.get('data').get('redirect_url')
        cookie = self.login(login_url)
        print(f'获取cookie结果： {cookie}')


class DySmsAuth(DyWebAuth):

    @staticmethod
    def get_encrypt_mobile(phone_number):
        try:
            with open(r'F:\xhbproject\PlaywrightTest\js\dysms.js', 'r', encoding='utf-8') as ge:
                ctx1 = execjs.compile(ge.read())
            mobile = ctx1.call('get_encrypt_mobile', phone_number)
            print(f'mobile = {mobile}')
            return mobile
        except Exception as e:
            print(f'Get encrypted mobile failed!{e}')
            return ''

    def send_activate_code(self, phone_number):
        csrf_token = self.session.cookies.get('passport_csrf_token')
        headers = {
            'Accept': 'application/json, text/javascript',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.douyin.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-tt-passport-csrf-token': csrf_token,
        }
        mobile = self.get_encrypt_mobile(f'+86 {phone_number}')
        data = {
            'mix_mode': '1',
            'mobile': mobile,
            'type': '3731',
            'is6Digits': '1',
            'fixed_mix_mode': '1',
        }

        msToken = self.session.cookies.get('msToken')
        url = f'https://sso.douyin.com/send_activation_code/v2/?device_platform=web_app&aid=6383&account_sdk_source=sso&sdk_version=2.2.5&language=zh&verifyFp={self.verifyFp}&fp={self.verifyFp}&msToken={msToken}'
        x_bogus = self.get_signature(url).get('x_bogus')
        print('x-bogus', x_bogus)
        url = url + f'&X-Bogus={x_bogus}'

        response = self.session.post(
            url,
            headers=headers,
            data=data,
        )
        result = response.json()
        print(f'发送验证码： {result}')
        return result

    def get_capcha(self, detail):
        headers = {
            'Host': 'verify.zijieapi.com',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'Accept': 'application/json, text/plain, */*',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': self.ua,
            'sec-ch-ua-platform': '"Windows"',
            'Origin': 'https://www.douyin.com',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.douyin.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        tmp = int(time.time() * 1000)
        msToken = self.session.cookies.get('msToken')
        url = f'https://verify.zijieapi.com/captcha/get?lang=zh&app_name=%%E6%%8A%%96%%E9%%9F%%B3+Web+%%E7%%AB%%99&h5_sdk_version=2.28.9&h5_sdk_use_type=cdn&sdk_version=3.8.6&iid=0&did=0&device_id=0&ch=web_text&aid=6383&os_type=2&mode=&tmp={tmp}&platform=pc&webdriver=false&fp={self.verifyFp}&type=verify&detail={detail}&server_sdk_env=%%7B%%22idc%%22:%%22lf%%22,%%22region%%22:%%22CN%%22,%%22server_type%%22:%%22passport%%22%%7D&subtype=slide&challenge_code=3058&os_name=windows&h5_check_version=3.8.6&msToken={msToken}'
        x_bogus = self.get_signature(url).get('x_bogus')
        print('x-bogus', x_bogus)
        url = url + f'&X-Bogus={x_bogus}'
        response = self.session.get(
            url,
            headers=headers,
            verify=False,
        )

        result = response.json()
        print(f'captcha: {result}')
        return result

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

    def captcha_verify(self, detail):
        headers = {
            'Host': 'verify.zijieapi.com',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': self.ua,
            'sec-ch-ua-platform': '"Windows"',
            'Origin': 'https://www.douyin.com',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.douyin.com/',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }
        tmp = int(time.time() * 1000)
        msToken = self.session.cookies.get('msToken')
        url = f'https://verify.zijieapi.com/captcha/verify?lang=zh&app_name=%%E6%%8A%%96%%E9%%9F%%B3+Web+%%E7%%AB%%99&h5_sdk_version=2.28.9&h5_sdk_use_type=cdn&sdk_version=3.8.6&iid=0&did=0&device_id=0&ch=web_text&aid=6383&os_type=2&mode=slide&tmp=1688348478659&platform=pc&webdriver=false&fp=verify_ljm72xbx_LSV5avRU_ZG9V_4Jje_AxpN_YVgCxO9gjigy&type=verify&detail={detail}&server_sdk_env=%%7B%%22idc%%22:%%22lf%%22,%%22region%%22:%%22CN%%22,%%22server_type%%22:%%22passport%%22%%7D&subtype=slide&challenge_code=99999&os_name=windows&h5_check_version=3.8.6&xx-tt-dd=qJI7ttpVdGKKbSBvYqmaf0aPo&msToken={msToken}'
        x_bogus = self.get_signature(url).get('x_bogus')
        print('x-bogus', x_bogus)
        url = url + f'&X-Bogus={x_bogus}'
        data = {"captchaBody": captcha_data}
        response = self.session.post(
            url,
            headers=headers,
            verify=False,
        )

        with open('0.dat', 'wb') as f:
            f.write(response.content)

    def quick_login(self, phone_number, vali_code):
        csrf_token = self.session.cookies.get('passport_csrf_token')
        headers = {
            'Accept': 'application/json, text/javascript',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.douyin.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.douyin.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': self.ua,
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'x-tt-passport-csrf-token': csrf_token,
        }
        mobile = self.get_encrypt_mobile(f'+86 {phone_number}')
        code = self.get_encrypt_mobile(vali_code)
        data = {
            'mix_mode': '1',
            'mobile': mobile,
            'code': code,
            'service': 'https://www.douyin.com',
            'fixed_mix_mode': '1',
        }

        msToken = self.session.cookies.get('msToken')
        url = f'https://sso.douyin.com/quick_login/v2/?device_platform=web_app&aid=6383&account_sdk_source=sso&sdk_version=2.2.5&language=zh&verifyFp={self.verifyFp}&fp={self.verifyFp}&msToken={msToken}'
        x_bogus = self.get_signature(url).get('x_bogus')
        print('x-bogus', x_bogus)
        url = url + f'&X-Bogus={x_bogus}'

        response = self.session.post(
            url,
            headers=headers,
            data=data,
        )
        result = response.json()
        print(f'验证码验证： {result}')
        return result

    def auth(self):
        self.open_douyin()
        self.check_login()
        phone_number = input('请输入手机号：')
        acivate_result = self.send_activate_code(phone_number)
        if not acivate_result:
            raise Exception('验证码发送失败')
        elif acivate_result.get('error_code') != 0:
            raise Exception(acivate_result.get('description'))
        valicode = input('请输入验证码：')
        vali_result = self.quick_login(phone_number, valicode)
        if not vali_result:
            raise Exception('验证失败')
        elif vali_result.get('error_code') != 0:
            raise Exception(acivate_result.get('description'))
        login_url = vali_result.get('redirect_url')
        cookie = self.login(login_url)
        print(f'获取cookie结果： {cookie}')


if __name__ == '__main__':
    cookie = ''
    dy = DySmsAuth(cookie)
    dy.auth()
