from flask import request, jsonify, redirect, url_for, session
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields

from app.models import User, AgeStatus, GenderStatus
from config import db


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    age = fields.Str(required=True)
    gender = fields.Str(required=True)
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


user_blp = Blueprint("users", __name__, url_prefix="/users", description="Operations on users")


@user_blp.route("/")
class UserList(MethodView):
    @user_blp.response(200, UserSchema(many=True))
    def get(self):
        """모든 사용자 목록 조회"""
        return User.query.all()

    @user_blp.arguments(UserSchema)
    @user_blp.response(201, UserSchema)
    def post(self, new_data):
        """새로운 사용자 생성"""
        user = User(**new_data)
        db.session.add(user)
        db.session.commit()
        return user


@user_blp.route("/<int:user_id>")
class UserResource(MethodView):
    @user_blp.response(200, UserSchema)
    def get(self, user_id):
        """ID로 특정 사용자 조회"""
        user = User.query.get_or_404(user_id)
        return user


@user_blp.route("/start_survey", methods=["POST"])
def start_survey():
    """설문조사 시작: 사용자 정보 저장 및 첫 질문으로 리다이렉트"""
    user_name = request.form["user_name"]
    user_email = request.form["user_email"]
    user_age = request.form["user_age"]
    user_gender = request.form["user_gender"]

    user = User.query.filter_by(email=user_email).first()
    if not user:
        user = User(name=user_name, age=AgeStatus[user_age], gender=GenderStatus[user_gender], email=user_email)
        db.session.add(user)
        db.session.commit()

    session["user_id"] = user.id
    session["current_question_sqe"] = 1 # 첫 질문부터 시작

    return redirect(url_for("questions.show_question", question_sqe=1))