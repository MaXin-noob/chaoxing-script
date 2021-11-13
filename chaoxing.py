import time
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import re
import sys
from selenium import webdriver
from search import SearchAnswer


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
        self.driver.switch_to.frame("iframe")
        class_name = self.driver.find_element_by_class_name("ZyTop")
        title = class_name.find_element_by_xpath(
            "h3").get_attribute('textContent')
        time.sleep(self.delay)
        isOk = self.driver.find_element_by_class_name("ans-job-icon")
        if isOk.value_of_css_property('background-position-y') == "-24px":  # 完成
            print("这个任务点:", title, "已经完成")
            return True
        else:
            return False

    def play_video(self):
        self.switch_window()
        print("进入播放页面")
        self.driver.find_element_by_xpath(
            "//div[@class='leveltwo']/h3/a").click()
        self.switch_window()
        self.driver.find_element_by_id("right2").click()
        self.get_question()
        # while True:
        #     if self.task_finish:
        #         self.switch_window()
        #         self.driver.find_element_by_id("right2").click()
        #         self.get_question()
        #     else:
        #         videoFrame = self.driver.find_element_by_xpath("//iframe")
        #         self.driver.switch_to.frame(videoFrame)
        #         vedio = self.driver.find_element_by_id("video_html5_api")
        #         self.driver.find_element_by_xpath("//button").click()
        #         self.driver.execute_script("arguments[0].muted=true", vedio)
        #         ActionChains(driver=self.driver).move_to_element(
        #             vedio).perform()
        #         time.sleep(self.delay)
        #         while True:
        #             regex = r'<div class="vjs-play-progress vjs-slider-bar" style="width: (.*?)%;">'
        #             result = re.search(regex, self.driver.page_source, re.S)
        #             res = result.group(1) if result else None
        #             print("\r当前播放到: {}".format(res)+'％', end=" ")
        #             if res == "100":
        #                 print("当前课程已经完成，将自动跳转到下一个课程")
        #                 break
        #             time.sleep(3)
        #         self.switch_window()

    def get_question(self):
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
            qu_title = qu_title.replace(" ", "")
            pattern = re.compile(r'【(.*?)】')
            temp = pattern.search(qu_title).group()
            print(temp)
            qu_type = None
            if temp == "【单选题】":
                qu_type = 0
            elif temp == "【多选题】":
                qu_type = 1
            elif temp == "【判断题】":
                qu_type = 3
            qu_title = qu_title.replace(temp, "").replace(
                "（", "").replace("）", "").replace("。", "")
            self.set_question(qu_title, qu_type)
            self.get_answer()
            print(qu_title)
            break
