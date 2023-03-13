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
        self.ranker_on = False
        self.ranker = None
        self.by_keyword = False
        self.dev_on = False

    def _load_sentence_retriever(self, retriever_path: str):
        self.sentence_retriever = EmbeddingRetriever(document_store=self.database.document_store,
                                                     embedding_model=retriever_path,
                                                     model_format="sentence_transformers")

    # def _load_word_retriever(self):
    #     return BM25Retriever(self.database.document_store)

    def load_ranker(self, model_path_or_name: str):
        """This function lets the user load a cross-encoding SentenceTransformer either from the disk
        or from Huggingface.

        :param model_path_or_name: path to a cross-encoder, alternatively it searches for one on huggingface
        """
        self.ranker = SentenceTransformersRanker(model_path_or_name)
        self._ranker_switch(on=True)

    def _ranker_switch(self, on=True):
        """Turning on the ranker manually. It is safer to load a cross-encoder.

        :param on: optional
        """
        assert self.ranker is not None, "Could not find a SentenceTranformerRanker. " \
                                        "Please use load_cross_encoder() to initialize it first."
        self.ranker_on = on

    def _load_database(self, index_path: str, index_config_path: str):
        """This will load a Database object storing documents given the index path and a JSON config path.
        You need to make sure that the config file points to the correct SQL db file.
        The Engine object will store the link.

        :param index_path: path to the (FAISS, for semantic search) index
        :param index_config_path: path to the (JSON, for semantic search) index
        """
        self.database = Database()
        self.database.load_document_store(faiss_index_path=index_path, faiss_config_path=index_config_path)


    def dev_mode_switch(self, on=True):
        self.dev_on = on

    def test(self):
        assert self.dev_on, "No access. You are not in developer mode"

        pass

    def make_query_sentence(self, query: str, top_k: int):
        """It retrieves top_k paragraphs using an Embedding retriever stored in the Engine object.

        :param query: string with the query phrase/question that will be matched against every paragraph
        :param top_k: integer indicating number of paragraphs to be retrieved
        :return: a list of haystack.Document objects storing paragraphs
        """
        logger.info("Paragraphs retrieved.")
        return self.sentence_retriever.retrieve(query=query, top_k=top_k)


    def make_query_word(self, query: str, top_k: int):
        """NOT IMPLEMENTED This function uses the BM25 retriever to query top_k most similar paragraphs in the index.


        :param query: string with the query phrase/question that will be matched against every paragraph
        :param top_k: integer indicating number of paragraphs to be retrieved
        :return: a list of haystack.Document objects storing paragraphs
        """
        logger.info("Candidate paragraphs retrieved.")
        return self.word_retriever.retrieve(query=query, top_k=top_k, all_terms_must_match=True)


    def cross_encode(self, query: str, top_k: int, min_similarity=0.0, documents: List[haystack.Document] = None):
        """This function compares the query against each of the documents to achieve a similarity score
        on a scale from 0.0 to 100.0. It returns a list of haystack.Document object with top_k sim. scores that meet
        the minimum threshold.
        :param query: string with the query phrase/question that will be matched against every paragraph
        :param top_k: integer indicating number of paragraphs to be retrieved
        :param min_similarity: float (0.0 to 100.0) indicating similarity cut-off for the cross-encoder
        :param documents: a list of haystack.Document objects storing paragraphs for the query to be compared against
        :return results: a list of haystack.Document objects storing paragraphs that meet above criteria
        """
        results_threshold = self.ranker.predict(documents=documents, query=query, top_k=top_k)
        results = []
        for document in results_threshold:
            if document.score >= min_similarity:
                results.append(document)
            else:
                break
        logger.info("Paragraphs re-ranked.")
        return results

    def run(self, query: str, top_k: int, min_similarity=0.0):
        """This function retrieves top-k most similar paragraphs based on lexical (self.by_keyword) or semantic search.
        It is the single start point for every query. If self.ranker_on == True, the engine will run the cross-encoder
        on 2*top_k candidates retrieved by make_query__().
        :param query: string with the query phrase/question
        :param top_k: integer indicating number of paragraphs to be retrieved
        :param min_similarity: float (0.0 to 100.0) indicating similarity cut-off for the cross-encoder
        :return results: a list of haystack.Document objects storing paragraphs
        """
        top_k = 2 * top_k if self.ranker_on else top_k
        results = self.make_query_word(query, top_k) if self.by_keyword else self.make_query_sentence(query, top_k)

        if self.ranker_on:
            top_k = int(top_k / 2)
            results = self.cross_encode(query=query, top_k=top_k, min_similarity=min_similarity, documents=results)

        return results
