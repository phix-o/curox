cd backend/live

. ./venv/bin/activate
git checkout dev
git pull

pip install -r requirements.txt
alembic upgrade head
