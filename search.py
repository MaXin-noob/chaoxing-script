
import requests
from urllib import parse
import json


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
        return json.loads(response.text)


