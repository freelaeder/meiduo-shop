import json

from ronglian_sms_sdk import SmsSDK


class SmsUtil:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.smsSdk = SmsSDK(accId='8aaf07087dc23905017dc74ff83701b7',
                                accToken='68507d25130344b58d116d42ce4b131d',
                                appId='8a216da87dc23fe1017dc750a7aa0192')

        return cls.__instance

    def send_message(self, mobile='18916216440', tid='1', code='1234'):

        sendback = self.smsSdk.sendMessage(tid=tid, mobile=mobile, datas=(code, 5))
        # 把返回值转为字典
        sendback = json.loads(sendback)
        # "statusCode": "000000"
        if sendback.get("statusCode") == "000000":
            print("发送成功")
        else:
            print("发送失败")
