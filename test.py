import requests
import json



urls = ['http://127.0.0.1:8000/analytics/geographical-distribution/',
'http://127.0.0.1:8000/analytics/customer-lifetime-value/',
'http://127.0.0.1:8000/analytics/new-customers/month/',
'http://127.0.0.1:8000/analytics/repeat-customers/',
'http://127.0.0.1:8000/analytics/sales-growth/',
'http://127.0.0.1:8000/analytics/total-sales/daily/'
]

def get_data(url):
    r1 = requests.get(url)
    data = r1.json()
    print(data)

for url in urls:
    print(url, "================================")
    get_data(url)
    