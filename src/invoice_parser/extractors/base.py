from abc import ABC, abstractmethod

from PIL import Image

from invoice_parser.schema.models import GSTInvoice


class Extractor(ABC):
    @abstractmethod
    def analyze(self, image: Image.Image) -> GSTInvoice:
        raise NotImplementedError

    @abstractmethod
    async def analyze_async(self, image: Image.Image) -> GSTInvoice:
        raise NotImplementedError
