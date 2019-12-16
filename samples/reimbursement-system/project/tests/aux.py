# project/tests/aux.py


import datetime

from project import db
from project.api.models import Event, Type


def add_event_type(name, amount_in_cents, currency="SEK"):
    event_type = Type(name=name,
                      amount_in_cents=amount_in_cents,
                      currency=currency)
    db.session.add(event_type)
    db.session.commit()
    return event_type


def add_event(type_id,
              caregiver_id,
              start_time=datetime.datetime.now(),
              reimbursed=False):
    event = Event(type_id=type_id,
                  caregiver_id=caregiver_id,
                  start_time=start_time,
                  reimbursed=reimbursed)
    db.session.add(event)
    db.session.commit()
    return event
