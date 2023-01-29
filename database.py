import haystack.nodes
from haystack.document_stores.faiss import FAISSDocumentStore
from haystack.nodes import PDFToTextConverter, PDFToTextOCRConverter, TextConverter, FileTypeClassifier
from haystack.nodes import PreProcessor, DocxToTextConverter, EmbeddingRetriever
from engine_v2 import Engine
import logging
from haystack.pipelines import Pipeline
from re import match, search
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
    def load_document_store(faiss_index_path: str, faiss_config_path: str):
        database = Database()
        database.document_store = FAISSDocumentStore.load(index_path=faiss_index_path, config_path=faiss_config_path)
        logging.info("Database loaded. Existing Document Store initialized.")
        return database

    def update_document_store(self, path_to_documents: str, retriever: haystack.nodes.EmbeddingRetriever):
        assert self.document_store is not None, "No Document Store to update. " \
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

        tray_dir = os.listdir(path_to_documents)
        assert len(tray_dir) > 0, f"{tray_dir} is empty. Please provide a non-empty directory."
        new_documents = self.load_documents(path_to_documents)
        self.document_store.write_documents(new_documents)
        # add assertion, must be the same retriever
        self.document_store.update_embeddings(retriever=retriever, update_existing_embeddings=False)
        logging.info("New documents embedded. Database updated.")

        """
        for f in os.listdir(tray_dir):
            if not f.endswith(".txt") or f.endswith(".pdf") or f.endswith(".docx"):
                continue
            assert os.chdir == os.path.join(tray_dir), "Wrong directory!"
            os.remove(os.path.join(tray_dir, f))
        """

    def launch_new_document_store(self):
        self.document_store = FAISSDocumentStore(faiss_index_factory_str="Flat",
                                                 sql_url="sqlite:///special_reports_faiss_store.db",
                                                 embedding_dim=764,
                                                 similarity="dot_product")
        logging.info("Database created. Initialized a new Document Store")

    def extract_paragraphs(self, text_raw: str):
        """Given text documents, this method splits them into numbered paragraphs
        and saves the number of each paragraph.
        """
        i = 0

        paragraph_number_list = []
        paragraph_list = []
        while not bool(match(r'This((\sSpecial\s)|\s)(R|r)eport\swas\sadopted\sby', text_raw[i])):
            paragraph = ''

            # every paragraph must start with the number + '.' + tab sequence

            if bool(match(r'^(\d|\d\d|\d\d\d)\.\t', text_raw[i][0:10])):
                if bool(match(r'^\d\d\.', text_raw[i])):
                    paragraph_number_list.append(int(text_raw[i][0:2]))
                    paragraph += ' ' + text_raw[i][4:].strip('\n')
                    i += 1
                elif bool(match(r'^\d\d\d', text_raw[i])):
                    paragraph_number_list.append(int(text_raw[i][0:3]))
                    paragraph += ' ' + text_raw[i][5:].strip('\n')
                    i += 1
                else:
                    paragraph_number_list.append(int(text_raw[i][0]))
                    paragraph += ' ' + text_raw[i][3:].strip('\n')
                    i += 1

                # search for a full stop at the end of the line (most bullet points do not end with full stops)

                while not bool(search(r'\.($|\s+$|\n)', text_raw[i][-10:-1])):
                    paragraph += ' ' + text_raw[i].strip('\n')
                    i += 1

                paragraph += ' ' + text_raw[i].strip('\n')
                paragraph_list.append(paragraph)

        return paragraph_number_list, paragraph_list

    def extract_metadata(self, text_raw: str):
        """Given text documents, this method extracts report_title. Currently, it extracts only the title
        and report info.
        """
        i = 0
        if bool(match(r'\((p|P)ersuant\sto', text_raw[i].strip('\n'))):
            i += 1
        title = (text_raw[i].strip('\n').strip('\t') + ': ' + text_raw[i + 2].strip('\n'))
        i += 3

        report_info = ''
        while not bool(match(r'(t|T)ogether\swith', text_raw[i])):
            report_info += (' ' + text_raw[i].strip('\n'))
            i += 1
            if i > 10:
                break

        return title, report_info, i

    def load_documents(self, path_to_documents: str):
        """This method take a relative path to a folder with documents of different types.
        It converts them to text files and splits into paragraphs.
        It, then, saves all files into a new folder [name]_paragraphs.
        :param: path_to_documents: relative path to the folder with new documents (pdf,text, or docx)
        :return: haystack Documents"""

        documents_processed = []

        pipeline_preprocessing = Pipeline()
        pipeline_preprocessing.add_node(component=self.file_classifier, name="FyleTypeClassifier",
                                        inputs=["File"])
        pipeline_preprocessing.add_node(component=self.converter_txt, name="TextConverter",
                                        inputs=["FileTypeClassifier.output_1"])
        pipeline_preprocessing.add_node(component=self.converter_pdf, name="PdfConverter",
                                        inputs=["FileTypeClassifier.output_2"])
        pipeline_preprocessing.add_node(component=self.converter_docx, name="DocxConverter",
                                        inputs=["FileTypeClassifier.output_4"])

        for file in os.listdir(path_to_documents):
            # 1.open path_to_documents and open one-by-one, classify the type, convert to text
            converted_document = pipeline_preprocessing.run(file_paths=[os.path.join(path_to_documents, file)])
            # 2. Extract metadata for the whole document
            report_title, report_info, line_number = self.extract_metadata(converted_document)
            # 3. Split into paragraphs and save paragraph numbers in a list
            paragraph_numbers, paragraphs = self.extract_paragraphs(converted_document, line_number)
            # 4. Pre-process each paragraph, save as Documents, and metadata to each
            document_paragraphs = self.pre_processor.process(paragraphs)
            assert len(document_paragraphs) == len(paragraph_numbers), "Too many documents"

            # add metadata and paragraph number to each paragraph
            i = 0
            for doc in document_paragraphs:
                doc.meta["report_title"] = report_title
                doc.meta["report_info"] = report_info
                doc.meta["paragraph_number"] = paragraph_numbers[i]
                i += 1

            documents_processed.append(document_paragraphs)

        return documents_processed
