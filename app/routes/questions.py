from flask import request, jsonify, render_template, session, redirect, url_for
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields
from sqlalchemy.orm import joinedload

from app.models import Question, Image, Choices
from config import db


class QuestionSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    is_active = fields.Bool(required=True)
    sqe = fields.Int(required=True)
    image_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


questions_blp = Blueprint(
    "questions", __name__, description="Operations on questions"
)

@questions_blp.route("/")
def show_start_page():
    """설문조사 시작 페이지 렌더링"""
    return render_template("index.html")


@questions_blp.route("/survey/<int:question_sqe>")
def show_question(question_sqe):
    """특정 질문 페이지 렌더링"""
    if "user_id" not in session:
        return redirect(url_for("questions.show_start_page"))

    question = Question.query.options(joinedload(Question.choices), joinedload(Question.image)).filter_by(sqe=question_sqe, is_active=True).first_or_404()
    session["current_question_sqe"] = question_sqe
    return render_template("question.html", question=question)


@questions_blp.route("/questions")
class QuestionList(MethodView):
    @questions_blp.response(200, QuestionSchema(many=True))
    def get(self):
        """모든 질문 목록 조회"""
        return Question.query.all()

    @questions_blp.arguments(QuestionSchema)
    @questions_blp.response(201, QuestionSchema)
    def post(self, new_data):
        """새로운 질문 생성"""
        question = Question(**new_data)
        db.session.add(question)
        db.session.commit()
        return question