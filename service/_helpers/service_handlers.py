import os
from dotenv import load_dotenv
from mailjet_rest import Client

from infobip_api_client.api_client import ApiClient, Configuration
from infobip_api_client.model.sms_advanced_textual_request import SmsAdvancedTextualRequest
from infobip_api_client.model.sms_destination import SmsDestination
from infobip_api_client.model.sms_response import SmsResponse
from infobip_api_client.model.sms_textual_message import SmsTextualMessage
from infobip_api_client.api.send_sms_api import SendSmsApi
from infobip_api_client.exceptions import ApiException

from mailing_system.common.services import Service


load_dotenv()


class Mailjet(Service):
    API_KEY = os.getenv("MAILJET__API_KEY")
    API_SECRET = os.getenv("MAILJET__API_SECRET")
    mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')

    def __init__(self, data) -> None:
        super().__init__(data)

    def format_data(self) -> dict:
        email_data = self.data

        data = {
            'Messages': [
                {
                    "From": {
                        "Email": email_data.user.email,
                        "Name": email_data.user.get_full_name()
                    },
                    "To": self.get_receiver_details(email_data.to),
                    "CC": self.get_receiver_details(email_data.cc),
                    "BCC": self.get_receiver_details(email_data.bcc),
                    "Subject": email_data.subject,
                    "TextPart": email_data.message,
                    "CustomID": "AppGettingStartedTest"
                }
            ]
        }

        return data

    def get_receiver_details(self, emails) -> list:
        receivers = []

        for receiver in emails:
            details = {
                "Email": receiver,
                "Name": "Receiver"
            }
            receivers.append(details)

        return receivers

    def send(self, formatted_data) -> None:
        result = self.mailjet.send.create(data=formatted_data)

        if result.status_code == 200:
            status = 'success'
        else:
            status = 'failed'

        return {
            'status': self.get_service_status(status),
            'result': result.json()
        }


class Infoblip(Service):
    BASE_URL = os.getenv("INFOBLIP__BASE_URL")
    API_KEY = os.getenv("INFOBLIP__API_KEY")

    def __init__(self, data) -> None:
        super().__init__(data)

        client_config = Configuration(
            host=self.BASE_URL,
            api_key={"APIKeyHeader": self.API_KEY},
            api_key_prefix={"APIKeyHeader": "App"},
        )

        api_client = ApiClient(client_config)
        self.api_instance = SendSmsApi(api_client)

    def format_data(self):
        msg_data = self.data

        sms_request = SmsAdvancedTextualRequest(
            messages=[
                SmsTextualMessage(
                    destinations=self.get_receiver_details(msg_data.to),
                    _from=msg_data.user.get_full_name(),
                    text=msg_data.message,
                )
            ])

        return sms_request

    def get_receiver_details(self, phone_numbers) -> list:
        receivers = []

        for receiver in phone_numbers:
            receivers.append(SmsDestination(
                to=receiver,
            ))

        return receivers

    def send(self, formatted_data) -> None:
        sms_request = formatted_data

        try:
            api_response: SmsResponse = self.api_instance.send_sms_message(
                sms_advanced_textual_request=sms_request)
        except ApiException as ex:
            print("Error occurred while trying to send SMS message.")
            print(ex)

        status = api_response['messages'][0].status.group_name
        return {
            'status': self.get_service_status(status),
            'result': api_response
        }
