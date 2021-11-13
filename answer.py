import time
import threading


class Answer(threading.Thread):
    def __init__(self, driver, delay=2):
        self.driver = driver
        self.delay = delay

    def start(self):
        print("启动视频中答题线程")
        while True:
            try:
                self.driver.find_element_by_xpath(
                    '//input[@value="true"]').click()
                time.sleep(self.delay)
                self.driver.find_element_by_xpath(
                    '//div[@class="ans-videoquiz-submit"]').click()   # 提交
                print('答题完成')
            except:
                pass
