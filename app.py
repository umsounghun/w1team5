from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient('mongodb+srv://gotgam:sparta@cluster0.k5twj.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta


@app.route('/')
def posts():
    return render_template('posts.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)