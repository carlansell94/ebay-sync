#!/usr/bin/env python3

import xml.etree.ElementTree as ET
from datetime import datetime

from .lib.api_request import APIrequest
from .lib.feedback import Feedback

class GetFeedback:
    ns = {'ebay_ns': 'urn:ebay:apis:eBLBaseComponents'}

    def __init__(self, db, credentials):
        self.db = db
        self.credentials = credentials

    def fetch(self, order_id) -> bool:
        item_id, transaction_id = order_id.split('-')

        args = (
            "<DetailLevel>ReturnAll</DetailLevel>"
            "<FeedbackType>FeedbackReceivedAsSeller</FeedbackType>"
            f"<ItemID>{item_id}</ItemID>"
            f"<TransactionID>{transaction_id}</TransactionID>"
            "<OutputSelector>CommentType</OutputSelector>"
            "<OutputSelector>CommentText</OutputSelector>"
            "<OutputSelector>FeedbackID</OutputSelector>"
        )

        content = APIrequest.get_xml_content('GetFeedback', self.credentials,
                                             args)
        response = ET.fromstring(content)

        if response.find('ebay_ns:Ack', self.ns).text == 'Failure':
            self.error(response)
            return False

        if fb_detail := response.find('.//ebay_ns:FeedbackDetail', self.ns):
            feedback = Feedback(self.db)
            feedback.set_legacy_order_id(order_id)

            feedback.set_feedback_id(fb_detail.find(
                'ebay_ns:FeedbackID', self.ns
            ).text)

            feedback.set_comment(fb_detail.find(
                'ebay_ns:CommentText', self.ns
            ).text)

            feedback.set_feedback_type(fb_detail.find(
                'ebay_ns:CommentType', self.ns
            ).text)

            feedback.add()

        return True

    def error(self, response) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for error in response.findall('ebay_ns:Errors', self.ns):
            classification = error.find(
                'ebay_ns:ErrorClassification', self.ns
            ).text
            code = error.find('ebay_ns:ErrorCode', self.ns).text
            message = error.find('ebay_ns:LongMessage', self.ns).text

            print(f"""[{timestamp}] [ERROR] Unable to sync feedback. """
                  f"""{classification}: {message} ({code})""")
