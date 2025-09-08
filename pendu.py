import sys
import random
import pygame
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QComboBox, QGridLayout, QStackedLayout
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt

def load_words(language):
    filename = {
        "Français": "mots/francais.txt",
        "English": "mots/english.txt",
        "Deutsch": "mots/deutsch.txt"
    }.get(language, "mots/francais.txt")

    try:
        with open(filename, "r", encoding="utf-8") as f:
            words = [line.strip() for line in f if line.strip()]
        return words if words else ["ERREUR"]
    except FileNotFoundError:
        return ["ERREUR"]

class Menu(QWidget):
    def __init__(self, switch_to_game, show_scores):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        self.setLayout(layout)

        title = QLabel("🪢 Jeu du Pendu Multilingue_apprentissage")
        title.setFont(QFont("Arial", 20))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        play_button = QPushButton("🎮 Jouer")
        play_button.clicked.connect(switch_to_game)

        score_button = QPushButton("📊 Voir les scores")
        score_button.clicked.connect(show_scores)

        quit_button = QPushButton("🚪 Quitter")
        quit_button.clicked.connect(QApplication.instance().quit)

        for btn in (play_button, score_button, quit_button):
            btn.setFont(QFont("Arial", 14))
            btn.setFixedHeight(40)
            layout.addWidget(btn)

class HangmanGame(QWidget):
    def __init__(self, return_to_menu):
        super().__init__()
        pygame.mixer.init()
        self.return_to_menu = return_to_menu
        self.language = "Français"
        self.word = ""
        self.guessed_letters = []
        self.max_tries = 10  # 🔥 Plus d'essais !
        self.remaining_tries = self.max_tries
        self.letter_buttons = {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        top_bar = QHBoxLayout()
        back_btn = QPushButton("🔙 Menu")
        back_btn.clicked.connect(self.return_to_menu)
        top_bar.addWidget(back_btn)
        layout.addLayout(top_bar)

        lang_layout = QHBoxLayout()
        lang_label = QLabel("Langue:")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Français", "English", "Deutsch"])
        start_button = QPushButton("Démarrer 🎯")
        start_button.clicked.connect(self.start_game)

        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addWidget(start_button)
        layout.addLayout(lang_layout)

        self.image_label = QLabel()
        self.image_label.setPixmap(QPixmap("images/pendu_0.png"))
        layout.addWidget(self.image_label)

        self.word_label = QLabel("")
        self.word_label.setFont(QFont("Arial", 24))
        layout.addWidget(self.word_label)

        self.tries_label = QLabel("")
        self.tries_label.setFont(QFont("Arial", 16))
        layout.addWidget(self.tries_label)

        self.keyboard_layout = QGridLayout()
        layout.addLayout(self.keyboard_layout)

    def start_game(self):
        self.language = self.lang_combo.currentText()
        words = load_words(self.language)
        self.word = random.choice(words).upper()
        self.guessed_letters = []
        self.remaining_tries = self.max_tries
        self.update_display()
        self.create_keyboard()

    def create_keyboard(self):
        while self.keyboard_layout.count():
            child = self.keyboard_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.letter_buttons = {}
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ" if self.language == "Deutsch" else "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        row, col = 0, 0
        for letter in alphabet:
            button = QPushButton(letter)
            button.setFixedSize(35, 35)
            button.setStyleSheet("font-weight: bold;")
            button.clicked.connect(lambda checked, l=letter: self.check_letter(l))
            self.keyboard_layout.addWidget(button, row, col)
            self.letter_buttons[letter] = button
            col += 1
            if col == 8:
                row += 1
                col = 0

    def check_letter(self, letter):
        if letter in self.guessed_letters:
            return

        self.guessed_letters.append(letter)

        btn = self.letter_buttons.get(letter)
        if btn:
            if letter in self.word:
                btn.setStyleSheet("background-color: lightgreen; font-weight: bold;")
                self.play_sound("sons/correct.wav")
            else:
                btn.setStyleSheet("background-color: lightcoral; font-weight: bold;")
                self.remaining_tries -= 1
                self.play_sound("sons/wrong.wav")
            btn.setEnabled(False)

        self.update_display()

        if all(c in self.guessed_letters or c == " " for c in self.word):
            self.play_sound("sons/win.wav")
            self.save_score(True)
            self.show_message("🎉 Bravo !", f"Tu as trouvé : {self.word}")
        elif self.remaining_tries == 0:
            self.play_sound("sons/lose.wav")
            self.save_score(False)
            self.show_message("💀 Perdu !", f"Le mot était : {self.word}")

    def update_display(self):
        display_word = " ".join([c if c in self.guessed_letters else "_" for c in self.word])
        self.word_label.setText(display_word)
        self.tries_label.setText(f"Essais restants : {self.remaining_tries}")
        current_image_index = self.max_tries - self.remaining_tries
        self.image_label.setPixmap(QPixmap(f"images/pendu_{current_image_index}.png"))

    def show_message(self, title, message):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        self.start_game()

    def play_sound(self, path):
        try:
            pygame.mixer.Sound(path).play()
        except Exception as e:
            print(f"Erreur son : {e}")

    def save_score(self, won: bool):
        result = "gagné" if won else "perdu"
        with open("scores.txt", "a", encoding="utf-8") as f:
            f.write(f"{self.language} : {self.word} => {result}\n")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pendu Multilingue")
        self.setGeometry(100, 100, 520, 600)

        self.stack = QStackedLayout()
        self.setLayout(self.stack)

        self.menu = Menu(self.show_game, self.show_scores)
        self.game = HangmanGame(self.show_menu)

        self.stack.addWidget(self.menu)
        self.stack.addWidget(self.game)

        self.show_menu()

    def show_menu(self):
        self.stack.setCurrentWidget(self.menu)

    def show_game(self):
        self.stack.setCurrentWidget(self.game)

    def show_scores(self):
        if os.path.exists("scores.txt"):
            with open("scores.txt", "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = "Aucun score enregistré."

        msg = QMessageBox()
        msg.setWindowTitle("📊 Scores")
        msg.setText(content)
        msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

