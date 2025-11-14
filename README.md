# Curox

An event management system

## Project setup

### Docker

If you prefer docker then follow the steps below:


```sh
docker compose up --build
```

### Manual

If you want to run it manually then you can follow this guide. Ensure you have [postgresql](https://www.postgresql.org) and [mailpit](https://mailpit.axllent.org) (or similar) installed.

#### Dependencies
You can use a virtual environment manager of your choice, but [uv](https://docs.astral.sh/uv) is recommended.

Assuming you are using `uv` and on a `linux` operating system, create and activate your virtual environment:
```sh
# Make virtual environment
uv venv

# Activate virtual environment
. .venv/bin/activate
```

Install dependencies by running:
```sh
uv sync
```

#### Running the project
To run the project, run the migrations first in your virtual environment:
```sh
alembic upgrade head
```

Then run the server:
```sh
fastapi run src/main.py --port 8000
```

#### Migrations
To create a new migration, ensure you model is imported in the `src/models.py` folder first, then run:
```sh
alembic revision --autogenerate -m '<migration-name>'
```

Check the geneated migration file in `alembic/revision` directory and verify the migration.  Run the
migration by doing:
```sh
alembic upgrade head
```

To undo a recent migration, do:
```sh
alembic donwgrade -1
```

## Testing
To run tests, run the following in the root directory of the project:
```sh
pytest
```

