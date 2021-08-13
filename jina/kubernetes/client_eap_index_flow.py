import requests
import time

from jina.kubernetes import kubernetes_tools

kubernetes_tools.get_pod_logs("otto")

time.sleep(6)

ip = '104.197.58.47'
host = f'http://{ip}'

data = [{'text': 'hello jina'} for _ in range(1)]
resp = requests.post(f'{host}/index', json={'data': data})
print(resp)