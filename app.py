from pymongo import MongoClient
import jwt
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
import certifi

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.e5mxe.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

# @app.route('/user/<username>')
# def user(username):
#     # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False
#
#         user_info = db.users.find_one({"username": username}, {"_id": False})
#         return render_template('user.html', user_info=user_info, status=status)
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# @app.route('/sign_up/save', methods=['POST'])
# def sign_up():
#     # 회원가입
#     username_receive = request.form['username_give']
#     password_receive = request.form['password_give']
#     password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
#     # DB에 저장
#     return jsonify({'result': 'success'})
#
#
# @app.route('/sign_up/check_dup', methods=['POST'])
# def check_dup():
#     # ID 중복확인
#     return jsonify({'result': 'success'})


# @app.route('/update_profile', methods=['POST'])
# def save_img():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         # 프로필 업데이트
#         return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))

@app.route('/posts')
def comment():
    msg = request.args.get("msg")
    return render_template('posts.html', msg=msg)

@app.route("/posts/comment", methods=["POST"])
def comment_post():
    comment_receive = request.form['comment_give']
    comment_list = list(db.comment.find({}, {'_id': False}))

    doc = {
        'comment' : comment_receive
    }

    db.comment.insert_one(doc)
    return jsonify({'msg':'댓글 등록 완료!'})

@app.route("/posts/comment", methods=["GET"])
def comment_get():
    comment_list = list(db.comment.find({}, {'_id': False}))
    return jsonify({'comments': comment_list})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)