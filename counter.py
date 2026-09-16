import logging
import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import logging
import sys

load_dotenv()
os.makedirs('./logs', exist_ok=True)
log_file = './logs/counter.log'

APP_PORT = os.getenv('COUNTER_PORT')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.logger.handlers.clear()
logging.getLogger('werkzeug').disabled = True
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

#stdout_handler = logging.StreamHandler(sys.stdout)
#stdout_handler.setLevel(logging.INFO)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
#stdout_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
#app.logger.addHandler(stdout_handler)
#app.logger.setLevel(logging.INFO)

db = SQLAlchemy(app)

class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()
    if Counter.query.first() is None:
        db.session.add(Counter(count=0))
        db.session.commit()

@app.before_request
def log_request_info():
    app.logger.info(f"Request {request.method} {request.url} from {request.remote_addr}")

@app.route('/')
def index():
    log_request_info()
    counter = Counter.query.first()
    counter.count += 1
    db.session.commit()
    return render_template('index.html', count=counter.count)

if __name__ == '__main__':
    app.logger.info('Counter application started')
    app.run(host='0.0.0.0', port=APP_PORT)

