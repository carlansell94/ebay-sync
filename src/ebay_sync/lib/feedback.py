#!/usr/bin/env python3

from dataclasses import dataclass

from .logger import Logger

@dataclass
class Feedback():
    db: any
    id: int = None
    legacy_order_id: str = None
    _comment_type: str = None
    _comment: str = None
    _valid: bool = True

    @property
    def comment_type(self):
        return self._comment_type

    @comment_type.setter
    def comment_type(self, comment_type: str):
        try:
            assert(comment_type in ('Positive','Neutral','Negative','Withdrawn'))
            self._comment_type = comment_type
        except AssertionError:
            msg = (f"""Invalid comment type '{comment_type}' for feedback """
                   f"""id {self.id}.""")
            Logger.create_entry(message=msg, entry_type="warn")
            self._valid = False

    @property
    def comment(self):
        return self._comment

    @comment.setter
    def comment(self, comment: str):
        self._comment = comment.encode("utf-8")
    
    @property
    def valid(self):
        return self._valid

    def exists(self):
        query = self.db.cursor()
        query.execute("""
            SELECT
                feedback_id
            FROM
                feedback
            WHERE
                feedback_id = %(id)s
        """, {
            'id': self.id
        })

        return query.fetchone()

    def add(self) -> bool:
        query = self.db.cursor()

        try:
            query.execute("""
                INSERT INTO feedback (
                    feedback_id,
                    legacy_order_id,
                    feedback_type,
                    comment
                ) VALUES (
                    %(feedback_id)s, 
                    %(legacy_order_id)s,
                    %(comment_type)s,
                    %(comment)s
                )
            """, {
                'feedback_id': self.id,
                'legacy_order_id': self.legacy_order_id,
                'comment_type': self.comment_type,
                'comment': self.comment
            })
        except self.db.OperationalError as error:
            msg = (f"""Unable to add feedback record for feedback id """
                   f"""'{self.id}'. Message: {error}.""")
            Logger.create_entry(message=msg, entry_type="error")
            return False

        return True

    def update(self) -> bool:
        query = self.db.cursor()

        try:
            query.execute("""
                UPDATE
                    feedback
                SET
                    feedback_type = %(comment_type)s,
                    comment = %(comment)s
                WHERE
                    feedback_id = %(feedback_id)s
            """, {
                'comment_type': self.comment_type,
                'comment': self.comment,
                'feedback_id': self.id
            })
        except self.db.OperationalError as error:
            msg = (f"""Unable to update feedback record for feedback id """
                   f"""'{self.id}'. Message: {error}.""")
            Logger.create_entry(message=msg, entry_type="error")
            return False

        return True
