import json
import re
from abc import ABC
import requests
from deepdoc.parser import HtmlParser
from agent.component.base import ComponentBase, ComponentParamBase

SPECIFIC_STRING = "此内容来源校内知识库，经大模型优化生成，仅供参考！如有不准确，请点击“反馈”提交！"

class AnswerArchiverParam(ComponentParamBase):
    """
    Define the Crawler component parameters.
    """

    def __init__(self):
        super().__init__()
        self.method = "post"
        self.variables = []
        self.url = ""
        self.json = {}

    def check(self):
        self.check_valid_value(self.method.lower(), "Type of content from the crawler", ['get', 'post', 'put'])
        self.check_empty(self.url, "End point URL")


class AnswerArchiver(ComponentBase, ABC):
    component_name = "AnswerArchiver"

    def _run(self, history, **kwargs):
        args = {}
        for para in self._param.variables:
            if para.get("component_id"):
                if '@' in para["component_id"]:
                    component = para["component_id"].split('@')[0]
                    field = para["component_id"].split('@')[1]
                    cpn = self._canvas.get_component(component)["obj"]
                    for param in cpn._param.query:
                        if param["key"] == field:
                            if "value" in param:
                                args[para["key"]] = param["value"]
                else:
                    cpn = self._canvas.get_component(para["component_id"])["obj"]
                    if cpn.component_name.lower() == "answer":
                        args[para["key"]] = self._canvas.get_history(1)[0]["content"]
                        continue
                    _, out = cpn.output(allow_partial=False)
                    if not out.empty:
                        args[para["key"]] = "\n".join(out["content"])
            else:
                args[para["key"]] = para["value"]

        print(f"Sending request with args: {json.dumps(args, ensure_ascii=False, indent=4)}")
        print(self._param.json)

        if "answer" in args and SPECIFIC_STRING in args["answer"]:
            url = self._param.url.strip()
            if not re.match(r'^https?://', url):
                url = "http://" + url

            method = self._param.method.lower()

            headers = {}
            headers['Authorization'] = 'gjBnru247osdyO95ceojWQxj9lzBPfnF'

            if method == 'get':
                response = requests.get(url=url,
                                        params=args,
                                        headers=headers)
                return AnswerArchiver.be_output(response.text)

            elif method == 'put':
                response = requests.put(url=url,
                                        data=args,
                                        headers=headers)
                return AnswerArchiver.be_output(response.text)

            elif method == 'post':
                response = requests.post(url=url,
                                         json=args,
                                         headers=headers)
                return AnswerArchiver.be_output(response.text)
        else:
            pass