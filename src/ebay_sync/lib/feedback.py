#!/usr/bin/env python3

class Feedback():
    def __init__(self, db) -> None:
        self.db = db
        self.legacy_order_id = None
        self.feedback_id = None
        self.feedback_type = None
        self.comment = None

    def set_legacy_order_id(self, value: str):
        self.legacy_order_id = value
        return self

    def set_feedback_id(self, value: int):
        self.feedback_id = value
        return self

    def set_feedback_type(self, value: str):
        self.feedback_type = value
        return self

    def set_comment(self, value: str):
        self.comment = value.encode("utf-8")
        return self

    def add(self) -> None:
        query = self.db.cursor()
        query.execute("""
            INSERT INTO feedback (
                feedback_id,
                legacy_order_id,
                feedback_type,
                comment
            ) VALUES (
                %(feedback_id)s, 
                %(legacy_order_id)s,
                %(feedback_type)s,
                %(comment)s
            ) ON DUPLICATE KEY UPDATE
                feedback_type=VALUES(feedback_type),
                comment=VALUES(comment)
        """, {
            'feedback_id': self.feedback_id, 
            'legacy_order_id': self.legacy_order_id,
            'feedback_type': self.feedback_type,
            'comment': self.comment
        })

        self.db.commit()
