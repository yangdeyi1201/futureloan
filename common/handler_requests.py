import requests


def visit_api(method, url, headers=None, params=None, data=None, json=None, **kwargs):

    """ 接口访问，返回响应对象，支持多种请求方法 """

    # method：请求方法，大小写不敏感
    # headers：请求头部信息
    # params：querystring，查询字符串，在 url 中发送
    # data: 在请求体中，以 form 表单格式发送
    # json: 在请求体中，以 json 数据格式发送

    res = requests.request(method, url, headers=headers, params=params, data=data, json=json, **kwargs)
    return res.json()
