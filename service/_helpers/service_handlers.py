import os
from dotenv import load_dotenv
from mailjet_rest import Client

load_dotenv()


class Mailjet:
    API_KEY = os.getenv("MAILJET__API_KEY")
    API_SECRET = os.getenv("MAILJET__API_SECRET")
    mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')

    def send_mail(self, email_data) -> None:
        data = self.generate_data(email_data)
        result = self.mailjet.send.create(data=data)

        self.status_code = result.status_code
        self.result = result.json()

    def generate_data(self, email_data) -> dict:
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": email_data.user.email,
                        "Name": email_data.user.get_full_name()
                    },
                    "To": self.set_receiver_details(email_data.to),
                    "CC": self.set_receiver_details(email_data.cc),
                    "BCC": self.set_receiver_details(email_data.bcc),
                    "Subject": email_data.subject,
                    "TextPart": email_data.message,
                    "CustomID": "AppGettingStartedTest"
                }
            ]
        }

        return data

    def set_receiver_details(self, emails) -> list:
        receivers = []

        for receiver in emails:
            details = {
                "Email": receiver,
                "Name": "Receiver"
            }
            receivers.append(details)

        return receivers
