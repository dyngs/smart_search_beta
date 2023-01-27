#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 24 21:29:23 2023

@author: dyngs
"""

import haystack
from sentence_transformers import SentenceTransformer, CrossEncoder
from resource_path import *
from torch.nn import Sigmoid

class Engine:
    
    def __init__(self):
        self.retriver = self.load_retriver()
        self.reader_on = False
        self.dev_on = False
        self.database = None
        
    
    def load_retriever(self):
        loaded_model = SentenceTransformer(
            resource_path('Models/4_eca_retriever_sr_disitlbert-dot-tas_b-b256-msmarco'))
        
        
        return loaded_model
    
    def reader_switch(self, on = True):
        self.reader_on = on
    
    def dev_mode_switch(self, on = True):
        self.dev_on = on
        
    def make_query(self):
        pass
    
    def load_databse(self):
        pass
    
    @staticmethod
    def load_paragraphs(self):
        pass
    
    def update(self):
        assert self.dev_on, "No access. You are not in developer mode"
            
        pass
    
    def test(self):
        assert self.dev_on, "No access. You are not in developer mode"
        
        pass
    
    
        
        
        
        
        
        
        
        
        
        