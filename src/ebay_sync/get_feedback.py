#!/usr/bin/env python3

import xml.etree.ElementTree as ET

from .lib.api_request import APIrequest
from .lib.feedback import Feedback
from .lib.logger import Logger

class GetFeedback:
    ns = {'ebay_ns': 'urn:ebay:apis:eBLBaseComponents'}

    def __init__(self, db, credentials):
        self.db = db
        self.credentials = credentials

    def fetch(self, order_id):
        self.order_id = order_id
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
        else:
            return response

    def parse(self, record) -> None:
        if fb_detail := record.find('.//ebay_ns:FeedbackDetail', self.ns):
            feedback = Feedback(self.db)
            feedback.legacy_order_id = self.order_id

            feedback.feedback_id = fb_detail.find(
                'ebay_ns:FeedbackID', self.ns
            ).text

            feedback.comment = fb_detail.find(
                'ebay_ns:CommentText', self.ns
            ).text

            feedback.comment_type = fb_detail.find(
                'ebay_ns:CommentType', self.ns
            ).text

            if not feedback.valid:
                msg = (f"Unable to add feedback id {feedback.feedback_id}.")
                Logger.create_entry(message=msg, entry_type="error")
                return
            
            if feedback.exists():
                success = feedback.update()
            else:
                success = feedback.add()
            
            if not success:
                msg = (f"Unable to add feedback id {feedback.feedback_id}.")
                Logger.create_entry(message=msg, entry_type="error")

    def error(self, response) -> None:
        for error in response.findall('ebay_ns:Errors', self.ns):
            classification = error.find(
                'ebay_ns:ErrorClassification', self.ns
            ).text
            code = error.find('ebay_ns:ErrorCode', self.ns).text
            message = error.find('ebay_ns:LongMessage', self.ns).text

            msg = (f"""Unable to sync feedback. {classification}: """
                   f"""{message} ({code})""")
            Logger.create_entry(message=msg, entry_type="error")
