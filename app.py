from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)

import time
import jwt
import hashlib
import datetime
import schedule
import requests

from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'


client = MongoClient('mongodb+srv://test:sparta@cluster0.e5mxe.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta
global doc

@app.route('/posts/<keyword>')
def posts(keyword):
    go_list = list(db.candidate.find({}, {'_id': False}))
    can_list = list(db.candidate.find({"name":keyword}))
    word_receive = request.args.get("word_give")
    return render_template('posts.html', go_list = go_list, list = can_list, word=keyword )

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

@app.route('/membership')
def login():
    msg = request.args.get("msg")
    return render_template('membership.html', msg=msg)


@app.route('/login', methods=['POST'])
def sign_in():
    # 로그인
    return jsonify({'result': 'success'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    name_receive = request.form['name_give']
    gender_receive = request.form['gender_give']
    email_receive = request.form['email_give']
    #해시함수를 통해 암호화
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
        "profile_name": name_receive,                               # 이름
        "gender": gender_receive,                                   # 성별
        "email": email_receive,                                     # 이메일
        "like_1": 0,                                                # 기호1번 좋아요
        "like_2": 0,                                                # 기호2번 좋아요
        "like_3": 0,                                                # 기호3번 좋아요
        "like_5": 0,                                                # 기호5번 좋아요
        "like_6": 0,                                                # 기호6번 좋아요
        "like_7": 0,                                                # 기호7번 좋아요
        "like_8": 0,                                                # 기호8번 좋아요
        "like_10": 0,                                               # 기호10번 좋아요
        "like_11": 0,                                               # 기호11번 좋아요
        "like_12": 0,                                               # 기호12번 좋아요
        "like_13": 0,                                               # 기호13번 좋아요
        "like_14": 0                                                # 기호14번 좋아요
    }
    print(doc)
    #중복체크 로직
    user_list = list(db.users.find({"profile_name": name_receive, "gender":gender_receive}))
    len_user = len(user_list)
    print(len_user)
    if len_user == 0:
        db.users.insert_one(doc)
        msg = 'success'
    else:
        msg = 'fail'
    return jsonify({'result': msg})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

@app.route('/posts/like/personal', methods=['POST'])
def check_like():
    username_receive = request.form['username_give']
    can_num_receive = request.form['can_num_give']
    #좋아요 상태 확인
    like_list = list(db.like.find({"name": username_receive, "can_num": can_num_receive}, {'_id': False}))
    cnt_like = len(like_list)
    if cnt_like > 0:
        msg = 'success'
    else :
        msg = 'fail'
    return jsonify({'result': msg})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

while True:
    schedule.run_pending()
    time.sleep(1)

