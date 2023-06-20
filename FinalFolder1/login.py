import csv
import sqlite3
from PySide6 import QtCore, QtGui, QtWidgets, QtUiTools
from FinalFolder.mainwindow_ui import MainWindowUI


class Login(QtWidgets.QWidget):
    switch_window = QtCore.Signal()
    switch_window1 = QtCore.Signal()

    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        loader = QtUiTools.QUiLoader()

        file = QtCore.QFile("login.ui")
        file.open(QtCore.QFile.OpenMode.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()
        self.username = None

        self.btn_newuser = self.ui.findChild(QtWidgets.QPushButton, "btn_newuser")
        self.btn_Submit = self.ui.findChild(QtWidgets.QPushButton, "btn_Submit")
        self.txt_username = self.ui.findChild(QtWidgets.QLineEdit, "txt_username")
        self.txt_password = self.ui.findChild(QtWidgets.QLineEdit, "txt_password")

        self.btn_newuser.clicked.connect(self.btn_newuser_handler)
        self.btn_Submit.clicked.connect(self.btn_submit_handler)

    def pop_message(self, text=""):
        msg = QtWidgets.QMessageBox()
        msg.setText("{}".format(text))
        msg.exec()

    def bool_check_username(self):
        if len(self.txt_password.text()) <= 1:
            self.pop_message(text='Enter Valid Username and Password !')
        else:
            username = self.txt_username.text()
            password = self.txt_password.text()
            conn = sqlite3.connect('.\Data.db')
            cursor = conn.cursor()
            cursor.execute("SELECT username,password FROM credentials")
            val = cursor.fetchall()
            if len(val) >= 1:
                for x in val:
                    if username in x[0] and password in x[1]:
                        return True
                    else:
                        pass
            else:
                self.pop_message(text="No users Found ")
                return False

    def btn_submit_handler(self):
        val = self.bool_check_username()

        if val:
            self.pop_message(text="Welcome")
            self.open_mainwindow(self.txt_username.text())

        else:
            self.pop_message("Invalid username or password")

    def btn_newuser_handler(self):
        self.switch_window.emit()

    def open_mainwindow(self, username):
        self.hide()
        self.window = MainWindowUI()
        self.window.setupUi(username)


class NewUser(QtWidgets.QWidget):
    switch_window = QtCore.Signal()

    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        loader = QtUiTools.QUiLoader()
        file = QtCore.QFile("Newuser.ui")
        file.open(QtCore.QFile.OpenMode.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()

        self.Back = self.ui.findChild(QtWidgets.QPushButton, "Back")
        self.btn_submit = self.ui.findChild(QtWidgets.QPushButton, "btn_submit")
        self.txt_firstname = self.ui.findChild(QtWidgets.QLineEdit, "txt_firstname")
        self.txt_lastname = self.ui.findChild(QtWidgets.QLineEdit, "txt_lastname")
        self.txt_phone = self.ui.findChild(QtWidgets.QLineEdit, "txt_phone")
        self.txt_email = self.ui.findChild(QtWidgets.QLineEdit, "txt_email")
        self.txt_username = self.ui.findChild(QtWidgets.QLineEdit, "txt_username")
        self.lineEdit = self.ui.findChild(QtWidgets.QLineEdit, "lineEdit")

        self.Back.clicked.connect(self.back_handler)
        self.btn_submit.clicked.connect(self.btn_submit_handler)

    def create_csv_file(self, username):
        conn = sqlite3.connect('.\Data.db')
        cursor = conn.cursor()

        # Выполнение запроса для получения данных пользователя
        cursor.execute("SELECT * FROM credentials WHERE username = ?", (username,))
        user = cursor.fetchone()

        if user:
            csv_filename = f'{username}_file.csv'
            with open(csv_filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(
                    ['uid', 'title', 'synopsis', 'genre', 'aired', 'episodes', 'members', 'popularity', 'ranked',
                     'score', 'img_url', 'link'])

            self.pop_message(f"CSV file '{csv_filename}' created successfully.")
        else:
            self.pop_message("Failed to create CSV file.")

        cursor.close()
        conn.close()

    def btn_submit_handler(self):
        self.create_db_newuser()
        username = self.txt_username.text()
        self.create_csv_file(username)
        self.switch_window.emit(username)

    def pop_message(self, text=""):
        msg = QtWidgets.QMessageBox()
        msg.setText("{}".format(text))
        msg.exec()

    def back_handler(self):
        self.close()  # Close the current window
        self.switch_window.emit()

    def create_db_newuser(self):
        txt_firstname_v = self.txt_firstname.text()
        txt_lastname_v = self.txt_lastname.text()
        txt_phone_v = self.txt_phone.text()
        txt_emailid_v = self.txt_email.text()
        txt_username_v = self.txt_username.text()
        txt_password_v = self.lineEdit.text()

        if not (
                txt_firstname_v and txt_lastname_v and txt_phone_v and txt_emailid_v and txt_username_v and txt_password_v):
            self.pop_message(text="Please Enter All Fields")
        else:
            conn = sqlite3.connect('/check/FinalFolder/FinalFolder1\Data.db')
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS credentials 
                (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                fname TEXT, 
                lname TEXT, 
                Phone TEXT, 
                email TEXT,
                username TEXT, 
                password TEXT)""")

            cursor.execute("""INSERT INTO credentials 
                (fname, lname, Phone, email, username, password)
                VALUES (?, ?, ?, ?, ?, ?)""",
                           (
                               txt_firstname_v, txt_lastname_v, txt_phone_v, txt_emailid_v, txt_username_v,
                               txt_password_v))

            conn.commit()
            cursor.close()
            conn.close()
            self.pop_message(text="Added to Database!")


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    login = Login()
    new_user = NewUser()

    login.switch_window.connect(new_user.show)
    new_user.switch_window.connect(login.show)
    login.switch_window1.connect(lambda: print("Switch to another window"))

    login.show()
    sys.exit(app.exec())
