import re
import os
import logging
from haystack.nodes.base import BaseComponent

class SRExtractor(BaseComponent):
    outgoing_edges = 1

    def __init__(self):
        pass

    def document_preprocess_for_extraction(self, document: str) -> list:
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

                # search for a full stop at the end of the line (most bullet points do not end with full stops) (bool(re.search(r'\.($|\s+$|\n)', text_raw[i][len(text_raw[i])-10:])) == False) and

                while (bool(re.match(r'^(\d|\d\d|\d\d\d)\.', text_raw[i+1][:5])) == False):

                    if bool(re.match(r'This((\sSpecial\s)|\s)(R|r)eport\swas\sadopted\sby', text_raw[i+1])):
                        break
                    paragraph += ' ' + text_raw[i].strip('\n').rstrip()
                    i += 1

                paragraph += ' ' + text_raw[i].strip('\n').rstrip()
                paragraph_list.append(paragraph)

            i += 1

        return paragraph_number_list, paragraph_list

    def extract_metadata(self, text_raw: list):
        """Given text documents, this method extracts report_title. Currently, it extracts only the title
        and report info.
        """
        i = 0
        if bool(re.match(r'\((p|P)ersuant\sto', text_raw[i].strip('\n'))):
            i += 1
        title = (text_raw[i].strip('\n').strip('\t') + ': ' + text_raw[i + 2].strip('\n'))
        i += 3

        report_info = ''
        while bool(re.match(r'(t|T)ogether\swith', text_raw[i])) == False:
            report_info += ' ' + text_raw[i].strip('\n')
            i += 1
            if i > 10:
                break

        return title, report_info

        def run(self, text, pdf, docx):

            pass

        def run_batch(self):
            pass