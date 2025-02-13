from functools import partial
from typing import Tuple, Union, Generator

import pandas as pd
import http.client
import json
from agent.component.base import ComponentBase, ComponentParamBase


class AnswerArchiverParam(ComponentParamBase):
    """
    Define the AnswerArchiver component parameters.
    """
    def __init__(self):
        super().__init__()
        self.external_api_host = "szyx.xauat.edu.cn"
        self.external_api_path = "/openapi/v2/app/form/data_create"  
        self.authorization = 'txyutyEOwY7e1hCiWNmI3orPawHRRJyQ' 
        self.appId = "66cd3a7ce4b0e5eea624026d"
        self.formId = "67a9a672e4b000e54972cb86"
        self.output_var_name = "processed_data"

    def check(self):
        return True  


class AnswerArchiver(ComponentBase):
    component_name = "AnswerArchiver"

    def _run(self, history, **kwargs):
        original_input_data = self.get_input() 
        
        print("接收到的输入数据:")
        print(original_input_data)

        if not isinstance(original_input_data, pd.DataFrame) or original_input_data.empty:
            print("没有有效的数据需要处理。")
            self.set_output(pd.DataFrame()) 
            return
        
        non_kb_data = []
        for index, row in original_input_data.iterrows():
            content = row['content']
            if "知识库检索" not in content:
                non_kb_data.append({"content": content})
                
                try:
                    payload = json.dumps({
                        "appId": self._param.appId,
                        "formId": self._param.formId,
                        "data": {
                            "answer": content  
                        },
                        "openId": "",
                        "extField": "",
                        "dataCheck": "NO",
                        "calculate": "NO",
                        "startFlow": "NO",
                        "startEvent": "NO"
                    })
                    headers = {
                        'Authorization': f'Bearer {self._param.authorization}',
                        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
                        'Content-Type': 'application/json',
                        'Accept': '*/*',
                        'Host': self._param.external_api_host,
                        'Connection': 'keep-alive'
                    }
                    conn = http.client.HTTPSConnection(self._param.external_api_host, timeout=10)
                    conn.request("POST", self._param.external_api_path, payload, headers)
                    res = conn.getresponse()
                    if res.status == 200:
                        print(f"成功发送数据: {content}")
                    else:
                        response_body = res.read().decode()
                        print(f"发送数据失败: {content}, 状态码: {res.status}, 响应: {response_body}")
                    conn.close()
                except Exception as e:
                    print(f"发送数据失败: {content}, 错误: {str(e)}")
                    continue  

        if kwargs.get("stream"):
            return partial(self.stream_output, original_input_data)
        else:
            self.set_output(original_input_data)
        
        print("数据处理和 API 调用已完成，输出数据与输入数据一致。")

    def stream_output(self, original_input_data: pd.DataFrame):
        """用于流模式下的输出"""
        if hasattr(self, "exception") and self.exception:
            yield {"content": str(self.exception)}
            self.exception = None
            return

        if isinstance(original_input_data, pd.DataFrame):
            for index, row in original_input_data.iterrows():
                yield {"content": row['content']}
        else:
            for item in original_input_data:
                yield item

    def set_exception(self, e):
        self.exception = e

    def output(self, allow_partial=True) -> Tuple[str, Union[pd.DataFrame, partial]]:
        if allow_partial:
            output_df = getattr(self._param, self._param.output_var_name, pd.DataFrame())
            if not isinstance(output_df, (pd.DataFrame, partial)):
                output_df = pd.DataFrame()
            return self._param.output_var_name, output_df

        for r, c in self._canvas.history[::-1]:
            if r == "user":
                return self._param.output_var_name, pd.DataFrame([{"content": c}])

        return self._param.output_var_name, pd.DataFrame([])