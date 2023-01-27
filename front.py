#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 12:29:58 2023

@author: dyngs
"""
import streamlit as st
from PIL import Image
from resource_path import resource_path
from time import time
from engine import Engine



if 'query' not in st.session_state:
    st.session_state.query = ""
if 'engine' not in st.session_state:
    st.session_state.engine = Engine('bert')

text_show = st.session_state.engine.load_paragraphs('Data/EREP_reports_after2010.xlsx')

with st.sidebar:
    st.header("Advanced Settings")
    with st.form(key="parameters"):
        st.session_state.numb_paragraphs = st.slider('Show top N paragraphs:', 1, 100, 20, help='Selecting a large number of paragraphs will increase recall but decrease the speed of your search.')
        st.session_state.use_reranker = st.checkbox("Re-rank initial results", value=True, help="Re-ranking results increases the accuracy of your search, but it needs extra time.")
        st.form_submit_button("Submit")
    
col1, col2 = st.columns([1,5])

with col1:
    img_logo_top = Image.open(resource_path("images/logo_special_reports.png")).resize((90,87))
    st.write(" ")
    st.write(" ")
    st.image(img_logo_top, use_column_width="auto")

with col2:
    st.title("ECA Smart Search *beta*\n _Special_ _Reports_ _Index_")

col3, col4 = st.columns([5,1])

with col3:
    st.session_state.query = st.text_input("Search Query", placeholder="Ask me a question or simply type a phrase...", label_visibility="collapsed", max_chars=500)

with col4:  
    st.session_state.search_clicked = st.button("Search")
    
if st.session_state.query != "" or st.session_state.search_clicked:
    with st.spinner('Searching...'):
        t0 = time() 
        results = st.session_state.engine.make_query(st.session_state.query, st.session_state.use_reranker, st.session_state.numb_paragraphs)
        t1 = time()
        search_time = t1 - t0
        st.success(f'Searched {text_show.shape[0]} records in {round(search_time,2) } seconds \n')
        k = 1
        for i,j in results:
            text_meta = str(str(k) + '.' + ' Paragraph ' + str(text_show['ParagraphNumber'].values[i]))
            text_meta += str(' in ' + text_show['ParagraphInfo'].values[i] + '\n')
            text = str("\n" + text_show['ParagraphText'].values[i])
            if st.session_state.engine.model_type == 'bert' and st.session_state.use_reranker:
                text_score = str('Similarity Score: ' + str(j) + '%' + '\n\n\n')
            with st.container():
                st.subheader(text_meta)
                st.write(text)
                st.write("\n\n")
                if st.session_state.engine.model_type == 'bert' and st.session_state.use_reranker:
                    st.write(text_score)
                with st.expander("See context"):
                    text_long =  str("\n" + text_show['ParagraphText'].values[i-1] + "\n")
                    text_long_2 = str("\n" + text_show['ParagraphText'].values[i+1] + "\n")
                    st.write(text_long)
                    st.write(text)
                    st.write(text_long_2)
            k += 1
        
#disable search
st.session_state.search_clicked = False