from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.e5mxe.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route('/')
def home():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    candidates = requests.get(
        'https://search.naver.com/search.naver?sm=tab_sug.top&where=nexearch&query=20%EB%8C%80+%EB%8C%80%EC%84%A0%ED%9B%84%EB%B3%B4&oquery=20%EB%8C%80+%EB%8C%80%EC%84%A0&tqi=hAkBJdprvhGssLlM2uNssssstJZ-052723&acq=20%EB%8C%80+%EB%8C%80%EC%84%A0&acr=1&qdt=0',
        headers=headers)
    soup_candidates = BeautifulSoup(candidates.text, 'html.parser')
    profile = soup_candidates.select('.list_item')
    li_image = []
    li_symbol = []
    li_name = []
    li_party = []
    for can_list in profile:
        image_list = can_list.select_one('.thumb')
        if image_list is not None:
            images = image_list.select('img')
            for a in images:
                li_image.append(a['src'])
    for can_list in profile:
        symbol_list = can_list.select_one('.thumb')
        if symbol_list is not None:
            li_symbol.append(symbol_list.text)
    for can_list in profile:
        name_list = can_list.select_one('.name_txt')
        if name_list is not None:
            li_name.append(name_list.text)
    for can_list in profile:
        party_list = can_list.select_one('.party')
        if party_list is not None:
            li_party.append(party_list.text)

    return render_template('index.html', symbols = li_symbol, names = li_name, )

@app.route("/candidates", methods=["GET"])
def can_list_get():
    #대선 후보 크롤링
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    candidates = requests.get('https://search.naver.com/search.naver?sm=tab_sug.top&where=nexearch&query=20%EB%8C%80+%EB%8C%80%EC%84%A0%ED%9B%84%EB%B3%B4&oquery=20%EB%8C%80+%EB%8C%80%EC%84%A0&tqi=hAkBJdprvhGssLlM2uNssssstJZ-052723&acq=20%EB%8C%80+%EB%8C%80%EC%84%A0&acr=1&qdt=0',headers=headers)
    soup_candidates = BeautifulSoup(candidates.text, 'html.parser')
    profile = soup_candidates.select('.list_item')
    li_image = []
    li_symbol = []
    li_name = []
    li_party = []
    for can_list in profile:
        image_list = can_list.select_one('.thumb')
        if image_list is not None:
            images = image_list.select('img')
            for a in images:
                li_image.append(a['src'])
    for can_list in profile:
        symbol_list = can_list.select_one('.thumb')
        if symbol_list is not None:
            li_symbol.append(symbol_list.text)
    for can_list in profile:
        name_list = can_list.select_one('.name_txt')
        if name_list is not None:
            li_name.append(name_list.text)
    for can_list in profile:
        party_list = can_list.select_one('.party')
        if party_list is not None:
            li_party.append(party_list.text)
    return jsonify({'symbol' : li_symbol,
                    'name'  : li_name,
                    'party'  : li_party,
                    'image'  : li_image})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
