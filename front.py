#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 12:29:58 2023

@author: dyngs
"""
import streamlit as st
from PIL import Image
from time import time
from engine import Engine



if 'query' not in st.session_state:
    st.session_state.query = ""
if 'engine' not in st.session_state:
    st.session_state.engine = Engine(index_path="test_context_database.faiss",
                                     index_config_path="test_context_database.json",
                                     retriever_path="/Users/dyngs/Desktop/IntelligentSearch/smartsearchv0.4/Models/4_eca_retriever_sr_disitlbert-dot-tas_b-b256-msmarco")
    st.session_state.engine.load_reader(model_path_or_name="cross-encoder/ms-marco-TinyBERT-L-2-v2")


with st.sidebar:
    st.header("Advanced Settings")
    with st.form(key="parameters"):
        st.session_state.numb_paragraphs = st.slider('Show top N paragraphs:', 1, 100, 20, help='Selecting a large number of paragraphs will increase recall but decrease the speed of your search.')
        st.session_state.use_reranker = st.checkbox("Re-rank initial results", value=True, help="Re-ranking results increases the accuracy of your search, but it needs extra time.")
        st.session_state.engine.reader_switch(on=st.session_state.use_reranker)
        st.form_submit_button("Submit")
    
col1, col2 = st.columns([1, 5])

with col1:
    img_logo_top = Image.open("images/logo_special_reports.png").resize((90, 87))
    st.write(" ")
    st.write(" ")
    st.image(img_logo_top, use_column_width="auto")

with col2:
    st.title("ECA Smart Search *beta*\n _Special_ _Reports_ _Index_")

col3, col4 = st.columns([5, 1])

with col3:
    st.session_state.query = st.text_input("Search Query", placeholder="Ask me a question or simply type a phrase...", label_visibility="collapsed", max_chars=500)

with col4:  
    st.session_state.search_clicked = st.button("Search")
    
if st.session_state.query != "" or st.session_state.search_clicked:
    with st.spinner('Searching...'):
        t0 = time() 
        results = st.session_state.engine.run(st.session_state.query, st.session_state.numb_paragraphs)
        t1 = time()
        search_time = t1 - t0
        st.success(f'Searched {st.session_state.engine.database.document_store.get_embedding_count()} '
                   f'records in {round(search_time,2) } seconds \n')

        for i in range(len(results)):
            text_meta = str(str(i+1) + '.' + ' Paragraph ' + str(results[i].meta["paragraph_number"]))
            text_meta += str(' in ' + results[i].meta["report_info"] + '\n')
            text = str("\n" + results[i].content)
            if st.session_state.use_reranker:
                text_score = str('Similarity Score: ' + str(round(results[i].score, 3) * 100.0) + '%' + '\n\n\n')
            with st.container():
                st.subheader(text_meta)
                st.write(text)
                st.write("\n\n")
                if st.session_state.use_reranker:
                    st.write(text_score)
                with st.expander("See context"):
                    if results[i].meta["context_previous"] is not None:
                        text_long = str("\n" + results[i].meta["context_previous"] + "\n")
                    else:
                        text_long = "<_document_ _begins_ _here_>"

                    if results[i].meta["context_next"] is not None:
                        text_long_2 = str("\n" + results[i].meta["context_next"] + "\n")

                    else:
                        text_long_2 = "<_document_ _ends_ _here_>"

                    st.write(text_long)
                    st.write(text)
                    st.write(text_long_2)
        
#disable search
st.session_state.search_clicked = False