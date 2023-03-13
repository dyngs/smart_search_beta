import pandas as pd
import numpy as np
from engine import Engine


def test_ranker():
    engine = Engine(index_path="tests/data_test_engine/test_engine_database.faiss",
                    index_config_path="tests/data_test_engine/test_engine_database.json",
                    retriever_path="models/4_eca_retriever_sr_distilbert-dot-tas_b-b256-msmarco")
    engine.load_ranker(model_path_or_name="cross-encoder/ms-marco-MiniLM-L-12-v2")
    results = engine.run("European Union has introduced good policies.", top_k=5, min_similarity=0.4)
    assert results[-1].score >= 0.
    engine._ranker_switch(False)
    results = engine.run("European Union has introduced good policies.", top_k=5, min_similarity=0.4)
    assert len(results) == 5
    engine._ranker_switch(True)
    results = engine.run("European Union has introduced good policies.", top_k=5, min_similarity=0.900)
    assert results[-1].score >= 0.900


def test_query_sentence():
    test_set = pd.read_csv("tests/data_test_engine/test_paragraph.tsv", delimiter="\t")
    engine = Engine(index_path="tests/data_test_engine/test_engine_database.faiss",
                    index_config_path="tests/data_test_engine/test_engine_database.json",
                    retriever_path="models/4_eca_retriever_sr_distilbert-dot-tas_b-b256-msmarco")
    engine.load_ranker(model_path_or_name="cross-encoder/ms-marco-MiniLM-L-12-v2")
    mrr = []
    for query, pararaph in zip(test_set["question"].values, test_set["correct_paragraph"].values):
        results = engine.run(query=query, top_k=10)
        i = 1
        for document in results:
            if document.content == pararaph:
                mrr.append(i/10)
                i += 1
                break
            i += 1
    print(np.mean(mrr))


def test_query_word():
    pass
