from sqlalchemy import Column, DateTime, Integer, String, ForeignKey

from app.model.db import seq
from .entity_base import EntityBase


class Mark(EntityBase):
    __tablename__ = 'mark'

    mark_id = Column(Integer, seq, primary_key=True)
    criteria_id = Column(Integer, ForeignKey('criteria.criteria_id'))
    staff_id = Column(Integer, ForeignKey('staff.id'))
    solution_id = Column(Integer, ForeignKey('solution.solution_id'))
    score = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)

    create_date = Column(DateTime, default=EntityBase.now)
    update_date = Column(DateTime, default=EntityBase.now, onupdate=EntityBase.now)
    last_change_by_id = Column(Integer)

    serialize_items_list = ['mark_id', 'criteria_id', 'staff_id', 'solution_id', 'score', 'comment',
                            'create_date', 'update_date', 'last_change_by_id']

    update_fields = ['score', 'comment', 'last_change_by_id']

    update_simple_fields = ['score', 'comment', 'last_change_by_id']

    @classmethod
    def get_mark_by_id(cls, mark_id):
        return cls.dict_item(cls.query.filter_by(mark_id=mark_id).first())

    get_item_by_id = get_mark_by_id

    @classmethod
    def get_marks_by_solution(cls, solution_id):
        return [cls.dict_item(mark) for mark in cls.query.filter_by(solution_id=solution_id)]

    @classmethod
    def get_marks_by_solution_and_staff(cls, solution_id, staff_id):
        return [cls.dict_item(mark) for mark in cls.query.filter_by(solution_id=solution_id, staff_id=staff_id)]

    @classmethod
    def get_marks_by_solution_and_criteria(cls, solution_id, criteria_id):
        return [cls.dict_item(mark) for mark in cls.query.filter_by(solution_id=solution_id, criteria_id=criteria_id)]

    @classmethod
    def create(cls, data):
        mark = cls(criteria_id=data['criteria_id'], staff_id=data['staff_id'], solution_id=data['solution_id'],
                   score=data['score'], comment=data['comment'], last_change_by_id=data['last_change_by_id'])

        mark.add()
        mark_dict = mark.to_dict()

        return mark_dict

    @classmethod
    def update(cls, data):
        mark_dict = cls.get_mark_by_id(data['mark_id'])

        if mark_dict is None:
            return None, f'Mark with id {data["mark_id"]} was not found'

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
        return None, f'Mark with id {mark_id} was not found'

    @classmethod
    def delete_by_solution(cls, solution_id):
        marks = cls.get_marks_by_solution(solution_id)
        for mark in marks:
            cls._delete(mark)
