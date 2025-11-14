from fastapi import UploadFile
import pendulum
from src.common.repo import RepoBase
from src.common.utils.token import generate_token
from src.features.auth.schemas import UserCreate

from .models import UserModel
from src.core.storage.backend import storage_backend

class UserRepo(RepoBase[UserModel]):
    model = UserModel

    def create_one(self, user: UserCreate):
        db_user = UserModel(**user.model_dump())
        db_user.set_password(user.password)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_avatar(self, user: UserModel, avatar: UploadFile):
        db = self.db

        url = None
        try:
            file_path = f'avatars/avatar_{user.id}_{avatar.filename}'
            path = storage_backend.upload_file(avatar.file, file_path)
            user.avatar_path = path
            db.add(user)
            db.commit()
        except Exception as e:
            db.rollback()
            raise e

        url = storage_backend.get_url(path)
        return url

    def update_password(self, user: UserModel, password: str):
        db = self.db

        user.set_password(password)
        user.password_reset_token = None
        user.password_reset_token_expiry = None

        db.add(user)
        db.commit()

    def generate_reset_token(self, user: UserModel):
        db = self.db

        token = generate_token()
        now = pendulum.now(pendulum.UTC)
        user.password_reset_token = token
        user.password_reset_token_expiry = now.add(minutes=5)

        db.add(user)
        db.commit()
        return token
