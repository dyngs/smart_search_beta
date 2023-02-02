import logging
import sys
# setting path
sys.path.append('../smart_search_beta')

from special_reports_extractor import SrExtractor

def test_extract():
    splitter = SrExtractor()
    file = open('test_data_extractor/test_file1.txt', 'r')
    test_report = file.read()
    test_report = splitter.document_preprocess_for_extraction(test_report)
    paragraph_numbers_list, paragraphs_list = splitter.extract_paragraphs(test_report)
    file.close()

    logging.info("Paragraphs extracted.")

    file = open('test_data_extractor/test_file1_par1.txt', 'r')
    test_paragraph_1 = file.read()
    # test_paragraph_1 = Database().document_preprocess_for_extraction(test_paragraph_1)
    assert paragraphs_list[0] == test_paragraph_1
    assert paragraph_numbers_list[0] == 1
    file.close()

    file = open('test_data_extractor/test_file1_par15.txt', 'r')
    test_paragraph_15  = file.read()
    # test_paragraph_15 = Database().document_preprocess_for_extraction(test_paragraph_15)
    assert paragraphs_list[14] == test_paragraph_15
    assert paragraph_numbers_list[14] == 15
    file.close()

    file = open('test_data_extractor/test_file1_par34.txt', 'r')
    test_paragraph_34 = file.read()
    # test_paragraph_34 = Database().document_preprocess_for_extraction(test_paragraph_34)
    assert paragraphs_list[33] == test_paragraph_34
    assert paragraph_numbers_list[33] == 34
    file.close()

    file = open('test_data_extractor/test_file1_par90.txt', 'r')
    test_paragraph_90 = file.read()
    # test_paragraph_90 = Database().document_preprocess_for_extraction(test_paragraph_90)
    assert paragraphs_list[89] == test_paragraph_90
    assert paragraph_numbers_list[89] == 90
    file.close()

    file = open('test_data_extractor/test_file1_par141.txt', 'r')
    test_paragraph_141 = file.read()
    # test_paragraph_141 = Database().document_preprocess_for_extraction(test_paragraph_141)
    assert paragraphs_list[-1] == test_paragraph_141
    assert paragraph_numbers_list[-1] == 141
    file.close()


def test_preprocessing():
    pass