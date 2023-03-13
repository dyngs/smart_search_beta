import re
import logging
from typing import List
import datetime
from haystack.nodes.base import BaseComponent
from haystack import Document

logger = logging.getLogger(__name__)

class SrExtractor(BaseComponent):
    outgoing_edges = 1

    @staticmethod
    def document_preprocess_for_extraction(document: str) -> list:
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

    @staticmethod
    def extract_paragraphs(text_raw: list):
        """Given text documents, this method splits them into numbered paragraphs
        and saves the number of each paragraph. It detects paragraphs in two ways:
        -OPTION #1- Every paragraph starts with ^(\d|\d\d|\d\d\d)\.\t
                    aka it assumes there is a "." after the paragraph number (1/2/3 digits)
        -OPTION #2- Every paragraph starts with \d\d(\d)?(\s|\t) aka no "." after the paragraph number
                    aka there is no "." after the paragraph number (2/3 digits)
        :param text_raw: a single document saved a list of separate lines
        :returns paragraph_numer_list, paragraph_list:
            list of paragraph numbers, list of paragraphs
        """
        i = 0

        paragraph_number_list = []
        paragraph_list = []
        while bool(re.match(r'This((\sSpecial\s)|\s)([Rr])eport\swas\sadopted\sby', text_raw[i])) is False:
            paragraph = ''

            # OPTION 1: Every paragraph starts with ^(\d|\d\d|\d\d\d)\.\t
            # aka it assumes there is a "." after the paragraph number (1/2/3 digits)
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

                # Add to the current paragraph until a new one is detected or breaking condition met,
                # i.e. a new numbered paragraph detected or end of the main section met.
                while bool(re.match(r'^(\d|\d\d|\d\d\d)\.', text_raw[i+1][:5])) is False:

                    if bool(re.match(r'This((\sSpecial\s)|\s)([Rr])eport\swas\sadopted\sby', text_raw[i+1])):
                        break
                    paragraph += ' ' + text_raw[i].strip('\n').rstrip()
                    i += 1

                paragraph += ' ' + text_raw[i].strip('\n').rstrip()
                paragraph_list.append(paragraph)

            # OPTION 2: Every paragraph starts with \d\d(\d)?(\s|\t) aka no "." after the paragraph number
            # aka there is no "." after the paragraph number (2/3 digits)
            # print(text_raw[i][0:3])
            if bool(re.match(r'^\d\d(\d)?(\s|\t)', text_raw[i][0:5])):
                try:
                    number_before = paragraph_number_list[-1]
                except IndexError:
                    number_before = 0

                if bool(int(text_raw[i][0]) == 0):
                    current_number = int(text_raw[i][1])
                elif bool(re.match(r'\d', text_raw[i][2])):
                    current_number = int(text_raw[i][0:3])
                else:
                    current_number = int(text_raw[i][0:2])

                if bool(number_before == (current_number - 1)):
                    paragraph_number_list.append(current_number)
                    if current_number > 99:
                        paragraph += text_raw[i][4:].strip('\n').rstrip()
                    else:
                        paragraph += text_raw[i][3:].strip('\n').rstrip()

                    i += 1

                    # Check if the next line begins with a 2 or 3 digit sequence
                    try:
                        if bool(re.match(r'\d\d\d', text_raw[i+1][0:2])): # 3 digits
                            next_number = int(text_raw[i+1][0:3])
                        elif bool(re.match(r'\d\d', text_raw[i+1][0:1])): # 2 digits
                            next_number = int(text_raw[i+1][0:2])
                        else:                                             # no digits; will raise ValueError at casting
                            next_number = int(text_raw[i + 1][0:2])
                    except ValueError:
                        next_number = -1
                    except IndexError:
                        next_number = current_number + 1

                    # Add to the current paragraph until a new one is detected or breaking condition met
                    # Here the next paragraph must have a number that is 1 higher than the current one
                    while bool(re.match(r'^\d\d(\d)?(\s|\t)', text_raw[i + 1][:5]) and next_number == current_number + 1) is False:

                        if bool(re.match(r"This((\sSpecial\s)|\s)([Rr])eport\swas\sadopted\sby", text_raw[i + 1])) :
                            break
                        paragraph += ' ' + text_raw[i].strip('\n').rstrip()
                        i += 1

                        try:
                            if bool(re.match(r'\d', text_raw[i + 1][2])):
                                next_number = int(text_raw[i + 1][0:3])
                            elif bool(re.match(r'\d\d', text_raw[i + 1][0:1])):
                                next_number = int(text_raw[i + 1][0:2])
                            else:
                                next_number = int(text_raw[i + 1][0:2])
                        except ValueError:
                            next_number = -1
                        except IndexError:
                            next_number = current_number + 1

                    paragraph += ' ' + text_raw[i].strip('\n').rstrip()
                    paragraph_list.append(paragraph)
                    # print(paragraph)
            i += 1

        # paragraph_number_list == list(range(1, paragraph_number_list[-1]+1)),\
        #    f"Some paragraphs are missing. Check manually. Number of paragraphs missing" \
        #    f" {paragraph_number_list[-1] - len(paragraph_number_list)}. Paragraphs extracted:{paragraph_number_list}"

        return paragraph_number_list, paragraph_list

    @staticmethod
    def extract_metadata(text_raw: List):
        """Given text documents, this method extracts documents metadata. Currently, it extracts only the title
        and report info.
        :param text_raw: a single document saved a list of separate lines
        :returns title, report_info: e.g., report_info="Special Report 34/2012, report_title="Auditing is fun"
        """
        i = 0
        title = ""
        for j in range(0, 4):
            if bool(re.match(r'(\s*[Ss])pecial\s[Rr]eport\s[Nn][Oo]', text_raw[j].strip('\n'))):
                report_info = text_raw[j].strip('\n').strip('\t')
                i += 3
            elif bool(re.match(r'(\s*[Ss])pecial\s[Rr]eport', text_raw[j].strip('\n'))):
                report_info = "Special report "


        if bool(re.match(r'\([Pp]ersuant\sto', text_raw[i].strip('\n'))):
            i += 1


        while bool(re.match(r'([Tt])ogether\swith', text_raw[i]) or re.match(r'(CONTENTS)|(Contents)|(contents)', text_raw[i])) is False:
            title += text_raw[i].strip('\n') + ' '
            i += 1
            if i > 10:
                break

        if bool(re.match(r'(\s*[Ss])pecial\s[Rr]eport\s((?!N|no).)*$', text_raw[0].strip('\n'))):
            try:
                report_info += "No " + re.search(r'\d\d', title[-14:-1]).group() + "/" + re.search(r'2\d\d\d', title[-14:-1]).group()
            except AttributeError:
                report_info = "Special Report XX/20XX"
            title = title[15:-14]

        logger.info(f"{datetime.datetime}Metadata extracted.")

        return title, report_info

    @staticmethod
    def get_context(paragraphs_list: List[str]):
        """To extract context paragraphs, this function takes in a list of paragraphs ina document and shifts forwards
        and backwards to create to contexts lists. The beginning and end paragraphs store None values.
        :param paragraphs_list: a list of paragraphs stored as str
        :return paragraphs_previous: a list of paragraphs shifted back by 1; the first context paragraph is None
        :return paragraphs_next: a list of paragraphs shifted forward by 1; the last context paragraph is None
        """
        paragraphs_next = []
        for paragraph in paragraphs_list[1:]:
            paragraphs_next.append(paragraph)
        paragraphs_next.append(None)

        paragraphs_previous = [None]
        for paragraph in paragraphs_list[:-1]:
            paragraphs_previous.append(paragraph)

        return paragraphs_previous, paragraphs_next

    def run(self, documents: List):
        """To extract paragraphs, this function breaks down a document into lines, then searches for metadata
        in the first 10 lines of the document. After that, it finds the first numbered paragraph and splits
        the document. It converts paragraphs with metadata into a list of separate Documents.
        :param documents: a single Document of a special report
        :return output: a dict with a list of paragraphs saved with key "documents" (as required by haystack.pipeline)
        """

        text_raw = self.document_preprocess_for_extraction(documents[0].content)
        with open("new_format.txt", "w") as f:
            f.writelines(text_raw)
        title, report_info = self.extract_metadata(text_raw)
        paragraph_numbers, paragraphs = self.extract_paragraphs(text_raw)
        paragraphs_previous, paragraphs_next = self.get_context(paragraphs)
        meta_data = []
        for paragraph_number, previous, nextp in zip(paragraph_numbers, paragraphs_previous, paragraphs_next):
            meta_data.append({"title": title, "report_info": report_info, "paragraph_number": paragraph_number,
                              "context_previous": previous, "context_next": nextp})
        documents_list = [{"content": paragraph, "meta": meta} for paragraph, meta in zip(paragraphs, meta_data)]
        documents_paragraphs = [Document.from_dict(document) for document in documents_list]

        output = {
            "documents": documents_paragraphs
        }

        return output, "output_1"

    def run_batch(self, txt: List[Document], pdf: List[Document], docx: List[Document], **kwargs):
        pass
