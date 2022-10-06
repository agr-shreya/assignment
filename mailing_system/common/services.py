from service._helpers.constants import ServiceStatus


class Service:
    def __init__(self, data) -> None:
        self.data = data

    @ classmethod
    def get_service_status(cls, status: str) -> ServiceStatus:
        if status.lower() == 'success':
            return ServiceStatus.DELIVERED
        elif status.lower() == 'pending':
            return ServiceStatus.PENDING

        return ServiceStatus.FAILED

    def send_message(self):
        formatted_data = self.format_data()
        return self.send(formatted_data)

    def format_data(self):
        '''
            formatting the data according to the 
            api requirements (args)
        '''
        pass

    def send(self, formatted_data):
        '''
            return {
                status: 'Delivered/Pending/Failed',
                result: JSON of api result
            }
        '''
        pass
