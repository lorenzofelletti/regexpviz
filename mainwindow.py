from typing import List

from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QPlainTextEdit, QWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QFontDatabase, QStandardItemModel, QStandardItem
from qt_material import QtStyleTools

from regex_syntax_highlighter import RegexSyntaxHighlighter, highlight_colors
from pyregexp.engine import RegexEngine
from pyregexp.match import Match

import random


class RuntimeStylesheets(QMainWindow, QtStyleTools):
    def __init__(self) -> None:
        """ Loads the ui file and creates the QMainWindow instance."""
        super().__init__()
        self.main = QUiLoader().load('mainwindow.ui', self)

        self.reng = RegexEngine()

        # sets error_pte to read-only
        self.main.error_pte.setReadOnly(True)

        # sets overall app theme
        self.apply_stylesheet(self.main, 'dark_teal.xml')

        # sets mono font to LineEdit and PlainTextEdit
        self.apply_stylesheet(self.main.regex_le, 'dark_teal.xml', extra={
                              'font_family': 'Roboto Mono', })
        self.apply_stylesheet(self.main.error_pte, 'dark_teal.xml', extra={
                              'font_family': 'Roboto Mono', })
        self.apply_stylesheet(self.main.test_string_pte, 'dark_teal.xml', extra={
                              'font_family': 'Roboto Mono', })

        # enables the syntax highlighting
        self.syntax_highlighter = RegexSyntaxHighlighter(
            self.main.test_string_pte.document(), self.main.regex_le,
            self.main.find_all_matches_cb, self.reng)
        self.main.regex_le.textChanged.connect(self.__trigger_highlight__)
        self.main.find_all_matches_cb.stateChanged.connect(
            self.__trigger_highlight__)

    def __trigger_highlight__(self) -> None:
        """ Triggers the SyntaxHighlighter in the test string's QPlainTextEdit.

        The test string syntax highlighter is triggered whenever the test
        string text change. Thus, without this function, if I change the regex
        to search in the text, the syntax highlighter won't search the new
        regex until the test string's text is changed.

        This method forces the test string's syntax highlighter to be
        triggered.
        """
        self.main.test_string_pte.setPlainText(
            self.main.test_string_pte.toPlainText())
        self.__print_matches__()

    def __print_matches__(self) -> None:
        regex = self.main.regex_le.text()
        test_str = self.main.test_string_pte.toPlainText()
        try:
            res, _, matches = self.reng.match(
                regex, test_str, True, self.main.find_all_matches_cb.isChecked())

            if res == False:
                return

            #for match in matches:
            #    parent = QTreeWidgetItem(match[0].match)
            #    # self.main.matches_tv.setColumnCount(1)
            #    self.main.matches_tv.addTopLevelItem(parent)
            #    # for group, idx in match:
            #    #    if idx == 0:
            #    #        self.matches_tv.setColumnCount(3)
            #self.main.matches_tv.setModel(self.__create_matches_model__(matches))

        except Exception as e:
            pass
    
    def __create_matches_model__(self,matches: List[Match]) -> QStandardItemModel:
        # consider using a table instead...
        model = QStandardItemModel()

        if len(matches) == 0:
            return model

        parent_item = model.invisibleRootItem()

        for match in matches:
            item = QStandardItem(match[0].match)
            for i in range(len(match)):
                if i > 0:
                    sub_item = QStandardItem(match[i].match, parent=item)
                    #item.appendRow(sub_item)
                    #item.setChild(i-1,0,sub_item)
            parent_item.appendRow(item)
        return model


if __name__ == "__main__":
    app = QApplication()

    # loads Roboto Mono font
    QFontDatabase.addApplicationFont(
        'resources/RobotoMono/RobotoMono-VariableFont_wght.ttf')

    # randomize the highlight colors order
    random.shuffle(highlight_colors)

    frame = RuntimeStylesheets()
    frame.main.show()

    app.exec()
