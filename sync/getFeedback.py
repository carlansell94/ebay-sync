#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from core.xmlrequest import XMLRequest
from model.feedback import Feedback

class getFeedback:
    def __init__(self, db, credentials):
        self.db = db
        self.credentials = credentials

    def fetch(self, order_id):
        item_id = order_id.split('-')[0]
        transaction_id = order_id.split('-')[1]

        args = ('<DetailLevel>ReturnAll</DetailLevel><EntriesPerPage>200'
                + '</EntriesPerPage><FeedbackType>FeedbackReceivedAsSeller'
                + '</FeedbackType><ItemID>'
                + item_id
                + '</ItemID><TransactionID>'
                + transaction_id
                + '</TransactionID><OutputSelector>CommentType'
                + '</OutputSelector><OutputSelector>CommentText'
                + '</OutputSelector><OutputSelector>FeedbackID</OutputSelector>'
        )

        req = XMLRequest()
        res = req.getRequest('GetFeedback', args)
        root = ET.fromstring(res)

        feedback = Feedback(self.db)
        feedback.setLegacyOrderId(order_id)

        for fb in root.iter(tag='{urn:ebay:apis:eBLBaseComponents}FeedbackDetail'):
            for fb_id in fb.iter(tag='{urn:ebay:apis:eBLBaseComponents}FeedbackID'):
                feedback.setFeedbackId(fb_id.text)

            for comment in fb.iter(tag='{urn:ebay:apis:eBLBaseComponents}CommentText'):
                feedback.setComment(comment.text)

            for comment_type in fb.iter(tag='{urn:ebay:apis:eBLBaseComponents}CommentType'):
                feedback.setFeedbackType(comment_type.text)

            feedback.add()
