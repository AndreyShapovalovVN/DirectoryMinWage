from flask import Flask, make_response

app = Flask(__name__)
app.config.from_object('settings')

page_home = 'Доступны следующие сервисы:'
page_home += '<br>http://{h}:{p}/DictWage/?wsdl\n'
page_home += '<br>http://{h}:{p}/api/GetMinWage?DateWage=2002-04-16\n'
page_home += '<br>http://{h}:{p}/api/GetProsperousMin?DateWage=2002-04-16\n'
page_home = page_home.format(h='0.0.0.0', p=app.config.get('APP_PORT'))


@app.route('/')
def home():
    response = make_response(page_home.encode('utf_8'))
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response
