from datetime import datetime
from zoneinfo import ZoneInfo

from app import create_app  # Correct import
from config import db
from app.models import Question, Choices, Image, ImageStatus, User, Answer # Added Image, ImageStatus, User, Answer

def seed_data():
    app = create_app()
    with app.app_context():
        print("데이터베이스 시딩 시작...")

        # 기존 데이터 삭제 (FK 제약 조건 고려하여 순서 중요)
        db.session.query(Answer).delete()
        db.session.query(Choices).delete()
        db.session.query(Question).delete()
        db.session.query(User).delete()
        db.session.query(Image).delete()
        db.session.commit()

        # 새 데이터 정의
        questions_data = [
            {
                "title": "주말에 친구들과의 약속, 당신의 선택은?",
                "sqe": 1,
                "image_url": "/static/images/kpop1.jpg",
                "choices": [
                    "활기 넘치는 파티에 가서 새로운 사람들을 만난다.",
                    "친한 친구들과 소규모로 모여 깊은 대화를 나눈다.",
                    "집에서 혼자 좋아하는 영화를 보며 휴식을 취한다.",
                    "마음이 맞는 소수의 친구와 조용한 카페에서 시간을 보낸다."
                ]
            },
            {
                "title": "여행 계획을 세울 때 당신의 스타일은?",
                "sqe": 2,
                "image_url": "/static/images/kpop2.jpg",
                "choices": [
                    "가보고 싶은 곳 목록을 만들고 구체적인 일정을 짠다.",
                    "과거의 경험을 바탕으로 효율적인 동선을 계획한다.",
                    "전체적인 컨셉만 정하고, 현장에서 마음 가는 대로 움직인다.",
                    "새로운 가능성을 탐험하기 위해 즉흥적으로 결정한다."
                ]
            },
            {
                "title": "친구가 고민을 털어놓을 때 당신의 반응은?",
                "sqe": 3,
                "image_url": "/static/images/kpop3.jpg",
                "choices": [
                    "객관적인 사실을 바탕으로 현실적인 해결책을 제시한다.",
                    "친구의 감정에 공감하며 따뜻한 위로의 말을 건넨다.",
                    "문제의 원인을 논리적으로 분석하고 해결 과정을 설명한다.",
                    "상황에 대한 감정적인 지지를 표현하며 친구의 마음을 알아준다."
                ]
            },
            {
                "title": "업무를 처리할 때 당신이 선호하는 방식은?",
                "sqe": 4,
                "image_url": "/static/images/kpop4.jpg",
                "choices": [
                    "명확한 목표와 계획을 세워 체계적으로 처리한다.",
                    "정해진 절차와 규칙에 따라 꼼꼼하게 일을 완수한다.",
                    "상황에 따라 유연하게 대처하며 즉흥적으로 해결한다.",
                    "새로운 아이디어를 시도하며 자유롭게 일하는 것을 즐긴다."
                ]
            },
            {
                "title": "새로운 것을 배울 때 당신의 접근 방식은?",
                "sqe": 5,
                "image_url": "/static/images/kpop5.jpg",
                "choices": [
                    "미래의 가능성을 상상하며 창의적인 아이디어를 탐구한다.",
                    "실용적인 예시와 구체적인 데이터를 통해 단계적으로 학습한다.",
                    "개인의 감성과 가치를 중요하게 생각하며 의미를 찾는다.",
                    "논리적인 분석과 비평을 통해 체계적으로 지식을 습득한다."
                ]
            },
        ]

        # 질문과 선택지 삽입
        for q_data in questions_data:
            # 이미지 생성 또는 가져오기
            image = Image.query.filter_by(url=q_data["image_url"]).first()
            if not image:
                image = Image(url=q_data["image_url"], type=ImageStatus.main) # type은 예시로 main을 사용
                db.session.add(image)
                db.session.commit()

            question = Question(
                title=q_data["title"],
                sqe=q_data["sqe"],
                is_active=True,
                image_id=image.id,
            )

            for idx, choice_text in enumerate(q_data["choices"], start=1):
                choice = Choices(
                    content=choice_text,
                    is_active=True,
                    sqe=idx,
                )
                question.choices.append(choice)

            db.session.add(question)

        db.session.commit()
        print("기존 데이터를 삭제하고 새 질문/선택지를 삽입했습니다.")
        print("데이터베이스 시딩 완료!")

if __name__ == '__main__':
    seed_data()