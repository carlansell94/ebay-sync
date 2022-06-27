#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from lib.api_request import APIrequest
from lib.feedback import Feedback

class getFeedback:
    def __init__(self, db, credentials):
        self.db = db
        self.credentials = credentials

    def fetch(self, order_id):
        item_id, transaction_id = order_id.split('-')

        args = (
            "<DetailLevel>ReturnAll</DetailLevel>"
            "<EntriesPerPage>200</EntriesPerPage>"
            "<FeedbackType>FeedbackReceivedAsSeller</FeedbackType>"
            f"<ItemID>{item_id}</ItemID>"
            f"<TransactionID>{transaction_id}</TransactionID>"
            "<OutputSelector>CommentType</OutputSelector>"
            "<OutputSelector>CommentText</OutputSelector>"
            "<OutputSelector>FeedbackID</OutputSelector>"
        )

        content = APIrequest.getXMLContent('GetFeedback', self.credentials, args)
        root = ET.fromstring(content)

        feedback = Feedback(self.db)
        feedback.setLegacyOrderId(order_id)

        for fb in root.iter('{urn:ebay:apis:eBLBaseComponents}FeedbackDetail'):
            feedback.setFeedbackId(fb.findtext(
                '{urn:ebay:apis:eBLBaseComponents}FeedbackID'
            ))

            feedback.setComment(fb.findtext(
                '{urn:ebay:apis:eBLBaseComponents}CommentText'
            ))

            feedback.setFeedbackType(fb.findtext(
                '{urn:ebay:apis:eBLBaseComponents}CommentType'
            ))

            feedback.add()
