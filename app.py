import jwt
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
import certifi
import time
import schedule
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

ca = certifi.where()


client = MongoClient('mongodb+srv://test:sparta@cluster0.e5mxe.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta
global doc

SECRET_KEY = 'SPARTA'

# @app.route('/') #홈 중복
# def home():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#         user_info = db.users.find_one({"username": payload["id"]})
#         return render_template('index.html', user_info=user_info)
#     except jwt.ExpiredSignatureError:
#         return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
#     except jwt.exceptions.DecodeError:
#         return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('posts.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


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

@app.route('/posts/<keyword>')
def posts(keyword):
    go_list = list(db.candidate.find({}, {'_id': False}))
    can_list = list(db.candidate.find({'name':keyword}))
    word_receive = request.args.get("word_give")

    print(can_list)
    return render_template('posts.html', go_list = go_list, list = can_list, word=keyword)

def Crowling():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    candidates = requests.get(
        'https://search.naver.com/search.naver?sm=tab_sug.top&where=nexearch&query=20%EB%8C%80+%EB%8C%80%EC%84%A0%ED%9B%84%EB%B3%B4&oquery=20%EB%8C%80+%EB%8C%80%EC%84%A0&tqi=hAkBJdprvhGssLlM2uNssssstJZ-052723&acq=20%EB%8C%80+%EB%8C%80%EC%84%A0&acr=1&qdt=0',
        headers=headers)
    soup_candidates = BeautifulSoup(candidates.text, 'html.parser')
    profile = soup_candidates.select('.list_item')
    li_can = []
    for can_list in profile:
        image_list = can_list.select_one('.thumb')
        if image_list is not None:
            images = image_list.select('img')
            for a in images:
                li_image = a['src']
        symbol_list = can_list.select_one('.thumb')
        if symbol_list is not None:
            li_symbol = symbol_list.text.replace(" ", "")
        name_list = can_list.select_one('.name_txt')
        if name_list is not None:
            li_name = name_list.text.replace(" ", "") #공백제거 추가
        party_list = can_list.select_one('.party')
        if party_list is not None:
            li_party = party_list.text.replace(" ", "")
        doc = {
            'image': li_image,
            'name': li_name,
            'party': li_party,
            'symbol': li_symbol,
            'like' : 0
        }
        if can_list is not profile[-1]:
            li_can.append(doc)
        chk_list = list(db.candidate.find({'name': doc['name']}, {'_id': False}))
        count_chk = len(chk_list)
        if count_chk == 0:
            db.candidate.insert_one(doc)
            print('후보자 정보 insert 성공')
        else:
            db.candidate.update_one({'name' : doc['name']},{'$set': {'image': doc['image']}})
            db.candidate.update_one({'name': doc['name']}, {'$set': {'name': doc['name']}})
            db.candidate.update_one({'name': doc['name']}, {'$set': {'party': doc['party']}})
            db.candidate.update_one({'name' : doc['name']},{'$set': {'symbol': doc['symbol']}})
            print('후보자 정보 update 성공')

#100분마다 크롤링 진행.
schedule.every(100).minutes.do(Crowling)

@app.route('/')
def home():
    can_list = list(db.candidate.find({}, {'_id': False}))

    return render_template('index.html', list = can_list)


@app.route("/detail", methods=["GET"])
def detail_get():
    can_detail =  list(db.can_detail.find({}, {'_id': False}))
    return jsonify({'can_detail': can_detail})

@app.route("/detail", methods=["POST"])
def detail_post():
    name_receive = request.form['name_give']
    detail_receive = request.form['detail_give']
    doc ={
        'name' : name_receive,
        'detail' : detail_receive
    }
    print(name_receive, detail_receive)
    chk_list = list(db.can_detail.find({'name': {'$eq' : name_receive}}, {'_id': False}))
    count_chk = len(chk_list)
    if count_chk == 0:
        db.can_detail.insert_one(doc)
        print('insert 성공')
    else:
        db.can_detail.update_one({'name': name_receive}, {'$set': {'detail': detail_receive}})
        print('update 성공')

    return jsonify({'msg': '공약 업데이트 성공'})

@app.route("/shot", methods=["POST"])
def value_post():
    doc_recive = request.form['doc_give']
    doc = doc_recive
    return jsonify({'msg': 'dict 업데이트 성공'})

@app.route('/membership')
def membership():
        return render_template('membership.html')

# @app.route('/')
# def membership():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

#         return render_template('index.html')
#     except jwt.ExpiredSignatureError:
#         return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
#     except jwt.exceptions.DecodeError:
#         return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))




@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    name_receive = request.form['name_give']
    gender_receive = request.form['gender_give']
    email_receive = request.form['email_give']
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "name": name_receive,                                       # 성함
        "gender": gender_receive,                                   # 성별
        "email": email_receive                                      # 이메일주소
    # }
    # 중복체크 로직
    # user_list = list(db.users.find({'name': name_receive, 'gender': gender_receive}))
    # len_user = len(user_list)
    # print(len_user)
    # if len_user == 0:
    #     db.users.insert_one(doc)
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

# @app.route('/sign_up/check_dup_member', methods=['POST'])
# def check_dup_member():
#     name_receive = request.form['name_give']
#     gender_receiv = request.form['gender_give']
#     exists2 = bool(db.users.find_one({"name": name_receive})) and bool(db.users.find_one({"gender": gender_receiv}))
#     return jsonify({'result': 'success', 'exists2': exists2})

# @app.route("/give_like", methods=["POST"])
# def give_like():
#     token_receive = request.cookies.get('mytoken')
#     try:
#     payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#     username = db.users.find_one({"username": payload["id"]})
#     cannum_receive = request.form["cannum_give"]
#     like_receive = request.form["like_give"]
#     doc= {
#         "can_num":cannum_receive,
#         "name":username["username"],
#         "status":like_receive
#     }
#     if like_receive == "like":
#         db.likes.update_one(doc)
#     else:
#         db.likes.delete_one(doc)
#     count = db.likes.count_documents({"cannum": cannum_receive, "username": username["username"]})
#     return jsonify({"result": "success", 'msg': 'updated', "count": count})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

while True:
    schedule.run_pending()
    time.sleep(1)

