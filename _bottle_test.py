from bottle import route, run

from ashes import ashes_bottle_template as template
from ashes import ashes_bottle_view as view

@route('/')
@route('/hello')
@route('/hello/<name>')
def hello(name='World'):
    return template('bottle_hello_template', name=name)


@route('/hello_dec')
@route('/hello_dec/<name>')
@view('bottle_hello_template')
def hello_dec(name='World'):
    return {'name': name}


if __name__ == '__main__':
    # debug=True will prevent templates from being cached,
    # so you see changes without a manual reload
    run(host='localhost', port=8080, reloader=True, debug=True)
