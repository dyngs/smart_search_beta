from haystack.document_stores.faiss import FAISSDocumentStore
from haystack.nodes import PDFToTextConverter, PDFToTextOCRConverter, TextConverter, FileTypeClassifier
from haystack.nodes import PreProcessor, DocxToTextConverter
import logging
from haystack.pipelines import Pipeline
import os


class Database:

    def __init__(self):
        # will need change
        self.document_store = None
        self.file_classifier = None
        self.converter_pdf = None
        self.converter_docx = None
        self.converter_text = None
        self.pre_processor = None

    @staticmethod
    def load_database(faiss_index_path: str, faiss_config_path: str):
        database = Database()
        database.document_store = FAISSDocumentStore.load(index_path="", config_path="")
        return database

    def update_database(self, path_to_documents: str):
        assert self.document_store is not None, "No Database to update. " \
                                            "Please load a database or create a new one"
        self.file_classifier = FileTypeClassifier()
        self.converter_pdf = PDFToTextOCRConverter()
        self.converter_docx = DocxToTextConverter()
        self.converter_text = TextConverter()
        self.pre_processor = PreProcessor(clean_empty_lines=True,
                                          clean_whitespace=True,
                                          clean_header_footer=True,
                                          split_by="passage",
                                          split_respect_sentence_boundary=True,
                                          split_overlap=0)
        dir = os.listdir(path_to_documents)
        assert len(dir) > 0, f"{dir} is empty. Please provide a non-empty directory."
        self.load_documents(path_to_documents)

    def create_database(self):
        self.document_store = FAISSDocumentStore(faiss_index_factory_str="Flat",
                                                 sql_url="sqlite:///special_reports_faiss_store.db",
                                                 embedding_dim=764,
                                                 similarity="dot_product")

    def extract_paragraphs(self):
        """Given text documents, this method splits them into numbered paragraphs
        and saves the number of each paragraph.
        """
        pass

    def extract_metadata(self):
        """Given text documents, this method extracts report_guid, report_title
        """
        pass

    def load_documents(self, path_to_documents: str):
        """This method take a relative path to a folder with documents of different types.
        It converts them to text files and splits into paragraphs.
        It, then, saves all files into a new folder [name]_paragraphs.
        :param: path_to_documents: relative path to the folder with new documents (pdf,text, or docx)
        :return: haystack Documents"""

        documents_processed = None
        # 1.open path_to_documents and open one-by-one, classify the type, convert to text
        converted_documents = None

        # 2. Extract metadata for the whole document
        meta_data = self.extract_metadata()

        # 3. Split into paragraphs and save paragraph numbers

        # 4. Pre-process each paragraph, save as Documents, and metadata to each

        return documents_processed

