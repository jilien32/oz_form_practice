from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields

from app.models import Image
from config import db


class ImageSchema(Schema):
    id = fields.Int(dump_only=True)
    url = fields.Str(required=True)
    type = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


images_blp = Blueprint("images", __name__, url_prefix="/images", description="Operations on images")


@images_blp.route("/")
class ImageList(MethodView):
    @images_blp.response(200, ImageSchema(many=True))
    def get(self):
        """모든 이미지 목록 조회"""
        return Image.query.all()

    @images_blp.arguments(ImageSchema)
    @images_blp.response(201, ImageSchema)
    def post(self, new_data):
        """새로운 이미지 생성"""
        image = Image(**new_data)
        db.session.add(image)
        db.session.commit()
        return image
