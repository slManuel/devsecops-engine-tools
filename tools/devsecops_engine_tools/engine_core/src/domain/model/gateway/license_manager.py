from abc import ABCMeta, abstractmethod

class LicenseManagerGateway(metaclass=ABCMeta):
    @abstractmethod
    def upload_sbom(
        self, config, request
    ) -> "str":
        "upload sbom to license analyzer"
