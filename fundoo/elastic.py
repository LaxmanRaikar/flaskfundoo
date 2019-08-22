# from datetime import datetime
# from flask import Flask, jsonify, request
# from elasticsearch import Elasticsearch
#
# es = Elasticsearch()
#
# app = Flask(__name__)
#
# @app.route('/', methods=['GET'])
# def index():
#     results = es.get(index='contents', doc_type='title', id='my-new-slug')
#     return jsonify(results['_source'])
#
#
# @app.route('/insert_data', methods=['POST', 'GET'])
# def insert_data():
#
#     title = request.form.get('title')
#     content = request.form.get('content')
#
#     body = {
#         'title': title,
#         'content': content,
#         'timestamp': datetime.now()
#     }
#
#     result = es.index(index='contents', doc_type='title',  body=body)
#
#     return jsonify(result)
#
# @app.route('/search', methods=['POST'])
# def search():
#     keyword = request.form.get('keyword')
#
#     body = {
#         "query": {
#             "multi_match": {
#                 "query": keyword,
#                 "fields": ["content", "title"]
#             }
#         }
#     }
#
#     res = es.search(index="contents", body=body)
#
#     return jsonify(res['hits']['hits'])
#
# app.run(port=5000, debug=True)