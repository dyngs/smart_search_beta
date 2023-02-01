import logging
import sys
# setting path
sys.path.append('../smart_search_beta')

from database import Database


def test_create():
    test_database = Database()
    test_database.launch_new_document_store()
    assert test_database.document_store is not None


def test_load_and_update():
    pass
