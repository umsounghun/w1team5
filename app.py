from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.e5mxe.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/posts')
def posts():
    return render_template('posts.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

