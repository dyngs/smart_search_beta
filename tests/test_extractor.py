import logging
import sys
# setting path
sys.path.append('../smart_search_beta')

from special_reports_extractor import SrExtractor

def test_extract():

    splitter = SrExtractor()
    file_test = [1, 2]
    file_pars = [[1, 15, 34, 90, 141], [7, 28, 65, 72]]

    logging.info("Paragraphs extracted.")
    for file_number in file_test:
        file = open('test_data_extractor/test_file' +f'{file_number}.txt', 'r')
        test_report = file.read()
        test_report = splitter.document_preprocess_for_extraction(test_report)
        paragraph_numbers_list, paragraphs_list = splitter.extract_paragraphs(test_report)
        file.close()
        for paragraph_test in file_pars[file_number-1]:
            i = paragraph_test-1
            file = open('test_data_extractor/test_file' + f'{file_number}_par' + f'{paragraph_test}.txt', 'r')
            test_paragraph = file.read()
            # test_paragraph_1 = Database().document_preprocess_for_extraction(test_paragraph_1)
            assert paragraphs_list[i] == test_paragraph
            assert paragraph_numbers_list[i] == paragraph_test
            file.close()

def test_preprocessing():
    pass