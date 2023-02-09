import os
import sys
from haystack.nodes import EmbeddingRetriever
from database import Database

def test_create():
    test_database = Database()
    test_database.launch_new_document_store(set_file_name="test1")
    assert test_database.document_store is not None
    os.remove("test1.db")


def test_launch_and_update():
    test_database = Database()
    test_database.launch_new_document_store(set_file_name="test2")
    retriever_test = EmbeddingRetriever(document_store=test_database.document_store,
                                        embedding_model="models/4_eca_retriever_sr_distilbert-dot-tas_b-b256-msmarco",
                                        model_format="sentence_transformers")
    test_database.update_document_store('tests/data_test_database', retriever_test)
    assert test_database.document_store.get_embedding_count() == (72+141+86)
    os.remove("test2.db")


def test_save_and_load():
    test_database = Database()
    test_database.launch_new_document_store(set_file_name="test3")
    test_database.save_database()
    test_database_2 = Database()
    test_database_2.load_document_store(faiss_index_path=os.path.join(os.getcwd(), test_database.name + ".faiss"),
                                        faiss_config_path=os.path.join(os.getcwd(), test_database.name + ".json"))
    assert test_database_2.document_store is not None
    os.remove("test3.db")
    os.remove("test3.faiss")
    os.remove("test3.json")
