import logging
import sys
# setting path
sys.path.append('../smart_search_beta')
from haystack.nodes import EmbeddingRetriever
from database import Database
import haystack.telemetry as telemetry


def test_create():
    test_database = Database()
    test_database.launch_new_document_store()
    assert test_database.document_store is not None

def test_load_and_update():
    telemetry.disable_telemetry()
    test_database = Database()
    test_database.launch_new_document_store()
    retriever_test = EmbeddingRetriever(document_store=test_database.document_store,
                                                  embedding_model="/Users/dyngs/Desktop/IntelligentSearch/smartsearchv0.4/Models/4_eca_retriever_sr_disitlbert-dot-tas_b-b256-msmarco",
                                                  model_format="sentence_transformers")
    test_database.update_document_store('tests/', retriever_test)
