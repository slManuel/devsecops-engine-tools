
from devsecops_engine_tools.engine_utilities.dependency_track.infrastructure.driver_adapters.sbom import SbomRestConsumer

class SbomUserCase:
    def __init__(self, rest_component: SbomRestConsumer):
        self.__rest_component = rest_component

    def upload(self, request):
        return self.__rest_component.upload_sbom(request)