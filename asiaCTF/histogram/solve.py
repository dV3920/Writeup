import requests

req = requests.post('https://histogram.chal.acsc.asia/api/histogram', files = {"csv" : open("sample.csv", "rb")}, verify = False)
print(req.text)