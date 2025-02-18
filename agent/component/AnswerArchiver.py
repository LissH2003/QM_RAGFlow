import json
import re
from abc import ABC
import requests
from agent.component.base import ComponentBase, ComponentParamBase
from functools import partial


class AnswerArchiverParam(ComponentParamBase):
    """
    Define the parameters for the AnswerArchiver component.
    """

    def __init__(self):
        super().__init__()
        self.method = "post"
        self.variables = []
        self.url = ""
        self.json = {} 
        self.headers = {}
        self.string = ""

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
                    component, field = para["component_id"].split('@')
                    cpn = self._canvas.get_component(component)["obj"]
                    for param in cpn._param.query:
                        if param["key"] == field and "value" in param:
                            args[para["key"]] = param["value"]
                else:
                    cpn = self._canvas.get_component(para["component_id"])["obj"]
                    if cpn.component_name.lower() == "answer":
                        answer_output = self._canvas.get_history(1)[0]["content"]
                        args[para["key"]] = answer_output
                        continue
                    _, out = cpn.output(allow_partial=False)
                    if not out.empty:
                        args[para["key"]] = "\n".join(out["content"])
            else:
                args[para["key"]] = para["value"]

        args = json.loads(json.dumps(args))
        if isinstance(self._param.json, str):
            try:
                self._param.json = json.loads(self._param.json)
            except json.JSONDecodeError as e:
                print(f"Failed JSON decode: {e}")
                return self.be_output(args.get('answer', ''))

        if not isinstance(self._param.json.get('data'), dict):
            self._param.json['data'] = {}

        for key, value in args.items():
            self._param.json['data'][key] = value

        SPECIFIC_STRING = self._param.string

        if "answer" in args and (SPECIFIC_STRING not in args["answer"] or not kwargs.get("stream")):
            if kwargs.get("stream"):
                return partial(self.stream_output, args.get('answer', ''))
            else:
                return self.be_output(args.get('answer', ''))

        url = self._param.url.strip()
        if not re.match(r'^https?://', url):
            url = "http://" + url

        method = self._param.method.lower()

        headers = json.loads(self._param.headers)

        response = None
        if method == 'get':
            response = requests.get(url=url, params=self._param.json, headers=headers)
            result = response.text
        elif method == 'put':
            response = requests.put(url=url, data=self._param.json, headers=headers)
            result = response.text
        elif method == 'post':
            response = requests.post(url=url, json=self._param.json, headers=headers)
            print(response.json().get('msg'))
            result = response.json().get('result', {}).get('answer')

        if kwargs.get("stream"):
            return partial(self.stream_output, result)
        else:
            return self.be_output(result)

    def stream_output(self, content=None):
        yield {"content": content}

    def be_output(self, output_content):
        return output_content
