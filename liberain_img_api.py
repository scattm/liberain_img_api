from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import hashlib, time

app = Flask(__name__)
app.config.from_envvar('LIBERAIN_SETTINGS')
db = SQLAlchemy(app)


class UserKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(20), unique=True)
    authKey = db.Column(db.String(80))
    expireOn = db.Column(db.Integer)

    def __init__(self, uid):
        self.uid = uid

        timestamp = int(time.time())
        hash_string = app.config.get('AUTH_KEY_HASH_STRING') + uid + timestamp.__str__()
        self.authKey = int(hashlib.sha1(hash_string).hexdigest(), 16) % (10 ** 16)

        self.expireOn = timestamp + 300

    def __repr__(self):
        return "<UserId %s>" % self.uid


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/user/api/v1.0/key/<string:uid>', methods=['GET'])
def get_key(uid):
    user_key = UserKey.query.filter_by(uid=uid).first()
    if user_key is None:
        user_key = UserKey(uid)
        db.session.add(user_key)
        db.session.commit()
        return jsonify({
            'user': {
                'uid': user_key.uid,
                'key': user_key.authKey,
                'expired': False
            }
        })
    else:
        cur_time = int(time.time())
        expired = user_key.expireOn >= cur_time
        return jsonify({
            'user': {
                'uid': user_key.uid,
                'key': user_key.authKey,
                'expired': expired
            }
        })


if __name__ == '__main__':
    app.run()
