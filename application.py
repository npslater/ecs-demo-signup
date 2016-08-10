# Copyright 2015. Amazon Web Services, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# changing this comment for demo commit
import os
import sys
import json

import flask
from flask import request, Response

from redis import Redis

import boto3

def exists_in_redis(key):
    return redis.exists(key)

def put_item_redis(key, value):
    redis.set(key, value)

def exists_in_ddb(key):
    ddb = boto3.client("dynamodb")
    response = ddb.get_item(
        TableName="ecs-demo-signup",
        Key={"email": {"S": key}})
    return "Item" in response

def put_item_ddb(key, tuples):
    item = {"email": {"S": key}}
    for tuple in tuples:
        if len(tuple[1]) > 0:
            item[tuple[0]] = {"S": tuple[1]}
    ddb = boto3.client("dynamodb")
    try:
        ddb.put_item(TableName="ecs-demo-signup", Item=item)
    except Exception as err:
        print err
        raise

# Create the Flask app
application = flask.Flask(__name__)
redis = Redis(host='redis', port=6379)

@application.route('/')
def welcome():
    return flask.render_template('index.html')

@application.route('/signup', methods=['POST'])
def signup():
    tuples = []
    signup_data = dict()
    for item in request.form:
        signup_data[item] = request.form[item]
        if item != "email":
            tuples.append((item, request.form[item]))

    if exists_in_ddb(signup_data['email']):
        return Response("", status=409, mimetype='application/json')
    else:
        put_item_ddb(signup_data['email'], tuples)

    return Response(json.dumps(signup_data), status=201, mimetype='application/json')

if __name__ == '__main__':
    application.run(host='0.0.0.0')
