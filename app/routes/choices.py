from flask import request, jsonify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields

from app.models import Choices, Question
from config import db


class ChoiceSchema(Schema):
    id = fields.Int(dump_only=True)
    content = fields.Str(required=True)
    is_active = fields.Bool(required=True)
    sqe = fields.Int(required=True)
    question_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


choices_blp = Blueprint("choices", __name__, url_prefix="/choices", description="Operations on choices")


@choices_blp.route("/")
class ChoiceList(MethodView):
    @choices_blp.response(200, ChoiceSchema(many=True))
    def get(self):
        """모든 선택지 목록 조회"""
        return Choices.query.all()

    @choices_blp.arguments(ChoiceSchema)
    @choices_blp.response(201, ChoiceSchema)
    def post(self, new_data):
        """새로운 선택지 생성"""
        choice = Choices(**new_data)
        db.session.add(choice)
        db.session.commit()
        return choice
