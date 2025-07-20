from flask import render_template, Blueprint
from sqlalchemy import func
from config import db
from app.models import Answer, Choices, Question

stats_routes_blp = Blueprint('stats_routes', __name__)

def row_to_dict(row):
    """SQLAlchemy Row 객체를 딕셔너리로 변환"""
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}

# 1. 사용 중인 유저의 각 질문당 선택지 선택 비율
@stats_routes_blp.route('/stats/answer_rate_by_choice', methods=['GET'])
def user_answer_rate():
    try:
        answer_rate_by_choice_raw = db.session.query(
            Question.id.label('question_id'),
            Choices.id.label('choice_id'),
            func.count(Answer.id).label('answer_count'),
            (func.count(Answer.id) * 100.0 / func.sum(func.count(Answer.id)).over()).label('percentage')
        ).join(Choices, Choices.id == Answer.choice_id) \
         .join(Question, Question.id == Choices.question_id) \
         .group_by(Question.id, Choices.id) \
         .order_by(Question.id, Choices.id) \
         .all()

        answer_rate_by_choice_data = [
            {
                "question_id": row.question_id,
                "choice_id": row.choice_id,
                "answer_count": row.answer_count,
                "percentage": round(row.percentage, 2)
            }
            for row in answer_rate_by_choice_raw
        ]

        answer_count_by_question_raw = db.session.query(
            Question.id.label('question_id'),
            Choices.id.label('choice_id'),
            func.count(Answer.id).label('answer_count'),
            (func.count(Answer.id) * 100.0 / func.sum(func.count(Answer.id)).over(partition_by=Question.id)).label('percentage')
        ).join(Choices, Choices.id == Answer.choice_id) \
         .join(Question, Question.id == Choices.question_id) \
         .group_by(Question.id, Choices.id) \
         .order_by(Question.id, Choices.id) \
         .all()

        answer_count_by_question_data = [
            {
                "question_id": row.question_id,
                "choice_id": row.choice_id,
                "answer_count": row.answer_count,
                "percentage": round(row.percentage, 2)
            }
            for row in answer_count_by_question_raw
        ]

        return render_template(
            "stats.html",
            answer_rate_by_choice=answer_rate_by_choice_data,
            answer_count_by_question=answer_count_by_question_data
        ), 200
    except Exception as e:
        # 에러 발생 시 stats.html을 렌더링하고 에러 메시지를 전달
        return render_template("stats.html", error_message=str(e)), 500