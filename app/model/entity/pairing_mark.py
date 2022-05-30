from sqlalchemy import Column, DateTime, Integer, String, ForeignKey

from app.model.db import seq
from .entity_base import EntityBase


class PairingMark(EntityBase):
    __tablename__ = 'pairing_mark'

    pairing_mark_id = Column(Integer, seq, primary_key=True)
    criteria_id = Column(Integer, ForeignKey('criteria.criteria_id'))
    staff_id = Column(Integer, ForeignKey('staff.id'))
    first_solution_id = Column(Integer, ForeignKey('solution.solution_id'))
    second_solution_id = Column(Integer, ForeignKey('solution.solution_id'))
    event_id = Column(Integer, ForeignKey('Event.event_id'))
    score = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)

    create_date = Column(DateTime, default=EntityBase.now)
    update_date = Column(DateTime, default=EntityBase.now, onupdate=EntityBase.now)
    last_change_by_id = Column(Integer)

    serialize_items_list = ['pairing_mark_id', 'criteria_id', 'staff_id', 'first_solution_id', 'second_solution_id',
                            'event_id', 'score', 'comment', 'create_date', 'update_date', 'last_change_by_id']

    update_fields = ['score', 'comment', 'last_change_by_id']

    update_simple_fields = ['score', 'comment', 'last_change_by_id']

    @classmethod
    def get_mark_by_id(cls, pairing_mark_id):
        return cls.dict_item(cls.query.filter_by(pairing_mark_id=pairing_mark_id).first())

    get_item_by_id = get_mark_by_id

    @classmethod
    def get_mark_by_ids_staff_and_criteria(cls, first_solution_id, second_solution_id, staff_id, criteria_id):
        return cls.dict_item(cls.query.filter(
            (((PairingMark.first_solution_id == first_solution_id)
                & (PairingMark.second_solution_id == second_solution_id))
            | ((PairingMark.first_solution_id == second_solution_id)
                & (PairingMark.second_solution_id == first_solution_id)))
             & (PairingMark.criteria_id == criteria_id)
            & (PairingMark.staff_id == staff_id)
        ).first())

    @classmethod
    def get_marks_by_solution(cls, solution_id):
        return [
            cls.dict_item(mark) for mark in cls.query.filter(
                ((PairingMark.first_solution_id == solution_id) | (PairingMark.second_solution_id == solution_id))
                & (PairingMark.score != -1)
            )]

    @classmethod
    def get_marks_by_solution_and_staff(cls, solution_id, staff_id):
        return [
            cls.dict_item(mark) for mark in cls.query.filter(
                ((PairingMark.first_solution_id == solution_id) | (PairingMark.second_solution_id == solution_id))
                & (PairingMark.staff_id == staff_id)
            )
        ]

    @classmethod
    def get_marks_by_solution_staff_and_criteria(cls, solution_id, staff_id, criteria_id):
        return [
            cls.dict_item(mark) for mark in cls.query.filter(
                ((PairingMark.first_solution_id == solution_id) | (PairingMark.second_solution_id == solution_id))
                & (PairingMark.criteria_id == criteria_id)
                & (PairingMark.staff_id == staff_id)
                & (PairingMark.score != -1)
            )
        ]

    @classmethod
    def get_marks_by_solution_and_criteria(cls, solution_id, criteria_id):
        return [
            cls.dict_item(mark) for mark in cls.query.filter(
                ((PairingMark.first_solution_id == solution_id) | (PairingMark.second_solution_id == solution_id))
                & (PairingMark.criteria_id == criteria_id)
            )
        ]

    @classmethod
    def automatic_create_mark(cls, payload, score, first_id):
        mark = cls.get_mark_by_ids_staff_and_criteria(
            payload['first_solution_id'], payload['second_solution_id'], payload['staff_id'], payload['criteria_id']
        )
        if mark['score'] != -1:
            return mark
        if mark['first_solution_id'] != first_id:
            score = 2 - score
        payload['comment'] = ''
        payload['score'] = score
        payload['pairing_mark_id'] = mark['pairing_mark_id']
        mark = cls.update(payload)
        return mark

    @classmethod
    def get_pair_for_marking(cls, staff_id, event_id):
        pair = cls.dict_item(cls.query.filter_by(staff_id=staff_id, event_id=event_id, score=-1).first())
        any_pair = cls.dict_item(cls.query.filter_by(staff_id=staff_id, event_id=event_id).first())
        if pair is not None:
            return pair
        if any_pair is None:
            return None
        return { 'all_marked': True }

    @classmethod
    def auto_create_marks(cls, data):
        first_solution_id = data['first_solution_id']
        second_solution_id = data['second_solution_id']
        staff_id = data['staff_id']
        score = data['score']
        criteria_id = data['criteria_id']

        mark_list = []

        first_solution_marks = cls.get_marks_by_solution_staff_and_criteria(first_solution_id, staff_id, criteria_id)
        second_solution_marks = cls.get_marks_by_solution_staff_and_criteria(second_solution_id, staff_id, criteria_id)
        for item in first_solution_marks:
            if item['first_solution_id'] == second_solution_id or item['second_solution_id'] == second_solution_id:
                print()
            elif item['first_solution_id'] == first_solution_id:
                if (score == 2 and (item['score'] <= 1)) or (score == 0 and (item['score'] >= 1)):
                    payload = data
                    payload['first_solution_id'] = item['second_solution_id']
                    mark = cls.automatic_create_mark(payload, score, payload['first_solution_id'])
                    mark_list.append(mark)
                elif score == 1:
                    payload = data
                    payload['first_solution_id'] = item['second_solution_id']
                    mark = cls.automatic_create_mark(payload, 2 - item['score'], payload['first_solution_id'])
                    mark_list.append(mark)
            else:
                if (score == 2 and (item['score'] >= 1)) or (score == 0 and (item['score'] <= 1)):
                    payload = data
                    payload['first_solution_id'] = item['first_solution_id']
                    mark = cls.automatic_create_mark(payload, score, payload['first_solution_id'])
                    mark_list.append(mark)
                elif score == 1:
                    payload = data
                    payload['first_solution_id'] = item['first_solution_id']
                    mark = cls.automatic_create_mark(payload, item['score'], payload['first_solution_id'])
                    mark_list.append(mark)
        for item in second_solution_marks:
            if item['first_solution_id'] == first_solution_id or item['second_solution_id'] == first_solution_id:
                print()
            elif item['first_solution_id'] == second_solution_id:
                if (score == 2 and (item['score'] >= 1)) or (score == 0 and (item['score'] <= 1)):
                    payload = data
                    payload['second_solution_id'] = item['second_solution_id']
                    mark = cls.automatic_create_mark(payload, score, payload['first_solution_id'])
                    mark_list.append(mark)
                elif score == 1:
                    payload = data
                    payload['second_solution_id'] = item['second_solution_id']
                    mark = cls.automatic_create_mark(payload, item['score'], payload['first_solution_id'])
                    mark_list.append(mark)
            else:
                if (score == 2 and (item['score'] <= 1)) or (score == 0 and (item['score'] >= 1)):
                    payload = data
                    payload['second_solution_id'] = item['first_solution_id']
                    mark = cls.automatic_create_mark(payload, score, payload['first_solution_id'])
                    mark_list.append(mark)
                elif score == 1:
                    payload = data
                    payload['second_solution_id'] = item['first_solution_id']
                    mark = cls.automatic_create_mark(payload, 2 - item['score'], payload['first_solution_id'])
                    mark_list.append(mark)
        return mark_list

    @classmethod
    def create(cls, data):
        mark = cls(criteria_id=data['criteria_id'], staff_id=data['staff_id'], event_id=data['event_id'],
                   first_solution_id=data['first_solution_id'], second_solution_id=data['second_solution_id'],
                   score=data['score'], comment=data['comment'], last_change_by_id=data['last_change_by_id'])

        mark.add()
        mark_dict = mark.to_dict()

        return mark_dict

    @classmethod
    def update_tree(cls, data):
        mark = cls.update(data)
        mark_list = cls.auto_create_marks(data)
        return mark, mark_list

    @classmethod
    def update(cls, data):
        mark_dict = cls.get_mark_by_id(data['pairing_mark_id'])

        if mark_dict is None:
            return None, f'Pair mark with id {data["pairing_mark_id"]} was not found'

        if not cls._is_update_fields(data):
            return mark_dict

        mark = cls.from_dict(mark_dict)
        mark._update_simple_fields(data)
        mark_dict = mark.to_dict()
        return mark_dict

    @classmethod
    def delete(cls, mark_id):
        mark_dict = cls.get_mark_by_id(mark_id)
        if mark_dict:
            cls._delete(mark_dict)
            return mark_dict
        return None, f'Pairing mark with id {mark_id} was not found'

    @classmethod
    def delete_by_solution(cls, solution_id):
        marks = cls.get_marks_by_solution(solution_id)
        for mark in marks:
            cls._delete(mark)
