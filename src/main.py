import sys
import os
import numpy as np
from numpy import linalg as la

from MainWindow import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QInputDialog, QFileDialog, QApplication, QSizePolicy
from PyQt5.QtCore import QObject, pyqtSignal, QSize, Qt
from PyQt5.QtGui import QPixmap, QColor, QPainter, QBrush, QImage
from tqdm import tqdm

from naiveAlgorithm import naive_algorithm
from DLT import show_dlt
from normalized_DLT import show_normalized


class MainWindow(QMainWindow, Ui_MainWindow, QObject):
    all_points_given_signal = pyqtSignal()  # Pravi se signal koji će biti korišćen da obavesti kada se unesu sve tačke

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.beforeDots = []  # Niz tačaka slike pre otklanjanja distorzije
        self.afterDots = []  # Niz tačaka druge slike

        self.num_of_dots = 0  # Broj tačaka koji će biti korišćen ( unosi korisnik )

        self.first = False
        self.second = False

        self.setupUi(self)

        self.original_file = ""

        self.imageBefore = QPixmap()  # Učitana slika čuva se kao mapa piksela
        self.imageAfter = QPixmap()   # Slika koju pravi algoritam čuva se kao mapa piksela

        # Koriste se za crtanje tacaka na slikama
        self.painterBefore = QPainter()
        self.painterAfter = QPainter()

        self.init_gui()
        self.init_menu()

    def init_gui(self):
        self.labelBefore.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.labelAfter.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        self.labelBefore.mousePressEvent = self.get_pos
        self.labelAfter.mousePressEvent = self.get_pos

        self.get_num_of_dots()
        self.all_points_given_signal.connect(self.get_dots)  # Na signal poziva se funkcija get_dots
        self.loadButton.pressed.connect(self.load)  # Na klik na dugme "Učitaj sliku" poziva se funkcija load
        self.workButton.pressed.connect(self.work)  # Na klik na dugme "Primeni" poziva se funkcija work

    def init_menu(self):
        # Pritiskom na Esc ili u padajućem meniju na Izlaz izlazi se iz programa
        self.actionExit.triggered.connect(sys.exit)

        # Pritiskom na Ctrl + S ili u padajućem meniju na sačuvaj sliku čuva se slika dobijena iz algoritma
        self.actionSave.triggered.connect(self.save)

    def get_num_of_dots(self):
        num, ok = QInputDialog.getInt(self, "Broj tačaka", "Unesite broj tačaka koji će biti korišćen: ( >= 4 )")

        if ok and num >= 4:
            self.num_of_dots = num
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Greška")
            msg.setText("Broj tačaka mora biti >= 4!")
            msg.exec_()
            sys.exit()

    def load(self):
        file, _ = QFileDialog(self).getOpenFileName(self, "Open file", "", "Image files (*.bmp)")

        filename, file_extension = os.path.splitext(file)
        if file_extension != ".bmp":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Greška")
            msg.setText("Učitana slika mora biti u .bmp formatu!")
            msg.exec_()
            return

        self.imageBefore = QPixmap(filename)  # Učitava se slika kao mapa piksela
        self.original_file = filename

        if not self.imageBefore.isNull():
            # Postavlja se slika u okvir na prozoru za prikaz
            self.labelBefore.setPixmap(
                self.imageBefore.scaled(QSize(self.labelBefore.width(), self.labelBefore.height())))

            # Postavlja se da se slika uveličava i smanjuje sa labelom
            self.labelBefore.setScaledContents(True)

        # Pravi se crna slika koja će se upisati u okvir za novu sliku
        self.imageAfter = QPixmap(self.imageBefore.width(), self.imageBefore.height())
        self.imageAfter.fill(QColor("black"))

        self.labelAfter.setPixmap(
            self.imageAfter.scaled(QSize(self.labelAfter.width(), self.labelAfter.height())))

        # Postavlja se da se slika uveličava i smanjuje sa labelom
        self.labelAfter.setScaledContents(True)

        self.painterBefore = QPainter(self.imageBefore)
        self.painterBefore.setBrush(QBrush(Qt.blue))

        self.painterAfter = QPainter(self.imageAfter)
        self.painterAfter.setBrush(QBrush(Qt.red))

        self.first = True  # Omogučava se kliktanje po prvoj slici
        self.loadButton.setEnabled(False)
        self.get_dots()  # Poziva se funkcija za prikupljanje tačaka

    def get_dots(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Unos tačaka")

        # Ako je omogučeno kliktanje po prvoj slici
        if self.first:
            # Ovde se samo proverava broj tačaka da bi se gramatički tačno ispisala poruka :)
            if self.num_of_dots == 4:
                msg.setText("Unesite 4 tačke prve slike: ")
            else:
                msg.setText("Unesite " + str(self.num_of_dots) + " tačaka prve slike: ")
            msg.exec_()

            self.label.setText(self.label.text() + "\n" + "- Tačke prve slike: ( Ispisuju se u odnosu na original )\n")
        # Ako je omogučeno kliktanje po drugoj a onemogućeno kliktanje po prvoj slici
        elif not self.first and self.second:
            # Ovde se samo proverava broj tačaka da bi se gramatički tačno ispisala poruka :)
            if self.num_of_dots == 4:
                msg.setText("Unesite 4 tačke druge slike: ")
            else:
                msg.setText("Unesite " + str(self.num_of_dots) + " tačaka druge slike: ")
            msg.exec_()

            self.label.setText(self.label.text() + "\n" + "- Tačke druge slike: ( Ispisuju se u odnosu na original )\n")
        else:
            # Ako je unet dovoljan broj tačaka omogučava se dugme za primenu algoritama
            if len(self.beforeDots) == self.num_of_dots and len(self.afterDots) == self.num_of_dots:
                self.workButton.setEnabled(True)
                self.painterAfter.end()

    def work(self):
        if self.naiveAlgorithm.isChecked():
            P = naive_algorithm(self.beforeDots, self.afterDots)
            P_inv = la.inv(P)
        elif self.dltAlgorithm.isChecked():
            P = show_dlt(self.beforeDots, self.afterDots)
            P_inv = la.inv(P)
        elif self.dltNormAlgorithm.isChecked():
            P = show_normalized(self.beforeDots, self.afterDots)
            P_inv = la.inv(P)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Greška")
            msg.setText("Izaberite algoritam!")
            msg.exec_()
            return

        imgBefore = QImage(self.original_file)
        imgAfter = QPixmap(self.imageBefore.width(), self.imageBefore.height())
        imgAfter.fill(QColor("black"))
        imgAfter = imgAfter.toImage()

        for i in tqdm(range(imgBefore.width())):
            for j in range(imgBefore.height()):
                pixel = P_inv.dot(np.array([i, j, 1]))

                if pixel[0] < 0 or pixel[0] >= self.imageBefore.width():
                    continue

                if pixel[1] < 0 or pixel[1] >= self.imageBefore.height():
                    continue

                pix = imgBefore.pixelColor(pixel[0], pixel[1])
                imgAfter.setPixel(i, j, pix.rgb())

        self.imageAfter = QPixmap.fromImage(imgAfter)
        self.labelAfter.setPixmap(
            self.imageAfter.scaled(QSize(self.labelAfter.width(), self.labelAfter.height())))

        self.workButton.setEnabled(False)

    def get_pos(self, event):
        if self.first:
            x = event.pos().x()
            y = event.pos().y()

            # Skaliraju se koordinate da bi se dobile koordinate početne slike
            S_x = self.imageBefore.width() / self.labelBefore.width()
            x = x * S_x

            S_y = self.imageBefore.height() / self.labelBefore.height()
            y = y * S_y

            self.painterBefore.drawEllipse(x - 5, y - 5, 10, 10)

            self.labelBefore.setPixmap(
                self.imageBefore.scaled(QSize(self.labelBefore.width(), self.labelBefore.height())))

            self.beforeDots.append((x, y, 1))
            self.label.setText(self.label.text() + " " + str((round(x), round(y))))
        elif self.second:
            x = event.pos().x()
            y = event.pos().y()

            # Skaliraju se koordinate da bi se dobile koordinate krajnje slike bez skaliranja da stane u prozor
            S_x = self.imageAfter.width() / self.labelAfter.width()
            x = x * S_x

            S_y = self.imageAfter.height() / self.labelAfter.height()
            y = y * S_y

            self.painterAfter.drawEllipse(x - 5, y - 5, 10, 10)
            self.labelAfter.setPixmap(
                self.imageAfter.scaled(QSize(self.labelAfter.width(), self.labelAfter.height())))

            self.afterDots.append((x, y, 1))
            self.label.setText(self.label.text() + " " + str((round(x), round(y))))

        # Ako se unese dovoljno prvih tačaka traži se isti broj drugih
        if len(self.beforeDots) == self.num_of_dots and self.first:
            self.first = False
            self.second = True
            self.labelBefore.mousePressEvent = self.empty_func
            self.all_points_given_signal.emit()

        if len(self.afterDots) == self.num_of_dots and self.second:
            self.second = False
            self.all_points_given_signal.emit()

    def empty_func(self, event):
        pass

    def save(self):
        # Čuva se dobijena slika
        file, file_type = QFileDialog(self).getSaveFileName(self,
                                                            "Save file",
                                                            "",
                                                            "BMP (*.bmp);;PNG (*.png);;JPEG (*.jpeg)"
                                                            )

        filename, file_extension = os.path.splitext(file)

        if file_extension == "":
            if file_type == "BMP (*.bmp)":
                file_extension = ".bmp"
            elif file_type == "PNG (*.png)":
                file_extension = ".png"
            elif file_type == "JPEG (*.jpeg)":
                file_extension = ".jpeg"

        if file_extension == ".bmp" or file_extension == ".png" or file_extension == ".jpeg":
            self.imageAfter.save(file)

            QMessageBox.about(self, "Informacija", "Slika sačuvana.")
        else:
            QMessageBox.about(self, "Informacija", "Slika ne može biti sačuvana! ( Proveriti tip fajla... )")


def window():
    app = QApplication(sys.argv)
    win = MainWindow()

    win.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    window()
