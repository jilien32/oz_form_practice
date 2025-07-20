import os
from flask import request, jsonify, redirect, url_for, session, render_template
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from marshmallow import Schema, fields

from app.models import Answer, User, AgeStatus, GenderStatus, Question, Choices
from config import db


class AnswerSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    choice_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    age = fields.Str(required=True)
    gender = fields.Str(required=True)
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


answers_blp = Blueprint("answers", __name__, url_prefix="/answers", description="Operations on answers")


@answers_blp.route("/")
class AnswerList(MethodView):
    @answers_blp.response(200, AnswerSchema(many=True))
    def get(self):
        """모든 답변 목록 조회"""
        return Answer.query.all()

    @answers_blp.arguments(AnswerSchema)
    @answers_blp.response(201, AnswerSchema)
    def post(self, new_data):
        """새로운 답변 생성"""
        answer = Answer(**new_data)
        db.session.add(answer)
        db.session.commit()
        return answer


@answers_blp.route("/submit_answer", methods=["POST"])
def submit_answer():
    """각 질문의 답변을 처리하고 다음 질문 또는 MBTI 분석 페이지로 리다이렉트"""
    if "user_id" not in session:
        return redirect(url_for("questions.show_start_page"))

    user_id = session["user_id"]
    question_id = request.form["question_id"]
    choice_id = request.form["choice_id"]
    current_question_sqe = int(request.form["question_sqe"])

    answer = Answer(user_id=user_id, choice_id=choice_id)
    db.session.add(answer)
    db.session.commit()

    next_question_sqe = current_question_sqe + 1
    next_question = Question.query.filter_by(sqe=next_question_sqe, is_active=True).first()

    if next_question:
        session["current_question_sqe"] = next_question_sqe
        return redirect(url_for("questions.show_question", question_sqe=next_question_sqe))
    else:
        # 모든 질문에 답변 완료, MBTI 분석 페이지로 리다이렉트
        return redirect(url_for("answers.analyze_mbti"))


@answers_blp.route("/mbti_result")
def analyze_mbti():
    if "user_id" not in session:
        return redirect(url_for("questions.show_start_page"))

    user_id = session["user_id"]
    user_answers = Answer.query.filter_by(user_id=user_id).all()

    # MBTI 성향 카운트 초기화
    mbti_scores = {"E": 0, "I": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}

    # 질문 sqe별로 MBTI 성향 매핑
    mbti_mapping = {
        1: {1: "E", 2: "E", 3: "I", 4: "I"},
        2: {1: "S", 2: "S", 3: "N", 4: "N"},
        3: {1: "T", 2: "T", 3: "F", 4: "F"},
        4: {1: "J", 2: "J", 3: "P", 4: "P"},
        5: {1: "N", 2: "S", 3: "F", 4: "T"},  # 보조 질문
    }

    for answer in user_answers:
        choice = Choices.query.filter_by(id=answer.choice_id).first()
        if not choice:
            continue
        question = Question.query.filter_by(id=choice.question_id).first()
        if not question:
            continue

        q_sqe = question.sqe
        c_sqe = choice.sqe
        trait = mbti_mapping.get(q_sqe, {}).get(c_sqe)
        if trait:
            mbti_scores[trait] += 1

    # MBTI 결정
    mbti_type = (
        ("E" if mbti_scores["E"] >= mbti_scores["I"] else "I") +
        ("S" if mbti_scores["S"] >= mbti_scores["N"] else "N") +
        ("T" if mbti_scores["T"] >= mbti_scores["F"] else "F") +
        ("J" if mbti_scores["J"] >= mbti_scores["P"] else "P")
    )

    mbti_descriptions = {
    "ISTJ": "신중하고 책임감 있는 원칙주의자. 조직과 규칙을 존중하며 계획적으로 움직이는 완벽주의자입니다. (셀린)",
    "ISFJ": "헌신적이고 따뜻한 수호자. 조용하고 배려 깊으며 타인의 행복을 위해 헌신하는 성향입니다. (해당 캐릭터 없음)",
    "INFJ": "이상주의적이고 깊이 있는 조용한 리더. 타인의 고통에 공감하며 세상을 더 나은 곳으로 만들고자 합니다. (루미)",
    "INTJ": "전략적 사고를 가진 조용한 설계자. 독립적이고 비전을 바탕으로 미래를 계획하는 분석가입니다. (서씨)",
    "ISTP": "관찰력과 실용성의 대가. 조용하지만 상황에 빠르게 적응하며 도전적인 행동가입니다. (이라)",
    "ISFP": "자유롭고 감성적인 예술가. 조용하지만 섬세한 미적 감각과 감정의 깊이를 지닌 성향입니다. (베이비)",
    "INFP": "이상과 가치로 움직이는 중재자. 내면의 신념과 감정을 따르며 조용히 타인을 위로합니다. (더피)",
    "INTP": "호기심 많은 사색가. 복잡한 개념을 즐기고 논리로 세상을 이해하려는 지적 탐구자입니다. (미스터리)",
    "ESTP": "현실적이고 모험적인 행동파. 도전을 두려워하지 않고 순간을 즐기는 에너지 넘치는 성향입니다. (매비)",
    "ESFP": "주목받는 걸 즐기는 분위기 메이커. 밝고 사교적이며 모두에게 즐거움을 주는 성격입니다. (로맨스)",
    "ENFP": "창의적이고 열정적인 아이디어 뱅크. 새로운 사람과 경험을 좋아하며 에너지와 감성이 풍부합니다. (조이)",
    "ENTP": "도전을 즐기고 아이디어가 넘치는 혁신가. 논쟁을 즐기며 재치 있는 변화를 이끄는 리더형입니다. (진우)",
    "ESTJ": "체계적이고 명확한 지휘관. 규칙과 효율을 중시하며 조직을 정비하는 능력이 뛰어납니다. (해당 캐릭터 없음)",
    "ESFJ": "친절하고 책임감 강한 돌봄형 리더. 사람들과 잘 어울리며 공동체를 조화롭게 만드는 데 탁월합니다. (바비)",
    "ENFJ": "카리스마 있는 사회운동가. 타인의 성장을 이끌고 세상을 변화시키는 데 관심이 많은 리더입니다. (해당 캐릭터 없음)",
    "ENTJ": "야망 있고 결단력 있는 통솔자. 목표를 향해 전략적으로 전진하는 강력한 리더십을 지녔습니다. (해당 캐릭터 없음)",
    }

    mbti_description = mbti_descriptions.get(mbti_type, "MBTI 설명 없음")
    has_character = "(해당 캐릭터 없음)" not in mbti_description

    image_filename = f"{mbti_type}.png"
    image_path = os.path.join(os.path.dirname(__file__), '..\static\images', image_filename)

    if os.path.exists(image_path):
        mbti_image_url = url_for('static', filename=f'images/{image_filename}')
    else:
        mbti_image_url = url_for('static', filename='images/Default.png') # 기본 이미지 파일명을 Default.png로 가정

    # 세션 초기화
    session.pop("user_id", None)
    session.pop("current_question_sqe", None)

    return render_template(
        "mbti_result.html",
        mbti_type=mbti_type,
        mbti_description=mbti_description,
        mbti_image_url=mbti_image_url,
        has_character=has_character
    )
