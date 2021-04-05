from datetime import datetime

from flask_restful import reqparse


def parse_args():
    parser = reqparse.RequestParser()
    parser.add_argument("id", required=True, type=int)
    parser.add_argument("title", required=True)
    parser.add_argument("content", required=True)
    parser.add_argument("categories", required=True)
    # Их наличие не обязательно, т.к. по дефолту
    # они сами устанавливаются в модели News в data/news.py
    parser.add_argument("created_date", required=False, type=datetime)
    parser.add_argument("modified_date", required=False, type=datetime)
    return parser.parse_args()
