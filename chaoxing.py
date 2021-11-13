import time
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import re
import sys
from selenium import webdriver
from search import SearchAnswer
import random


class Script(SearchAnswer):
    global driver

    def __init__(self, username, password, classname, delay=0, headless=True, api="http://cx.icodef.com/wyn-nb?v=4"):
        super().__init__(api)
        self.username = username
        self.password = password
        self.classname = classname
        self.delay = delay
        self.headless = headless

    def get_driver(self):
        return self.driver

    def start(self):
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument('--disable-gpu')
        if self.headless:
            options.add_argument('-headless')
        self.driver = webdriver.Chrome(chrome_options=options)
        if self.delay != 0:
            self.driver.implicitly_wait(10)
        self.driver.get('http://passport2.chaoxing.com/login?newversion=true')
        self.login(self.username, self.password)
        self.assert_cookie()
        self.find_class()
        self.play_video()

    def login(self, account, password):
        try:
            print("正在尝试登录")
            self.driver.find_element_by_id("phone").send_keys(account)
            self.driver.find_element_by_id("pwd").send_keys(password)
            time.sleep(self.delay)
            self.driver.find_element_by_id("loginBtn").click()
            time.sleep(self.delay)
            print("登录成功")
            print("您的用户名:", account)
        except Exception:
            print("登录失败，请重试")
            sys.exit(0)

    def assert_cookie(self):
        self.driver.switch_to.frame("frame_content")
        try:
            self.driver.find_element_by_xpath(
                "//div[@class='hover-box']/a").click()
        except Exception:
            print("cookie尚未失效")
        time.sleep(self.delay)

    def find_class(self):
        try:
            courseListUL = self.driver.find_element_by_xpath(
                "//ul[@class='course-list']")
            print("定位课程目录")
            allCourse = courseListUL.find_elements_by_xpath("li")
            findFG = False
            classLink = ""
            for course in allCourse:
                classLink = course.find_element_by_xpath(
                    "div[@class='course-info']/h3/a")
                className = classLink.find_element_by_xpath("span")
                text = className.get_attribute('textContent')
                if text == self.classname:
                    print("成功找到课程：", text)
                    findFG = True
                    break
            if findFG:
                print("进入课程：", text)
                classLink.click()
            else:
                print("没有找到课程，请检查课程名称是否正确")
                sys.exit(0)
        except Exception:
            print("定位课程目录错误，请重试")
            sys.exit(0)

    def switch_window(self):
        time.sleep(self.delay)
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])
        # print("切换窗口，当前窗口：",self.driver.title)
        time.sleep(self.delay)

    def task_finish(self):
        self.switch_window()
        class_name = self.driver.find_element_by_class_name("main")
        title = class_name.find_element_by_xpath(
            "h1").get_attribute('textContent')
        time.sleep(self.delay)
        self.driver.switch_to.frame("iframe")
        time.sleep(self.delay)
        isOk = self.driver.find_element_by_class_name("ans-job-icon")
        if isOk.value_of_css_property('background-position-y') == "-24px":  # 完成
            print("任务点:", title, "已经完成")
            return True
        else:
            return False

    def play_video(self):
        self.switch_window()
        print("进入播放页面")
        self.driver.find_element_by_xpath(
            "//div[@class='leveltwo']/h3/a").click()
        while True:
            if self.task_finish():
                self.switch_window()
                self.driver.find_element_by_id("right2").click()
                if self.task_finish():
                    self.switch_window()
                    self.driver.find_element_by_id("right2").click()
                else:
                    self.answer_question()
                    time.sleep(self.delay)
                    self.driver.execute_script("btnBlueSubmit();")
                    time.sleep(self.delay)
                    self.driver.execute_script("form1submit();")
                    self.switch_window()
                    self.driver.find_element_by_id("right2").click()
            else:
                videoFrame = self.driver.find_element_by_xpath("//iframe")
                self.driver.switch_to.frame(videoFrame)
                vedio = self.driver.find_element_by_id("video_html5_api")
                self.driver.find_element_by_xpath("//button").click()
                self.driver.execute_script("arguments[0].muted=true", vedio)
                ActionChains(driver=self.driver).move_to_element(
                    vedio).perform()
                time.sleep(self.delay)
                while True:
                    regex = r'<div class="vjs-play-progress vjs-slider-bar" style="width: (.*?)%;">'
                    result = re.search(regex, self.driver.page_source, re.S)
                    res = result.group(1) if result else None
                    print("\r当前播放到: {}".format(res)+'％', end=" ")
                    if res == "100":
                        print("当前课程已经完成，将自动跳转到下一个课程")
                        break
                    time.sleep(3)
                self.switch_window()

    def answer_question(self):
        self.switch_window()
        self.driver.switch_to.frame("iframe")
        time.sleep(self.delay)
        self.driver.switch_to.frame(0)
        time.sleep(self.delay)
        self.driver.switch_to.frame("frame_content")
        questions = self.driver.find_elements_by_class_name("TiMu")
        for question in questions:
            qu_title = question.find_element_by_xpath(
                "div/div").get_attribute('textContent')
            print(qu_title)
            pattern = re.compile(r'【(.*?)】')
            temp = pattern.search(qu_title).group()
            qu_type = None
            if temp == "【单选题】":
                qu_type = 0
            elif temp == "【多选题】":
                qu_type = 1
            elif temp == "【判断题】":
                qu_type = 3
            qu_title = qu_title.replace(temp, "")
            self.set_question(qu_title, qu_type)
            answer = self.get_answer()
            if answer["code"] == -1:
                print("题库中没有题目", qu_title)
                print("正在随机作答")
                # TODO 添加随机作答功能

                continue
            self.set_answer(question, answer, qu_type)

    def random_answer(self, question, answer, type):
        if type == 0:
            tempNumber = 0
            ans = question.find_elements_by_xpath(
                "div[2]//ul/li")
            random_key = random.randint(0, 3)
            for an in ans:
                tempNumber += 1
                an = an.find_element_by_xpath("a")
                if tempNumber == random_key:
                    an.click()
        elif type == 1:
            tempNumber = 0
            ans = question.find_elements_by_xpath(
                "div[2]//ul/li")
            random_key = random.randint(0, 3)
            for an in ans:
                tempNumber += 1
                an = an.find_element_by_xpath("a")
                if tempNumber == random_key:
                    an.click()
        elif type == 3:
            ans = question.find_elements_by_xpath(
                "div[2]//ul/li")
            for an in ans:
                an = an.find_element_by_xpath("label")
                str2 = re.sub(
                    u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", answer["data"])
                if str2 == "正确":
                    an.find_element_by_xpath(
                        "//input[@value='true']").click()
                else:
                    an.find_element_by_xpath(
                        "//input[@value='false']").click()

    def set_answer(self, question, answer, type):
        if type == 0:
            ans = question.find_elements_by_xpath(
                "div[2]//ul/li")
            for an in ans:
                an = an.find_element_by_xpath("a")
                str1 = re.sub(
                    u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", an.get_attribute("textContent"))
                str2 = re.sub(
                    u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", answer["data"])
                if str1 == str2:
                    an.click()
        elif type == 1:
            ans = question.find_elements_by_xpath(
                "div[2]//ul/li")
            for an in ans:
                an = an.find_element_by_xpath("a")
                str1 = re.sub(
                    u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", an.get_attribute("textContent"))
                str2_s = answer["data"].split("#")
                for str2 in str2_s:
                    str2 = re.sub(
                        u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", str2)
                    if str1 == str2:
                        an.click()
        elif type == 3:
            ans = question.find_elements_by_xpath(
                "div[2]//ul/li")
            for an in ans:
                an = an.find_element_by_xpath("label")
                str2 = re.sub(
                    u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", answer["data"])
                if str2 == "正确":
                    an.find_element_by_xpath(
                        "//input[@value='true']").click()
                else:
                    an.find_element_by_xpath(
                        "//input[@value='false']").click()
