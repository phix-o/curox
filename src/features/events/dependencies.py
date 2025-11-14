
from typing import Annotated

from fastapi import Depends

from src.common.repo import get_repo
from src.features.events.repo import (AttendeesRepo, EventsRepo,
                                      EventTablesRepo, TicketsRepo)

EventsRepoDep = Annotated[EventsRepo, Depends(get_repo(EventsRepo))]
TicketsRepoDep = Annotated[TicketsRepo, Depends(get_repo(TicketsRepo))]
AttendeesRepoDep = Annotated[AttendeesRepo, Depends(get_repo(AttendeesRepo))]
EventTablesRepoDep = Annotated[EventTablesRepo, Depends(get_repo(EventTablesRepo))]


