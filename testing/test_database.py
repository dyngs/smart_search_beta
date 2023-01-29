from database import Database


def test_create():
    test_database = Database()
    test_database.launch_new_document_store()
    assert test_database.document_store is not None


def test_extract():
    test_database = Database()
    test_database.launch_new_document_store()
    test_report = open('test_data/test_file1.txt', 'r')
    paragraph_numbers_list, paragraphs_list = test_database.extract_paragraphs(test_report)

    test_paragraph_1 = open('test_data/test_file1_par1.txt.txt', 'r')
    assert paragraphs_list[0] == test_paragraph_1
    assert paragraph_numbers_list[0] == 1

    test_paragraph_15 = open('test_data/test_file1_par15.txt.txt', 'r')
    assert paragraphs_list[14] == test_paragraph_15
    assert paragraph_numbers_list[14] == 15

    test_paragraph_34 = open('test_data/test_file1_par34.txt.txt', 'r')
    assert paragraphs_list[33] == test_paragraph_34
    assert paragraph_numbers_list[33] == 34

    test_paragraph_90 = open('test_data/test_file1_par90.txt.txt', 'r')
    assert paragraphs_list[89] == test_paragraph_90
    assert paragraph_numbers_list[89] == 90

    test_paragraph_141 = open('test_data/test_file1_par141.txt.txt', 'r')
    assert paragraphs_list[-1] == test_paragraph_141
    assert paragraph_numbers_list[-1] == 141


def test_preprocessing():
    pass


def test_load_and_update():
    pass
