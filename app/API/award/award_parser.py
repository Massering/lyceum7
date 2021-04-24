from datetime import datetime

from flask_restful import reqparse


def parse_args():
    parser = reqparse.RequestParser()
    parser.add_argument("id", required=True, type=int)
    parser.add_argument("title", required=True)
    parser.add_argument("image_filename", required=True)
    parser.add_argument("direction", required=True)
    parser.add_argument("description", required=True)
    # Их наличие не обязательно, т.к. по дефолту
    # они сами устанавливаются в модели Award
    parser.add_argument("creation_date", type=datetime, required=False)
    return parser.parse_args()
