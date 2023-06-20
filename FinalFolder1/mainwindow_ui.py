import requests as requests
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QTableWidgetItem, QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QPixmap
from PySide6 import QtWidgets
import pandas as pd
import csv
import os
from FinalFolder.animedatabasemanager import AnimeDatabaseManager
import webbrowser


class MainWindowUI:
    def __init__(self, parent=None):
        self.database_manager = None
        self.sort_title_button = None
        self.parent = parent
        self.window = None
        self.get_info_button = None
        self.get_info_button_2 = None
        self.remove_anime = None
        self.anime_data_window = None
        self.username = None

    def setupUi(self, username):
        self.username = username
        loader = QUiLoader()
        ui_file = os.path.join(os.path.dirname(__file__), "MainWindow1.ui")
        self.window = loader.load(ui_file)

        self.window.lineEdit.textChanged.connect(self.find_data)

        # Создаем базу данных аниме
        self.database_manager = AnimeDatabaseManager()

        self.add_button = self.window.findChild(QPushButton, "pushButton_info_2")
        self.add_button.clicked.connect(lambda: self.add_selected_anime())

        self.remove_anime = self.window.findChild(QPushButton, "pushButton_remove")
        self.remove_anime.clicked.connect(lambda: self.remove_selected_anime())

        # Загружаем данные из CSV файла
        self.load_csv("animes.csv")

        self.sort_title_button = self.window.pushButton_STitle

        self.sort_title_button.clicked.connect(self.sort_by_title)

        self.get_info_button = self.window.findChild(QPushButton, "pushButton_info")
        self.get_info_button.clicked.connect(lambda: self.open_anime_data(self.window.tableWidget))

        self.get_info_button_2 = self.window.findChild(QPushButton, "pushButton_info_1")
        self.get_info_button_2.clicked.connect(lambda: self.open_anime_data(self.window.tableWidget_2))

        self.window.show()

    def open_link(self, url):
        webbrowser.open(url)

    def pop_message(self, text=""):
        msg = QtWidgets.QMessageBox()
        msg.setText("{}".format(text))
        msg.exec()

    def load_csv(self, filename):
        with open(filename, newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            header = next(reader)
            self.window.tableWidget.setColumnCount(len(header))
            self.window.tableWidget.setHorizontalHeaderLabels(header)

            for row, data in enumerate(reader):
                self.window.tableWidget.insertRow(row)
                for col, value in enumerate(data):
                    item = QTableWidgetItem(value)
                    if col == 2:  # Скрываем столбец с синопсисом
                        item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    self.window.tableWidget.setItem(row, col, item)

                    # Добавляем аниме в базу данных
                    self.database_manager.add_anime(data)

    def add_selected_anime(self):
        selected_rows = self.window.tableWidget.selectionModel().selectedRows()

        if len(selected_rows) > 0:
            anime_data = []
            for column in range(self.window.tableWidget.columnCount()):
                item = self.window.tableWidget.item(selected_rows[0].row(), column)
                if item is not None:
                    anime_data.append(item.text())

            csv_filename = f'{self.username}_file.csv'

            # Проверка на наличие аниме в базе
            if self.database_manager.is_anime_in_database(anime_data[0]):
                # Аниме уже существует в базе, выводим сообщение и прекращаем выполнение функции
                self.pop_message(text="YOU ALREADY HAVE THIS ANIME IN YOUR LIST")
                self.window.tableWidget.clearSelection()
                return

            # Добавление аниме в таблицу и запись в CSV файл
            row_count = self.window.tableWidget_2.rowCount()
            self.window.tableWidget_2.insertRow(row_count)
            for col, data in enumerate(anime_data):
                item = QTableWidgetItem(data)
                self.window.tableWidget_2.setItem(row_count, col, item)

            # Запись данных аниме в файл CSV
            with open(csv_filename, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(anime_data)

            # Очистка tableWidget_2
            self.window.tableWidget_2.clearContents()
            self.window.tableWidget_2.setRowCount(0)

            # Чтение CSV файла в DataFrame
            df = pd.read_csv(csv_filename, encoding='Windows-1250')

            # Заполнение tableWidget_2 данными из DataFrame
            self.window.tableWidget_2.setRowCount(len(df))
            self.window.tableWidget_2.setColumnCount(len(df.columns))
            for row in range(len(df)):
                for col in range(len(df.columns)):
                    item = QTableWidgetItem(str(df.iloc[row, col]))
                    self.window.tableWidget_2.setItem(row, col, item)

        self.window.tableWidget.clearSelection()

    def remove_selected_anime(self):
        selected_rows = self.window.tableWidget_2.selectionModel().selectedRows()

        if len(selected_rows) > 0:
            row_indexes = [row.row() for row in selected_rows]

            csv_filename = f'{self.username}_file.csv'

            # Чтение данных из CSV-файла
            with open(csv_filename, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                data = list(reader)

            # Удаление выбранных строк из данных
            updated_data = [row for i, row in enumerate(data) if i not in row_indexes]

            # Запись обновленных данных в CSV-файл
            with open(csv_filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(updated_data)

            # Очистка tableWidget_2
            self.window.tableWidget_2.clearContents()
            self.window.tableWidget_2.setRowCount(0)

            # Заполнение tableWidget_2 данными из обновленного CSV-файла
            with open(csv_filename, 'r', newline='') as csvfile:
                reader = csv.reader(csvfile)
                data = list(reader)

            self.window.tableWidget_2.setRowCount(len(data))
            self.window.tableWidget_2.setColumnCount(len(data[0]))
            for row, row_data in enumerate(data):
                for col, item in enumerate(row_data):
                    table_item = QTableWidgetItem(item)
                    self.window.tableWidget_2.setItem(row, col, table_item)

        self.window.tableWidget_2.clearSelection()

    @Slot()
    def find_data(self):
        search_text = self.window.lineEdit.text()
        if search_text:
            for row in range(self.window.tableWidget.rowCount()):
                title_item = self.window.tableWidget.item(row, 1)
                if title_item and search_text.lower() in title_item.text().lower():
                    self.window.tableWidget.setRowHidden(row, False)
                else:
                    self.window.tableWidget.setRowHidden(row, True)
        if search_text:
            for row in range(self.window.tableWidget_2.rowCount()):
                title_item = self.window.tableWidget_2.item(row, 1)
                if title_item and search_text.lower() in title_item.text().lower():
                    self.window.tableWidget_2.setRowHidden(row, False)
                else:
                    self.window.tableWidget_2.setRowHidden(row, True)

    @Slot()
    def sort_by_title(self):
        self.window.tableWidget.setSortingEnabled(True)
        self.window.tableWidget.sortItems(1)
        self.window.tableWidget_2.setSortingEnabled(True)
        self.window.tableWidget_2.sortItems(1)

    @Slot(object)
    def open_anime_data(self, table):
        selected_items = table.selectedItems()

        if len(selected_items) > 0:
            anime_data = []
            for item in selected_items:
                anime_data.append(item.text())

            loader = QUiLoader()
            ui_file = os.path.join(os.path.dirname(__file__), "AnimeData1.ui")
            self.anime_data_window = loader.load(ui_file)

            self.anime_data_window.label_title.setText(anime_data[1])
            self.anime_data_window.label_synopsis.setText(anime_data[2])
            self.anime_data_window.label_synopsis.setWordWrap(True)
            self.anime_data_window.label_genre.setText(anime_data[3])
            self.anime_data_window.label_aired.setText(anime_data[4])
            self.anime_data_window.label_episodes.setText(anime_data[5])
            self.anime_data_window.label_members.setText(anime_data[6])
            self.anime_data_window.label_popularity.setText(anime_data[7])
            self.anime_data_window.label_ranked.setText(anime_data[8])
            self.anime_data_window.label_score.setText(anime_data[9])

            self.anime_data_window.label_image.setText(anime_data[10])
            self.anime_data_window.button_open_image.clicked.connect(lambda: self.open_link(anime_data[10]))

            self.anime_data_window.label_link.setText(anime_data[11])
            self.anime_data_window.label_link.setOpenExternalLinks(True)
            self.anime_data_window.label_link.linkActivated.connect(self.open_link)
            self.anime_data_window.button_open_link.clicked.connect(lambda: self.open_link(anime_data[11]))

            self.anime_data_window.show()
            app = QApplication.instance()
            if app is None:
                app = QApplication([])
            app.exec_()

            if table is None:
                self.window.tableWidget.clearSelection()
            else:
                table.clearSelection()
