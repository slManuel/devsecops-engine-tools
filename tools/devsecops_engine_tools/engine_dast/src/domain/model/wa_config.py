class WaConfig:
    def __init__(self, data: dict, authentication_gateway):
        self.target_type: str = "WA"
        self.url: str = data["endpoint"]
        self.data: dict = data.wa_data
        self.concurrency: int = None
        self.rate_limit: int = None
        self.response_size: int = None
        self.bulk_size: int = None
        self.timeout: int = None

    def authenticate(self):
        self.credentials = self.authentication_gateway.get_credentials()
        if self.credentials is not None:
            self.data["headers"][self.credentials[0]] = self.credentials[1]