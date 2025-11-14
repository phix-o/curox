# Curox
An event management system

## Installing dependencies
You can use a virtual environment manager of your choice, but [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) is recommended.

Assuming you are using `virtualenvwrapper`, create and activate your virtual environment:
```sh
# Make virtual environment
mkvirtualenv events

# Activate virtual environment
workon events
```

Install dependencies by running:
```sh
poetry install
```

## Running the project
To run the project, run the migrations first in your virtual environment:
```sh
alembic upgrade head
```

Then run the server:
```sh
fastapi dev src/main.py
```

### Migrations
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
workon curiox             # Activate the virtual environment
pytest
```

