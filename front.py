#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 12:29:58 2023

@author: dyngs
"""
import streamlit as st
from PIL import Image
from engine import Engine
from streamlit_tags import st_tags_sidebar
from streamlit_lottie import st_lottie
from streamlit_extras.add_vertical_space import add_vertical_space
import time
import json

# image imports
path = "images/67532-artificial-intelligence-robot.json"
with open(path,"r") as file:
    robot = json.load(file)
path = "images/90753-not-found-loading.json"
with open(path,"r") as file:
    not_found_img = json.load(file)
icon = Image.open('images/ECA-logo.svg.png')
# page configurations
st.set_page_config(initial_sidebar_state="collapsed", page_icon=icon)


if 'query' not in st.session_state:
    st.session_state.query = ""
if 'engine' not in st.session_state:
    _left, mid, _right = st.columns([6, 30, 6])

    with mid:
        placeholder = st.container()
        with placeholder:
            st_lottie(robot,
                      reverse=True,
                      speed=1.5,
                      height=400,
                      width=500,
                      loop=True,
                      quality='high',
                      key='Robot')
            st.markdown("### &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;"
                        "&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;Loading the engine...",
                        unsafe_allow_html=True)

    st.session_state.engine = Engine(index_path="test_context_database.faiss",
                                     index_config_path="test_context_database.json",
                                     retriever_path="models/4_eca_retriever_sr_distilbert-dot-tas_b-b256-msmarco")
    st.session_state.engine.load_reader(model_path_or_name="cross-encoder/ms-marco-TinyBERT-L-2-v2")
    add_vertical_space(30)


with st.sidebar:
    col_side_1, col_side_2 = st.columns([1, 2])
    with col_side_1:
        img_logo_top = Image.open("images/ECA-logo.svg.png").resize((90, 87))
        st.image(img_logo_top, use_column_width="auto")
    with col_side_2:
        st.title("ECA Smart Search\n _Special_ _Reports_ _Index_")

    st.session_state.filters = st_tags_sidebar(label="## Add keywords", text=f"You can enter up to 10 keywords",
                                               maxtags=10, key='1')
    st.header("Advanced Search Parameters")
    with st.form(key="parameters"):
        st.session_state.numb_paragraphs = st.slider('Show top N paragraphs:', 1, 100, 20,
                                                     help='Selecting a large number of paragraphs will increase recall but decrease the speed of your search.')
        st.session_state.use_reranker = st.checkbox("Re-rank initial results    ", value=True,
                                                    help="Re-ranking results increases the accuracy of your search, but it needs extra time.")
        st.session_state.min_similarity = st.slider('Minimum similarity score (in %):', 0.0, 100.0, 1.0, step=0.1,
                                                    help='You can define a similarity score cut-off if you use the ranker. Otherwise, this feature will be disabled.') / 100
        st.session_state.engine.reader_switch(on=st.session_state.use_reranker)
        st.form_submit_button("Submit")


col1, col2 = st.columns([1, 5])

with col1:
    add_vertical_space(2)
    img_logo_top = Image.open("images/logo_special_reports.png").resize((90, 87))
    st.image(img_logo_top, use_column_width="auto")

with col2:
    st.title("ECA Smart Search *beta*\n _Special_ _Reports_ _Index_")

col3, col4, col5 = st.columns([640, 1, 96])

with col3:
    st.session_state.query = st.text_input("Search Query", placeholder="Ask me a question or simply type a phrase...", label_visibility="collapsed", max_chars=500)

with col5:
    with st.container():
        st.session_state.search_clicked = st.button("Search")
    
if st.session_state.query != "" or st.session_state.search_clicked:
    with st.spinner('Searching...'):
        t0 = time.time()
        results = st.session_state.engine.run(st.session_state.query, st.session_state.numb_paragraphs,
                                              st.session_state.min_similarity)
        t1 = time.time()
        search_time = t1 - t0
        if len(results) > 0:
            st.success(f'Searched {st.session_state.engine.database.document_store.get_embedding_count()} '
                       f'records in {round(search_time,2) } seconds \n')
            # print results
            for i in range(len(results)):
                text_meta = str(str(i + 1) + '.' + ' Paragraph ' + str(results[i].meta["paragraph_number"]))
                text_meta += str(' in ' + results[i].meta["report_info"] + '\n')
                text = str("\n" + results[i].content)
                if st.session_state.use_reranker:
                    text_score = str(
                        'Similarity Score: ' + str("{:.1f}".format(results[i].score * 100)) + '%' + '\n\n\n')
                with st.container():
                    st.subheader(text_meta)
                    st.write(text)
                    st.write("\n\n")
                    if st.session_state.use_reranker:
                        st.write(text_score, unsafe_allow_html=True)
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
            add_vertical_space(5)
            st.download_button(label="Download these results",
                               data=text,
                               file_name=f'{st.session_state.query}_results.txt',
                               mime='text'
                               )
        else:
            st.error("Sorry! None of the paragraphs meet your search criteria. You can adjust them in the sidebar.")
            _left, mid, _right = st.columns([7, 20, 7])
            with mid:
                st_lottie(not_found_img,
                          reverse=True,
                          speed=1,
                          height=300,
                          width=400,
                          loop=True,
                          quality='high',
                          key='NotFound')

#disable search
st.session_state.search_clicked = False


