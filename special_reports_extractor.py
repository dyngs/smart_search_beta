import re
import os
import logging
from haystack.nodes.base import BaseComponent

class SRExtractor(BaseComponent):
    outgoing_edges = 1

    def __init__(self):
        pass

    def document_preprocess_for_extraction(self, document: str) -> list:
        pass

    def extract_paragraphs(self, text_raw: list):
        """Given text documents, this method splits them into numbered paragraphs
        and saves the number of each paragraph.
        """
        pass

    def extract_metadata(self, text_raw: list):
        """Given text documents, this method extracts report_title. Currently, it extracts only the title
        and report info.
        """
        pass

        def run(self):
            pass

        def run_batch(self):
            pass