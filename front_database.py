import os
from haystack.nodes import EmbeddingRetriever
import streamlit as st
from numpy.random import randint

from database import Database
from engine import Engine
from database.database import Database

def handle_uploaded_files(uploaded_files):
    for file in uploaded_files:
        with open(f'data/tray/{file.name}', 'wb+') as destination:
            destination.write(file.read())



st.session_state.all_docs_approved = False
st.title("Database Config")
# 2. horizontal menu
with st.container():
    st.session_state.uploaded_files = st.file_uploader("Upload one or more special reports ", accept_multiple_files=True,
                                      type=[".txt", ".pdf", ".docx"], key="uploader")
handle_uploaded_files(st.session_state.uploaded_files)

st.session_state.conversion_start = st.button("Convert", help="Clicking on this button will also restart the whole process.")

@st.cache_resource
def call_database():
    st.session_state.disable_meta = True # need this only once on initialization
    database_eca = Database()
    database_eca.load_document_store(faiss_index_path="test_dev_db.faiss", faiss_config_path="test_dev_db.json")
    return database_eca

database_eca = call_database()


if st.session_state.conversion_start:
    if len(os.listdir("data/tray")) < 1:
        st.error("At least 1 documents is required.")
    st.session_state.documents = [database_eca.load_documents(os.path.join("data/tray", document)) for document in os.listdir("data/tray")]
    st.session_state.disable_meta = False
    # duplicate the last report for correct functionality
    st.session_state.documents.append(st.session_state.documents[-1])
    st.session_state.document_number = 0
    st.session_state.conversion_start = False
    st.session_state.conversion_button_disabled = True
    st.session_state.percent_completed = 0
    st.session_state.percent_completed_embed = 0
    st.session_state.documents_approved = []
    st.session_state.button_delete = False


if not st.session_state.disable_meta:
    st.session_state.bar = st.progress(st.session_state.percent_completed)

    if st.session_state.button_delete:
        st.session_state.documents_approved.pop(-2)

    try:
        document = st.session_state.documents[st.session_state.document_number]
        st.subheader(document[0].meta["report_info"])
        st.write(document[0].meta["title"])

        st.session_state.percent_completed += 1 / len(st.session_state.documents)

        validation_paragraphs = randint(0, len(document), 15)

        with st.form(document[0].meta["report_info"]):
            for paragraph_num in validation_paragraphs:
                document[paragraph_num].meta["report_info"] = document[0].meta[
                    "report_info"]
                document[paragraph_num].meta["title"] = document[0].meta["title"]
                st.write(f"**Paragraph {paragraph_num + 1}**")
                st.write(document[paragraph_num].content)
            st.session_state.approved_true = st.form_submit_button("Approve Document", type="primary")
            st.session_state.documents_approved.append(document)

        st.session_state.document_number += 1

        st.session_state.button_delete = st.button(label="Delete")

        st.session_state.bar.progress(st.session_state.percent_completed)


    except IndexError:
        # set this condition for when the last document approved -> deletes the duplicate
        try:
            condition = st.session_state.documents_approved[-1][0].id == st.session_state.documents_approved[-2][0].id
        except IndexError:
            condition = False

        if st.session_state.button_delete or condition:
            st.session_state.documents_approved.pop(-1)
            st.session_state.button_delete = False

        retriever_test = EmbeddingRetriever(document_store=database_eca.document_store,
                                            embedding_model="models/4_eca_retriever_sr_distilbert-dot-tas_b-b256-msmarco",
                                            model_format="sentence_transformers")
        st.success(f"Successfully pre-processed {len(st.session_state.documents_approved)} documents:")
        for approved_document in st.session_state.documents_approved:
            approved_document[0].meta["report_info"]

        st.session_state.percent_completed_embed = database_eca.document_store.get_embedding_count() / len(
            os.listdir("data/tray"))
        col_1, col_2, col_3, col_4 = st.columns(4)

        with col_1:
            st.session_state.start_embed = st.button(f"Embed documents",
                                                     help="Warning! This will delete your documents.")
        if st.session_state.start_embed:

            for document in st.session_state.documents_approved:
                database_eca.document_store.write_documents(document)
                database_eca.document_store.update_embeddings(retriever=retriever_test,
                                                              update_existing_embeddings=True)
                st.info(f"{document[0].meta['report_info']} embedded")

            database_eca.save_database()
            for file in st.session_state.uploaded_files:
                os.remove(f'data/tray/{file.name}')

            st.session_state.documents_approved.clear()
            st.session_state.disable_meta = True
            st.success("✅ All reports embedded. Document tray cleaned")



