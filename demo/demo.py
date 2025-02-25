import requests

data = {
    "text": "This is just some sample text",
}
url = "http://127.0.0.1:53048/calculate/sentiment-analysis"
res = requests.post(url, json=data)

if res.status_code == 200:
    __import__('pprint').pprint(res.json())
else:
    print(res.text)
