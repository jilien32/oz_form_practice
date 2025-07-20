from datetime import datetime
from enum import Enum
from zoneinfo import ZoneInfo

from config import db

KST = ZoneInfo("Asia/Seoul")

class CommonModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(tz=KST), nullable=False
    )
    updated_at = db.Column(
        db.DateTime, default=lambda: datetime.now(tz=KST),
        onupdate=lambda: datetime.now(tz=KST), nullable=False
    )


class AgeStatus(Enum):
    teen = "teen"
    twenty = "twenty"
    thirty = "thirty"
    forty = "forty"
    fifty = "fifty"


class GenderStatus(Enum):
    male = "male"
    female = "female"


class ImageStatus(Enum):
    main = "main"
    sub = "sub"


class User(CommonModel):
    __tablename__ = "users"
    name = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Enum(AgeStatus), nullable=False)
    gender = db.Column(db.Enum(GenderStatus), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age.value if hasattr(self.age, "value") else self.age,
            "gender": (
                self.gender.value if hasattr(self.gender, "value") else self.gender
            ),
            "email": self.email,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Image(CommonModel):
    __tablename__ = "images"
    url = db.Column(db.String(255), nullable=False)
    type = db.Column(db.Enum(ImageStatus), nullable=False)

    questions = db.relationship("Question", back_populates="image")

    def to_dict(self):
        return {
            "id": self.id,
            "url": self.url,
            "type": self.type.value if hasattr(self.type, "value") else self.type,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Question(CommonModel):
    __tablename__ = "questions"
    title = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    sqe = db.Column(db.Integer, nullable=False)

    image_id = db.Column(db.Integer, db.ForeignKey("images.id"), nullable=False)

    image = db.relationship("Image", back_populates="questions")
    choices = db.relationship("Choices", back_populates="question", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "is_active": self.is_active,
            "sqe": self.sqe,
            "image": self.image.to_dict() if self.image else None,
            "choices": [choice.to_dict() for choice in self.choices],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Choices(CommonModel):
    __tablename__ = "choices"
    content = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    sqe = db.Column(db.Integer, nullable=False)

    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
    question = db.relationship("Question", back_populates="choices")

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "is_active": self.is_active,
            "sqe": self.sqe,
            "question_id": self.question_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class Answer(CommonModel):
    __tablename__ = "answers"
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    choice_id = db.Column(db.Integer, db.ForeignKey("choices.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "choice_id": self.choice_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }