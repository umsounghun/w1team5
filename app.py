from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
import time
import schedule
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.e5mxe.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/posts')
def posts():
    return render_template('posts.html')

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
            li_symbol = symbol_list.text
        name_list = can_list.select_one('.name_txt')
        if name_list is not None:
            li_name = name_list.text
        party_list = can_list.select_one('.party')
        if party_list is not None:
            li_party = party_list.text
        doc = {
            'image': li_image,
            'name': li_name,
            'party': li_party,
            'symbol': li_symbol
        }
        if can_list is not profile[-1]:
            li_can.append(doc)
        db.candidate.insert_one(doc)
    print('DB input Sucess')

#10분마다 크롤링 진행.
schedule.every(30).minutes.do(Crowling)

@app.route('/')
def home():
    can_list = list(db.candidate.find({}, {'_id': False}))
    print(can_list)
    return render_template('index.html', list = can_list)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

while True:
    schedule.run_pending()
    time.sleep(1)

