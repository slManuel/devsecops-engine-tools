from abc import ABCMeta, abstractmethod
from typing import Optional

class LicenseManagerGateway(metaclass=ABCMeta):
    @abstractmethod
    def upload_sbom(
        self, config, request
    ) -> "Optional[str]":
        "upload sbom to license analyzer"
