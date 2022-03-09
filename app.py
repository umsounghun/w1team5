from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import time
import schedule
import requests

from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.e5mxe.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta
global doc

@app.route('/posts/<keyword>')
def posts(keyword):
    go_list = list(db.candidate.find({}, {'_id': False}))
    can_list = list(db.candidate.find({"name":keyword}))
    word_receive = request.args.get("word_give")

    print(can_list)
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

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

while True:
    schedule.run_pending()
    time.sleep(1)

