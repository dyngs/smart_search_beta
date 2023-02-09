#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 21:29:23 2023

@author: dyngs
"""
import logging
from typing import List
import haystack
from haystack.nodes import EmbeddingRetriever, SentenceTransformersRanker, BM25Retriever
from database import Database

logger = logging.getLogger("engine")


class Engine:

    def __init__(self, index_path: str, index_config_path: str, retriever_path: str):
        self._load_database(index_path, index_config_path)
        self._load_sentence_retriever(retriever_path)
        self.word_retriever = None
        self.reader_on = False
        self.reader = None
        self.by_keyword = False
        self.dev_on = False

    def _load_sentence_retriever(self, retriever_path: str):
        self.sentence_retriever = EmbeddingRetriever(document_store=self.database.document_store,
                                                     embedding_model=retriever_path,
                                                     model_format="sentence_transformers")

    # def _load_word_retriever(self):
    #     return BM25Retriever(self.database.document_store)

    def reader_switch(self, on=True):
        self.reader_on = on

    def dev_mode_switch(self, on=True):
        self.dev_on = on

    def make_query_sentence(self, query: str, top_k: int):
        logger.info("Candidate paragraphs retrieved.")
        return self.sentence_retriever.retrieve(query=query, top_k=top_k)


    def make_query_word(self, query: str, top_k: int):
        logger.info("Candidate paragraphs retrieved.")
        return self.word_retriever.retrieve(query=query, top_k=top_k, all_terms_must_match=True)

    def load_reader(self, model_path_or_name: str):
        self.reader_switch(on=True)
        self.reader = SentenceTransformersRanker(model_path_or_name)

    def _load_database(self, index_path: str, index_config_path: str):
        self.database = Database()
        self.database.load_document_store(faiss_index_path=index_path, faiss_config_path=index_config_path)

    def update(self):
        assert self.dev_on, "No access. You are not in developer mode"

        pass

    def test(self):
        assert self.dev_on, "No access. You are not in developer mode"

        pass

    def cross_encode(self, query: str, top_k: int, min_similarity=0.0, documents: List[haystack.Document] = None):
        results_threshold = self.reader.predict(documents=documents, query=query, top_k=top_k)
        results = []
        for document in results_threshold:
            if document.score >= min_similarity:
                results.append(document)
            else:
                break
        logger.info("Paragraphs re-ranked.")
        return results

    def run(self, query: str, top_k: int, min_similarity=0.0):
        top_k = 2 * top_k if self.reader_on else top_k
        results = self.make_query_word(query, top_k) if self.by_keyword else self.make_query_sentence(query, top_k)

        if self.reader_on:
            top_k = int(top_k / 2)
            results = self.cross_encode(query=query, top_k=top_k, min_similarity=min_similarity, documents=results)

        return results
