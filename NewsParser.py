import requests
from PyQt6.QtCore import QObject, pyqtSignal
from bs4 import BeautifulSoup


class NewsParser(QObject):
    news_signal = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
        self.url = None
        self.element_classes = []
        self.visited_links = set()
        self.stop_parsing = False

    def set_element_classes(self, element_classes):
        self.element_classes = element_classes

    def set_url(self, url):
        self.url = url

    def stop(self):
        self.stop_parsing = True

    def parse(self):
        while not self.stop_parsing:
            if self.url:
                response = requests.get(self.url)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    news_blocks = soup.select(self.element_classes[0])

                    for news_block in news_blocks:
                        authors_element = news_block.find('div', class_=self.element_classes[1])
                        if authors_element and not any(
                                cls.startswith('timestamp') for cls in authors_element.get('class', [])):
                            authors = authors_element.text.strip()
                        else:
                            authors = None

                        if authors is not None:
                            if self.element_classes[4] is not None:
                                title_element = news_block.find(self.element_classes[2], class_=self.element_classes[4])
                            else:
                                title_element = news_block.find(self.element_classes[2])
                            title = title_element.text.strip() if title_element else "No title found"
                            annotation_element = news_block.find('div', class_=self.element_classes[3])
                            annotation = annotation_element.text.strip() if annotation_element else None

                            news_data_tuple = (title, annotation, authors)

                            if news_data_tuple not in self.visited_links:
                                self.news_signal.emit(news_data_tuple)
                                self.visited_links.add(news_data_tuple)