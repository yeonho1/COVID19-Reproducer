from covid_parser import COVIDParser
import json
from wsgiref.simple_server import make_server

with open('key.txt', 'r') as f:
    key = f.read().strip()

recent_data = []
parser = COVIDParser(key)

def application(environ, start_response):
    code = None
    data = None
    retry_count = 0
    while code != 0 and retry_count < 10:
        code, data = parser.request(10)
        if code < 0:
            print('[COVID-Server] Error occured while getting data. Retrying...')
        retry_count += 1
    if retry_count >= 10:
        print('[COVID-Server] Maximum retry count exceeded. Serving previous data...')
    recent_data = data
    start_response('200 OK', [
        ('Content-type', 'text/json')
    ])
    return [bytes(json.dumps(recent_data), 'utf-8')]

httpd = make_server('0.0.0.0', 8000, application)
httpd.serve_forever()