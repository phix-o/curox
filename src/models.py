'''
This file is used by the database module to ensure that the
Base.metadata is populated with the models that alembic tracks for
autogenerating timestamps
'''

from src.features.auth.models import *
from src.features.companies.models import *
from src.features.events.models import *
