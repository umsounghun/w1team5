from pymongo import MongoClient

client = MongoClient('mongodb+srv://test:sparta@cluster0.e5mxe.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

@app.route("/posts/like", methods=["POST"])
def like_post():
    like_receive = request.form['like_give']
    bucket_list = list(db.bucket.find({}, {'_id': False}))
    num = len(bucket_list) + 1

    doc = {
        'candidate_num': num,
        'id': jwt방식에서 가져온 ID ,
        'done': 0
    }


    db.bucket.insert_one(doc)