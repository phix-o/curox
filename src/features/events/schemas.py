from datetime import datetime

from pydantic import BaseModel, Field

from src.common.schemas import BaseModelSchema
from src.features.auth.schemas import UserSchema


class EventSchemaBase(BaseModel):
    name: str                   = Field(description='The name of the event',
                                    examples=['My Event'])
    description: str | None     = Field(default=None,
                                    description='The description of the event',
                                    examples=['My super event'])
    date_from: datetime         = Field(description='The date of the event')
    date_to: datetime | None    = Field(description='The date of the event')

class EventCreateSchema(EventSchemaBase):
    '''
    Used to validate EventModel creation data
    '''

    venue: str          = Field(description='The venue of the event',
                                examples=['The Plaza'])
    company_id: int     = Field(description='The company id that this event should belong',
                                examples=[1])
    tables: list[str]   = Field(description='The number of tables for this event',
                                examples=[['Table 1', 'Table 2']])

class EventSchema(BaseModelSchema, EventSchemaBase):
    '''
    Used to return a shallow EventModel
    '''
    pass

class EventDetailsSchema(EventSchema):
    '''
    Used to return a shallow EventModel
    '''
    venue: str             = Field(description='The venue of the event',
                                   examples=['The Plaza'])
    created_by: UserSchema = Field(description='Who created this event')


class EventTableSchema(BaseModelSchema):
    '''
    Serializes an event table tuple
    '''
    name: str = Field(description='The table name')

class EventTicketSchema(BaseModelSchema):
    '''
    Serializes an event ticket tuple
    '''
    code: str                   = Field(description='The unique ticket code',
                                        examples=['45CXY8'])
    sent_at: datetime | None    = Field(default=None,
                                        description='When this ticket was sent to the attendee')
    scanned_at: datetime | None = Field(default=None,
                                        description='When this ticket was scanned')
    table: EventTableSchema     = Field(description='The table this ticket belongs to')


class EventAttendeeBase(BaseModel):
    name: str                   = Field(description='The attendees name',
                                        examples=['Jane Doe'])
    email: str                  = Field(description='The attendees email address',
                                        examples=['attendee@ac.ac'])
    phone_number: str | None    = Field(default=None,
                                        description='The attendees phone number',
                                        examples=['254700000000'])
class EventAttendeeSchema(EventAttendeeBase, BaseModelSchema):
    '''
    Serializes an event attendee
    '''
    ticket: EventTicketSchema   = Field(description='The attendees ticket')
class EventAttendeeCreateSchema(EventAttendeeBase):
    '''
    Used to create an event attendee
    '''
    price: int              = Field(description='The ticket price this attendee paid',
                                    examples=[2000])
    table_id: int | None    = Field(default=None,
                                    description='The table id that this attendee is assigned',
                                    examples=[1])
