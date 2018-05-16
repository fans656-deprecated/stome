from flask import *


app = Flask(__name__)


@app.route('/')
def index():
    return send_file_from_directory('.', 'api.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=True)

