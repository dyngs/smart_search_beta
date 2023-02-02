import time
import haystack.nodes
from haystack.document_stores.faiss import FAISSDocumentStore
from haystack.nodes import PDFToTextConverter, PDFToTextOCRConverter, TextConverter, FileTypeClassifier
from haystack.nodes import PreProcessor, DocxToTextConverter
import logging
from haystack.pipelines import Pipeline
import os
from special_reports_extractor import SrExtractor


haystack.HAYSTACK_TELEMETRY_ENABLED = False


class Database:

    def __init__(self):
        self.document_store = None
        self.file_classifier = None
        self.converter_pdf = None
        self.converter_docx = None
        self.converter_text = None
        self.pre_processor = None
        self.extractor = None
        self.current_number_of_documents = 0
        self.name = ""

    def load_document_store(self, faiss_index_path: str, faiss_config_path: str):

        self.document_store = FAISSDocumentStore.load(index_path=faiss_index_path, config_path=faiss_config_path)
        logging.info("Database loaded. Existing Document Store initialized.")

    def update_document_store(self, path_to_documents: str, retriever: haystack.nodes.EmbeddingRetriever):

        assert self.document_store is not None, "No Document Store to update. " \
                                            "Please load a database or create a new one"
        self.file_classifier = FileTypeClassifier()
        self.converter_pdf = PDFToTextOCRConverter()
        self.converter_docx = DocxToTextConverter()
        self.converter_text = TextConverter()
        self.extractor = SrExtractor()
        self.pre_processor = PreProcessor(clean_empty_lines=True,
                                          clean_whitespace=True,
                                          clean_header_footer=True,
                                          split_by="passage",
                                          split_respect_sentence_boundary=False,
                                          split_overlap=0)

        tray_dir = os.listdir(path_to_documents)
        assert len(tray_dir) > 0, f"{tray_dir} is empty. Please provide a non-empty directory."
        new_documents = self.load_documents(path_to_documents)
        print(len(new_documents))
        self.document_store.write_documents(new_documents)
        # add assertion, must be the same retriever
        self.document_store.update_embeddings(retriever=retriever, update_existing_embeddings=True)
        logging.info("New documents embedded. Database updated.")
        """
        if not test:
            for f in os.listdir(tray_dir):
                if not f.endswith(".txt") or f.endswith(".pdf") or f.endswith(".docx"):
                    continue
                assert os.chdir == os.path(tray_dir), "Wrong directory!"
                os.remove(os.path.join(tray_dir, f))
        """

    def launch_new_document_store(self, set_file_name="special_reports_faiss_store"):
        print(os.getcwd())
        assert not os.path.exists(f"{os.getcwd()}/{set_file_name}.db"), "A Document Store with this name " \
                                                                        "already exits. Please load it."

        self.document_store = FAISSDocumentStore(faiss_index_factory_str="Flat",
                                                 sql_url=f"sqlite:///{set_file_name}.db",
                                                 embedding_dim=768,
                                                 similarity="dot_product")
        logging.info("Database created. Initialized a new Document Store")

    def load_documents(self, path_to_documents: str):
        """This method take a relative path to a folder with documents of different types.
        It converts them to text files and splits into paragraphs.
        It, then, saves all files into a new folder [name]_paragraphs.
        :param: path_to_documents: relative path to the folder with new documents (pdf,text, or docx)
        :return: haystack Documents"""

        documents_processed = []

        pipeline_preprocessing = Pipeline()
        pipeline_preprocessing.add_node(component=self.file_classifier, name="FileTypeClassifier",
                                        inputs=["File"])
        pipeline_preprocessing.add_node(component=self.converter_text, name="TextConverter",
                                        inputs=["FileTypeClassifier.output_1"])
        pipeline_preprocessing.add_node(component=self.converter_pdf, name="PdfConverter",
                                        inputs=["FileTypeClassifier.output_2"])
        pipeline_preprocessing.add_node(component=self.converter_docx, name="DocxConverter",
                                        inputs=["FileTypeClassifier.output_4"])
        pipeline_preprocessing.add_node(component=self.extractor, name="SrExtractor",
                                        inputs=["TextConverter", "PdfConverter", "DocxConverter"])

        for file in os.listdir(path_to_documents):
            # Open path_to_documents and open one-by-one, classify the type,
            # convert to text, extract metadata and paragraphs
            converted_document = pipeline_preprocessing.run(file_paths=[os.path.join(path_to_documents, file)])
            documents_processed.append(self.pre_processor.process(converted_document["documents"]))

        self.current_number_of_documents += len(documents_processed[0])

        return documents_processed[0]

    def save_database(self, path: str):
        """This method saves the Document Store of the database with a time stamp."""

        self.name = f"special_report_database_at_{str(int(time.time())).replace(' ', '_')}"
        self.document_store.save(index_path=os.path.join(path, self.name))
