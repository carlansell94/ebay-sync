#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from datetime import datetime

from .lib.api_request import APIrequest
from .lib.feedback import Feedback

class GetFeedback:
    def __init__(self, db, credentials):
        self.db = db
        self.credentials = credentials

    def fetch(self, order_id) -> bool:
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

        content = APIrequest.get_xml_content('GetFeedback', self.credentials, args)
        root = ET.fromstring(content)

        if root.findtext('{urn:ebay:apis:eBLBaseComponents}Ack') == 'Failure':
            self.error(root)
            return False

        feedback = Feedback(self.db)
        feedback.set_legacy_order_id(order_id)

        for fb in root.iter('{urn:ebay:apis:eBLBaseComponents}FeedbackDetail'):
            feedback.set_feedback_id(fb.findtext(
                '{urn:ebay:apis:eBLBaseComponents}FeedbackID'
            ))

            feedback.set_comment(fb.findtext(
                '{urn:ebay:apis:eBLBaseComponents}CommentText'
            ))

            feedback.set_feedback_type(fb.findtext(
                '{urn:ebay:apis:eBLBaseComponents}CommentType'
            ))

            feedback.add()

        return True

    def error(self, response) -> None:
        dt = datetime.now()
        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")

        for error in response.iter('{urn:ebay:apis:eBLBaseComponents}Errors'):
            classification = error.findtext('{urn:ebay:apis:eBLBaseComponents}ErrorClassification')
            code = error.findtext('{urn:ebay:apis:eBLBaseComponents}ErrorCode')
            message = error.findtext('{urn:ebay:apis:eBLBaseComponents}LongMessage')

            print(f"[{timestamp}] [ERROR] Unable to sync feedback. {classification}: {message} ({code})")
