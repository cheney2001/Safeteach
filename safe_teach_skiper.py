import json
import time
import requests

class SafeTeachSkiper:
    LOGIN_URL = 'http://weiban.mycourse.cn/pharos/login/login.do'
    RAND_IMAGE_URL = 'https://weiban.mycourse.cn/pharos/login/randImage.do'
    LIST_SPECIAL_URL = 'http://weiban.mycourse.cn/pharos/project/listSpecial.do'
    LIST_COURSE_URL = 'http://weiban.mycourse.cn/pharos/usercourse/listCourse.do'
    POST_STUDY = 'https://weiban.mycourse.cn/pharos/usercourse/study.do'
    POST_GETCOURSE = 'https://weiban.mycourse.cn/pharos/usercourse/getCourseUrl.do'
    A07001 = 'https://mcwk.mycourse.cn/course/A07001/A07001.html'
    FINISH_COURSE_URL = 'https://weiban.mycourse.cn/pharos/usercourse/finish.do'

    def __init__(self):
        self._session = requests.session()
        self._user = None  # type: dict
        self._info = None  # type: dict

        self._time = int(time.time() *1000) #毫秒时间戳 验证码请求
        self._timestamp = int(time.time())  #秒时间错 登录Post

    def get_verifyCode(self):
        RAND_IMAGE = self.RAND_IMAGE_URL + str('?time=') + str(self._time);
        img = requests.get(RAND_IMAGE)
        f = open('/Users/cheney/Desktop/code.jpg','ab') #登录验证码存放地址 ，WINDOWS 请修改此路径。
        f.write(img.content)
        f.close()

    def login(self, tenant_code, key_number, password, verifyCode):
        form = {
            'tenantCode': tenant_code,
            'keyNumber': key_number,
            'password': password,
            'time': self._time,
            'verifyCode': verifyCode
        }
        LOGIN_URL_TIMESTAMP = self.LOGIN_URL + str('?timestamp=') + str(self._timestamp)
        resp = self._session.post(LOGIN_URL_TIMESTAMP, form)
        resp_str = resp.content.decode()
        result = self._get_data(resp_str)
        self._user = result
        return result is not None

    def _get_data(self, json_str, into_list=True):
        data = json.loads(json_str)  # type: dict
        result = data.get('data')
        if into_list and isinstance(result, list) and len(result) == 1:
            result = result[0]

        return result


    def get_info(self):
        form = {
            'userId': self._user['userId'],
            'tenantCode': self._user['tenantCode'],
        }
        LIST_SPECIAL_TIMESTAMP = self.LIST_SPECIAL_URL + str('?timestamp=') + str(int(time.time()))
        resp = self._session.post(LIST_SPECIAL_TIMESTAMP, form)
        resp_str = resp.content.decode()
        result = self._get_data(resp_str)
        self._info = result
        return result

    def list_course(self):
        form = {
            'userProjectId': self._user['preUserProjectId'],
            'chooseType': 3,
            'tenantCode': self._user['tenantCode'],
        }
        LIST_COURSE_TIMESTAMP = self.LIST_COURSE_URL + str('?timestamp=') + str(int(time.time()))
        resp = self._session.post(LIST_COURSE_TIMESTAMP, form)
        resp_str = resp.content.decode()
        result = self._get_data(resp_str, False)
        return result

    def post_study_getcourse(self,userCourseId,course_id):  #请求STUDY ，GETCOURSE 解决猫腻
        form = {
            'userProjectId':self._user['preUserProjectId'],
            'courseId':course_id,
            'tenantCode':self._user['tenantCode'],
        }
        CURRTIME = int(time.time())
        POST_STUDY_TIMESTAMP = self.POST_STUDY + str('?timestamp=')+str(CURRTIME)
        resp = self._session.post(POST_STUDY_TIMESTAMP,form)
        POST_GETCOURSE_TIMESTAMP = self.POST_GETCOURSE + str('?timestamp=')+str(CURRTIME)
        resp = self._session.post(POST_STUDY_TIMESTAMP,form)

        getForm = {
            'userCourseId':userCourseId,
            'tenantCode':self._user['tenantCode'],
            'type':1
        }
        resp = self._session.get(self.A07001, params=form)

    def finish(self, course_id):
        form = {
            'userCourseId': course_id,
            'tenantCode': self._user['tenantCode'],
        }
        resp = self._session.get(self.FINISH_COURSE_URL, params=form)
        resp_str = resp.content.decode()
        return 'ok' in resp_str
