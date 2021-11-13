
import requests
from urllib import parse


class SearchAnswer:
    def __init__(self, api, method="POST"):
        self.method = method
        self.api = api
        self.question = ""
        self.type = None

    def set_question(self, question,type):
        self.question = parse.quote_plus(question)
        self.type = type


    def get_answer(self):
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        payload = 'question={0}&type={1}'.format(self.question,self.type)
        response = requests.request(self.method, self.api, headers=headers, data=payload)
        print(response.text)



# search = SearchAnswer("http://cx.icodef.com/wyn-nb?v=4")
# search.set_question("关于树立正确的党史观，下列说法中错误的是",0)
# search.get_answer()
