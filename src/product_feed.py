import os

import csv
import json
import logging
from enum import Enum, auto
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, request, Response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from marshmallow import validate
from webargs import fields
from webargs.flaskparser import use_kwargs

app = Flask(__name__)
# limiter = Limiter(app, key_func=get_remote_address, default_limits=["10 per minute"])


load_dotenv()

access_token = os.environ.get('ACCESS_TOKEN')

port = int(os.environ.get('PORT', 5000))

logging.basicConfig(level=logging.INFO)

file_template = './data/product_feed_{}.csv'


class StoreId(Enum):
    DFS = auto()
    WFN = auto()
    FF = auto()
    TW = auto()
    DFSDev = auto()


pathes_map = {
    StoreId.DFS.name: file_template.format(StoreId.DFS.name),
    StoreId.WFN.name: file_template.format(StoreId.WFN.name),
    StoreId.FF.name: file_template.format(StoreId.FF.name),
    StoreId.TW.name: file_template.format(StoreId.TW.name),
    StoreId.DFSDev.name: file_template.format(StoreId.DFSDev.name),
}


def catch_custom_exception(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e), 500
    return decorated_function


@app.route("/")
# @limiter.limit("10/minute")
def hello():
    app.logger.info(f"Received request form IP: {request.access_route}")
    return "Hello World!"


@app.route("/catalog", methods=['GET'])
# @limiter.limit("10/minute")
@use_kwargs(
    {
        "store_id": fields.Str(
            # required=True,
            missing='DFS',
            validate=[validate.Length(min=2, max=6)],
        )
    },
    location="query",
)
@catch_custom_exception
def catalog(store_id):
    app.logger.info(f"Received request form IP: {request.access_route}, {request.remote_addr}")

    if request.headers.environ['HTTP_USER_AGENT'] != 'Klaviyo/1.0' and request.args.get('access_token') != access_token:
        return 'INVALID REQUEST', 400

    with open(pathes_map.get(store_id), encoding='latin-1') as f:
        reader = csv.DictReader(f)

        entries = []
        for product in reader:
            app.logger.info(f"Prepared product: {product}")
            entries.append(product)

        with open(f'./data/catalog_{store_id}.json', 'w+') as f:
            f.write(json.dumps(entries))

    with open(f'./data/catalog_{store_id}.json') as f:
        content = f.read()

    response = Response(content, mimetype='application/rss+xml')
    return response


if __name__ == "__main__":
    app.run(debug=False, port=port)
