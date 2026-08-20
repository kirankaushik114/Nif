import os

from dotenv import load_dotenv
from twilio.rest import Client


load_dotenv()


class WhatsAppNotifier:

    def __init__(self):

        self.account_sid = os.getenv(
            "TWILIO_ACCOUNT_SID"
        )

        self.auth_token = os.getenv(
            "TWILIO_AUTH_TOKEN"
        )

        self.from_number = os.getenv(
            "TWILIO_WHATSAPP_FROM"
        )

        self.recipients = [
            os.getenv("TWILIO_WHATSAPP_TO_1"),
            os.getenv("TWILIO_WHATSAPP_TO_2"),
        ]

        self.recipients = [
            number
            for number in self.recipients
            if number
        ]

        if not self.account_sid:
            raise ValueError(
                "TWILIO_ACCOUNT_SID is missing."
            )

        if not self.auth_token:
            raise ValueError(
                "TWILIO_AUTH_TOKEN is missing."
            )

        if not self.from_number:
            raise ValueError(
                "TWILIO_WHATSAPP_FROM is missing."
            )

        if not self.recipients:
            raise ValueError(
                "No WhatsApp recipients configured."
            )

        self.client = Client(
            self.account_sid,
            self.auth_token,
        )

    def send(self, message):

        results = []

        for recipient in self.recipients:

            response = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=recipient,
            )

            results.append(response.sid)

        return results