import sys
from PyQt6.QtCore import QThreadPool, QRunnable, QCoreApplication
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QApplication, QDialog
from NewsParser import NewsParser
from myUi import Ui_Dialog


class Worker(QRunnable):
    def __init__(self, parser):
        super().__init__()
        self.parser = parser

    def run(self):
        self.parser.parse()


class NewsApp(QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.news_parser = NewsParser()
        self.thread_pool = QThreadPool.globalInstance()
        self.worker = None

        self.ui.readWashingtonBtn.clicked.connect(lambda: self.start_parsing('https://www.washingtonpost.com/',
                                                                            ['[class^="card relative"]',
                                                                             'byline gray-dark font-xxxxs pb-xs', 'h2',
                                                                             'pb-xs font-size-blurb lh-fronts-tiny '
                                                                             'font-light gray-dark', None]))
        self.ui.readDigitalBtn.clicked.connect(lambda: self.start_parsing('https://www.digitaltrends.com',
                                                                         ['[class^="b-river-post b-river__item" ]',
                                                                          'b-river-post__label', 'h3',
                                                                          'b-river-post__excerpt dt-clamp dt-clamp-2 '
                                                                          'dt-clamp-large-3',
                                                                          'b-river-post__title dt-clamp dt-clamp-4']))
        self.ui.readTechBtn.clicked.connect(lambda: self.start_parsing('https://www.techspot.com',
                                                                      ['[class^="article-content" ]', 'byline', 'h2',
                                                                       'intro', None]))
        self.ui.readReadWriteBtn.clicked.connect(lambda: self.start_parsing('https://readwrite.com',
                                                                           ['[class^="col-md-9"]', 'entry-meta', 'h2',
                                                                            'entry-content', 'entry-title']))
        self.ui.exitBtn.clicked.connect(QCoreApplication.quit)

        # Create a model for the list view
        self.model = QStandardItemModel()
        self.ui.listView.setModel(self.model)

    def start_parsing(self, url, classes):
        self.model.clear()
        if self.worker:
            # Stop the existing worker
            self.worker.setAutoDelete(True)
            self.worker = None

        # Create a new instance of NewsParser for each parsing operation
        self.news_parser = NewsParser()

        # Set parser parameters
        self.news_parser.set_url(url)
        self.news_parser.set_element_classes(classes)
        self.news_parser.stop_parsing = False

        # Connect signals
        self.news_parser.news_signal.connect(self.update_ui)

        # Create a new worker
        self.worker = Worker(self.news_parser)
        self.thread_pool.start(self.worker)

    def parsing_stop(self):
        if self.worker:
            self.worker.setAutoDelete(True)
            self.worker = None

        if self.news_parser:
            self.news_parser.stop()
            self.news_parser = None

    def update_ui(self, news_data):
        title, annotation, authors = news_data

        item_text = ""

        # Create a list item for the entire news information
        item_text += f"Title: {title}\n"
        item_text += f"Annotation: {annotation}\n" if annotation else ""
        item_text += f"Authors: {authors}\n"

        # Create a single list item
        item = QStandardItem(item_text)

        # Append the item to the model
        self.model.appendRow(item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NewsApp()
    window.show()
    sys.exit(app.exec())
