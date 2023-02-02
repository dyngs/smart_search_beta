import re
import os
import logging
from typing import List

from haystack.nodes.base import BaseComponent
from haystack import Document

class SrExtractor(BaseComponent):
    outgoing_edges = 1

    def document_preprocess_for_extraction(self, document: str) -> list:
        """Given text documents, this method splits them into lines and saves as a list.
        :param document: a single document saved str
        :return text_raw: list of separate lines from document
        """
        text_raw = []

        for line in document.splitlines():
            if not (line.strip() or line.strip('\n')):
                continue
            else:
                text_raw.append(line)

        return text_raw

    def extract_paragraphs(self, text_raw: list):
        """Given text documents, this method splits them into numbered paragraphs
        and saves the number of each paragraph.
        :param text_raw: a single document saved a list of separate lines
        :returns paragraph_numer_list, paragraph_list:
            list of paragraph numbers, list of paragraphs
        """
        i = 0

        paragraph_number_list = []
        paragraph_list = []
        while bool(re.match(r'This((\sSpecial\s)|\s)(R|r)eport\swas\sadopted\sby', text_raw[i])) == False:
            paragraph = ''
            # every paragraph must start with the number + '.' + tab sequence

            if bool(re.match(r'^(\d|\d\d|\d\d\d)\.\t', text_raw[i][0:10])):
                if bool(re.match(r'^\d\d\.', text_raw[i])):
                    paragraph_number_list.append(int(text_raw[i][0:2]))
                    paragraph += text_raw[i][4:].strip('\n').rstrip()
                    i += 1
                elif bool(re.match(r'^\d\d\d\.', text_raw[i])):
                    paragraph_number_list.append(int(text_raw[i][0:3]))
                    paragraph += text_raw[i][5:].strip('\n').rstrip()
                    i += 1
                else:
                    paragraph_number_list.append(int(text_raw[i][0]))
                    paragraph += text_raw[i][3:].strip('\n').rstrip()
                    i += 1

                # add to the current paragraph until a new one is detected or breaking condition met
                while (bool(re.match(r'^(\d|\d\d|\d\d\d)\.', text_raw[i+1][:5])) == False):

                    if bool(re.match(r'This((\sSpecial\s)|\s)(R|r)eport\swas\sadopted\sby', text_raw[i+1])):
                        break
                    paragraph += ' ' + text_raw[i].strip('\n').rstrip()
                    i += 1

                paragraph += ' ' + text_raw[i].strip('\n').rstrip()
                paragraph_list.append(paragraph)

            i += 1

        assert paragraph_number_list == range(1, paragraph_number_list[-1]) ,\
            "Some paragraphs are missing. Check manually."

        return paragraph_number_list, paragraph_list

    def extract_metadata(self, text_raw: list):
        """Given text documents, this method extracts documents metadata. Currently, it extracts only the title
        and report info.
        :param text_raw: a single document saved a list of separate lines
        :returns title, report_info: e.g., report_info="Special Report 34/2012, report_title="Auditing is fun"
        """
        i = 0
        if bool(re.match(r'\((p|P)ersuant\sto', text_raw[i].strip('\n'))):
            i += 1
        report_info = (text_raw[i].strip('\n').strip('\t'))
        i += 2

        title = ''
        while bool(re.match(r'(t|T)ogether\swith', text_raw[i])) == False:
            title += text_raw[i].strip('\n')
            i += 1
            if i > 10:
                break

        return title, report_info

    def run(self, documents: List):
        """To extract paragraphs, this function breaks down a document into lines, then searches for metadata
        in the first 10 lines of the document. After that, it finds the first numbered paragraph and splits
        the document. It converts paragraphs with metadata into a list of seperate Documents.
        :param documents: a single Document of a special report
        :return output: a dict with a list of paragraphs saved with key "documents" (as required by haystack.pipeline)
        """
        text_raw = self.document_preprocess_for_extraction(documents[0].content)
        title, report_info = self.extract_metadata(text_raw)
        paragraph_numbers, paragraphs = self.extract_paragraphs(text_raw)
        meta_data = [{"title" : title, "report_info" : report_info,
                 "paragraph_number" : paragraph_number} for paragraph_number in paragraph_numbers]
        documents_list = [{"content" : paragraph, "meta" : meta} for paragraph, meta in zip(paragraphs, meta_data)]
        documents_paragraphs = [Document.from_dict(document) for document in documents_list]

        output = {
            "documents": documents_paragraphs
        }

        return output, "output_1"

    def run_batch(self, txt: List[Document], pdf: List[Document], docx: List[Document]):
        """STILL NEEDS IMPLEMENTATION"""
        text_raw = self.document_preprocess_for_extraction(documents["documents"][0].content)
        title, report_info = self.extract_metadata(text_raw)
        paragraph_numbers, paragraphs = self.extract_paragraphs(text_raw)
        meta_data = [{"title" : title, "report_info" : report_info,
                 "paragraph_number" : paragraph_number} for paragraph_number in paragraph_numbers]
        documents_dict = [{"content" : paragraph, "meta" : meta} for paragraph, meta in zip(paragraphs, meta_data)]
        documents_paragraphs = [Document.from_dict(document) for document in documents_dict]

        return documents_paragraphs, "output_1"