#!/usr/bin/env python3

class Feedback():
    def __init__(self, db):
        self.db = db

    def setLegacyOrderId(self, value):
        self.legacy_order_id = value
        return self

    def setFeedbackId(self, value):
        self.feedback_id = value
        return self

    def setFeedbackType(self, value):
        self.feedback_type = value
        return self

    def setComment(self, value):
        self.comment = value.encode("utf-8")
        return self

    def add(self):
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
