# project/api/views.py


import datetime
from flask import Blueprint, jsonify, request, make_response
from sqlalchemy import exc, text

from collections import defaultdict
from project.api.models import Event, Type
from project import db


def rec_dd():
    return defaultdict(rec_dd)


events_blueprint = Blueprint('events', __name__)


@events_blueprint.route('/ping', methods=['GET'])
def ping():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })


@events_blueprint.route('/events', methods=['POST'])
def add_event():
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400
    type_id = post_data.get('type_id')
    caregiver_id = post_data.get('caregiver_id')
    start_time = post_data.get('start_time')
    try:
        event = Event(type_id=type_id,
                      caregiver_id=caregiver_id,
                      start_time=start_time)
        db.session.add(event)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': 'Event created.',
            'id': event.id
        }
        return make_response(jsonify(response_object)), 201

    except exc.IntegrityError:
        db.session().rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400
    except Exception:  # other error e.g. invalid start_time
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400


@events_blueprint.route('/events/<event_id>', methods=['GET'])
def get_single_event(event_id):
    response_object = {
        'status': 'fail',
        'message': 'Event does not exist'
    }
    try:
        event = Event.query.filter_by(id=int(event_id)).first()
        if not event:
            return make_response(jsonify(response_object)), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': event.id,
                    'type_id': event.type_id,
                    'caregiver_id': event.caregiver_id,
                    'reimbursed': event.reimbursed,
                    'created_at': event.created_at
                }
            }
            return make_response(jsonify(response_object)), 200
    except ValueError:
        return make_response(jsonify(response_object)), 404


@events_blueprint.route('/events/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    response_object = {
        'status': 'fail',
        'message': 'Event does not exist'
    }
    event = Event.query.filter_by(id=int(event_id)).first()
    if not event:
        return make_response(jsonify(response_object)), 404
    else:
        db.session.delete(event)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': 'Event deleted.'
        }
        return make_response(jsonify(response_object)), 200


@events_blueprint.route('/events/<event_id>/reimburse', methods=['POST'])
def reimburse_event(event_id):
    response_object = {'status': 'fail', }

    event = Event.query.filter_by(id=int(event_id)).first()
    if not event:
        response_object["message"] = "Event does not exist"
        return make_response(jsonify(response_object)), 404
    if event.reimbursed:
        response_object["message"] = "Event already reimbursed"
        return make_response(jsonify(response_object)), 400

    event.reimbursed = True
    db.session.commit()
    response_object = {
        'status': 'success',
        'message': 'Event reimbursed.'
    }
    return make_response(jsonify(response_object)), 200


@events_blueprint.route('/events', methods=['GET'])
def get_all_events():
    events = Event.query.all()
    event_list = []
    for e in events:
        event_object = {
            'id': e.id,
            'type_id': e.type_id,
            'caregiver_id': e.caregiver_id,
            'reimbursed': e.reimbursed,
            'created_at': e.created_at
        }
        event_list.append(event_object)
    response_object = {
        'status': 'success',
        'data': {
            'events': event_list
        }
    }
    return make_response(jsonify(response_object)), 200


@events_blueprint.route('/events/types', methods=['POST'])
def add_event_type():
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400
    name = post_data.get('name')
    amount_in_cents = post_data.get('amount_in_cents')
    currency = post_data.get('currency', 'SEK')
    if currency != "SEK":
        response_object = {
            'status': 'fail',
            'message': 'Invalid currency.'
        }
        return make_response(jsonify(response_object)), 400

    try:
        etype = Type(name=name,
                     amount_in_cents=amount_in_cents,
                     currency=currency)
        db.session.add(etype)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': 'Event type created.',
            'id': etype.id
        }
        return make_response(jsonify(response_object)), 201

    except exc.IntegrityError:
        db.session().rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400


@events_blueprint.route('/events/types/<etype_id>', methods=['GET'])
def get_single_event_type(etype_id):
    response_object = {
        'status': 'fail',
        'message': 'Event type does not exist.'
    }
    try:
        etype = Type.query.filter_by(id=int(etype_id)).first()
        if not etype:
            return make_response(jsonify(response_object)), 404
        else:
            response_object = {
                'status': 'success',
                'data': {
                    'id': etype.id,
                    'name': etype.name,
                    'amount_in_cents': etype.amount_in_cents,
                    'currency': etype.currency
                }
            }
            return make_response(jsonify(response_object)), 200
    except ValueError:
        return make_response(jsonify(response_object)), 404


@events_blueprint.route('/events/types/<etype_id>', methods=['DELETE'])
def delete_event_type(etype_id):
    response_object = {
        'status': 'fail',
        'message': 'Event type does not exist.'
    }
    etype = Type.query.filter_by(id=int(etype_id)).first()
    if not etype:
        return make_response(jsonify(response_object)), 404

    try:
        db.session.delete(etype)
        db.session.commit()
        response_object = {
            'status': 'success',
            'message': 'Event type deleted.'
        }
        return make_response(jsonify(response_object)), 200
    except exc.IntegrityError:
        db.session().rollback()
        response_object = {
            'status': 'fail',
            'message': 'Event type is used in existing events.'
        }
        return make_response(jsonify(response_object)), 400


@events_blueprint.route('/events/types', methods=['GET'])
def get_all_event_types():
    etypes = Type.query.all()
    etype_list = []
    for e in etypes:
        etype_object = {
            'id': e.id,
            'name': e.name,
            'amount_in_cents': e.amount_in_cents,
            'currency': e.currency
        }
        etype_list.append(etype_object)
    response_object = {
        'status': 'success',
        'data': {
            'event_types': etype_list
        }
    }
    return make_response(jsonify(response_object)), 200


@events_blueprint.route('/events/report', methods=['GET', 'POST'])
def get_report_event_types():
    """
    outputs a report of events which consists of summed amounts in SEK
    by year>month>caregiver id. They are further grouped by reimbursion state.
    example output format of report field follows:
    report = {
        '2017': {
            'Jan': {
                caregiver_id1: {
                    'non-reimbursed SEK': 500,
                    'reimbursed SEK': 2500,
                }
                caregiver_id2: {
                    'reimbursed SEK': 1000,
                }
                caregiver_id3: {
                    'reimbursed SEK': 2500,
                }
            }
            'Feb': {
                caregiver_id1: {
                    'non-reimbursed SEK': 1500,
                }
                caregiver_id3: {
                    'reimbursed SEK': 3000,
                    'non-reimbursed SEK': 1000,
                }
            }
        }
    }

    accepts the following POST parameters which act as filters:
    - 'caregiver_ids': [3,4,5],  # includes only events for selected caregivers
    - 'min_time': '2017-10-28T23:28:23.456701',  # only events started after
    - 'max_time': '2017-10-28T23:28:23.456701',  # only events started before

    check project/tests/test_event_reports.py for more examples
    """
    post_data = request.get_json()
    where_clause = ""
    if post_data:
        where_clause = "WHERE 1 = 1 "
        if post_data.get('caregiver_ids'):
            where_clause += "AND e.caregiver_id = ANY(:caregiver_ids) "
        if post_data.get('min_time'):
            where_clause += "AND e.start_time > :min_time "
        if post_data.get('max_time'):
            where_clause += "AND e.start_time < :max_time "

    sql = text("""
        SELECT extract(year from e.start_time) as yyyy,
               to_char(e.start_time, 'Mon') as mon,
               e.caregiver_id,
               e.reimbursed,
               sum(t.amount_in_cents)/100
        FROM event e INNER JOIN type t
        ON e.type_id = t.id
        {}
        GROUP BY yyyy, mon, e.caregiver_id, e.reimbursed
        """.format(where_clause))
    try:
        result = db.session.execute(sql, post_data).fetchall()
    except Exception:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload.'
        }
        return make_response(jsonify(response_object)), 400

    report = rec_dd()
    for r in result:
        prefix = "" if r[3] else "non-"
        report[int(r[0])][r[1]][r[2]][prefix + "reimbursed SEK"] = r[4]

    response_object = {
        'status': 'success',
        'data': {
            'report': report,
            'generated_at': datetime.datetime.now()
        }
    }
    return make_response(jsonify(response_object)), 200
