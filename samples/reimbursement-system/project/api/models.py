# project/api/models.py


import datetime

from project import db


class Event(db.Model):
    __tableevents_ = "events"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_id = db.Column(db.Integer, db.ForeignKey('type.id'), nullable=False)
    caregiver_id = db.Column(db.Integer, index=True, nullable=False)
    start_time = db.Column(db.DateTime, index=True, nullable=False)  # time IRL
    reimbursed = db.Column(db.Boolean, index=True, default=False,
                           nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)  # time is introduced

    def __init__(self, type_id, caregiver_id, start_time, reimbursed=False):
        self.type_id = type_id
        self.caregiver_id = caregiver_id
        self.start_time = start_time
        self.reimbursed = reimbursed
        self.created_at = datetime.datetime.now()


class Type(db.Model):
    __tabletypes_ = "types"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(), index=True, unique=True, nullable=False)
    amount_in_cents = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), default="SEK", nullable=False)

    def __init__(self, name, amount_in_cents, currency="SEK"):
        self.name = name
        self.amount_in_cents = amount_in_cents
        self.currency = currency
