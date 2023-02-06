#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 21:29:23 2023

@author: dyngs
"""
import logging
from haystack.nodes import EmbeddingRetriever, SentenceTransformersRanker, BM25Retriever
from database import Database

logging.getLogger("engine")

class Engine:

    def __init__(self, index_path: str, index_config_path: str, retriever_path: str):
        self._load_database(index_path, index_config_path)
        self.sentence_retriever = self._load_sentence_retriever(retriever_path)
        # self.word_retriever = self._load_word_retriever()
        self.reader_on = False
        self.reader = None
        self.by_keyword = False
        self.dev_on = False

    def _load_sentence_retriever(self, retriever_path: str):
        return EmbeddingRetriever(document_store=self.database.document_store,
                                  embedding_model=retriever_path,
                                  model_format="sentence_transformers")

    # def _load_word_retriever(self):
    #     return BM25Retriever(self.database.document_store)

    def reader_switch(self, on=True):
        self.reader_on = on

    def dev_mode_switch(self, on=True):
        self.dev_on = on

    def make_query_sentence(self, query: str, top_k: int):
        return self.sentence_retriever.retrieve(query=query, top_k=top_k)
    #
    # def make_query_word(self, query: str, top_k: int):
    #     return self.word_retriever.retrieve(query=query, top_k=top_k, all_terms_must_match=True)

    def load_reader(self, model_path_or_name: str):
        self.reader_switch(on=True)
        return SentenceTransformersRanker(model_path_or_name)

    def _load_database(self, index_path: str, index_config_path: str):
        self.database = Database()
        self.database.load_document_store(faiss_index_path=index_path, faiss_config_path=index_config_path)


    def update(self):
        assert self.dev_on, "No access. You are not in developer mode"

        pass

    def test(self):
        assert self.dev_on, "No access. You are not in developer mode"

        pass

    def run(self, query: str, top_k: int, min_similarity=0.0):
        top_k = 2 * top_k if self.reader_on else top_k

        if self.by_keyword:
            results = self.make_query_word(query, top_k)
        else:
            results = self.make_query_sentence(query, top_k)

        if self.reader_on:
            results = self.reader.predict(results)
            top_k = top_k / 2

        return results[0:(top_k- 1)]
