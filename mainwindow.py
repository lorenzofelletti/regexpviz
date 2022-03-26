from typing import List, Literal, Tuple, Union

from PySide6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QHeaderView
from PySide6.QtUiTools import QUiLoader
from PySide6.QtGui import QFontDatabase, QStandardItemModel
from PySide6.QtCore import Qt
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

        # table rows width
        header = self.main.matches_tbl.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        # enables the syntax highlighting
        self.syntax_highlighter = RegexSyntaxHighlighter(
            self.main.test_string_pte.document(), self)
        self.main.regex_le.textChanged.connect(self.__trigger_highlight__)
        self.main.find_all_matches_cb.stateChanged.connect(
            self.__trigger_highlight__)
        self.main.case_sensitive_rb.toggled.connect(self.__trigger_highlight__)
        self.main.case_insensitive_rb.toggled.connect(
            self.__trigger_highlight__)
        self.main.casefold_rb.toggled.connect(self.__trigger_highlight__)

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
        # self.__print_matches__()

    def __case_sensitivity_state__(self) -> Tuple[bool, bool, bool]:
        """ Return a tuple representing the state of the case sensitivity radio buttons.

            Returns:
                A tuple of three values, the first being if the case sensitive radio button
                is checked, the other for the case insensitive, and the third for the casefold.
        """

        return self.main.case_sensitive_rb.isChecked(), self.main.case_insensitive_rb.isChecked(), self.main.casefold_rb.isChecked()

    def get_case_sensitivity(self) -> Literal[0, 1, 2]:
        case_sensitive, case_insensitive, _ = self.__case_sensitivity_state__()
        case_sensitivity: int
        if case_sensitive:
            case_sensitivity = 0
        elif case_insensitive:
            case_sensitivity = 1
        else:
            case_sensitivity = 2
        return case_sensitivity

    def __print_matches__(self) -> None:
        regex = self.main.regex_le.text()
        test_str = self.main.test_string_pte.toPlainText()

        if len(regex) == 0:
            self.__create_matches_table__()
            return
        try:
            case_sensitivity = self.get_case_sensitivity()
            res, _, matches = self.reng.match(
                regex, test_str, True, self.main.find_all_matches_cb.isChecked(), case_sensitivity)  # test_str
            self.__create_matches_table__(matches)
        except Exception as e:
            pass

    def __create_matches_table__(self, matches: Union[List[List[Match]], None] = None) -> None:
        if matches is None:
            self.main.matches_tbl.setRowCount(0)
            return
        rows = 0
        for match in matches:
            rows += len(match)

        #self.main.matches_tbl = QTableWidget(rows,4)
        self.main.matches_tbl.setRowCount(rows)
        # self.main.matches_tbl.setColumnCount(4)

        if len(matches) == 0:
            return
        i = 0
        test_str = self.main.test_string_pte.toPlainText()
        for match in matches:
            for match_group in match:
                name_item = QTableWidgetItem(match_group.name)
                self.main.matches_tbl.setItem(i, 0, name_item)

                start_item = QTableWidgetItem(str(match_group.start_idx))
                self.main.matches_tbl.setItem(i, 1, start_item)

                end_item = QTableWidgetItem(str(match_group.end_idx))
                self.main.matches_tbl.setItem(i, 2, end_item)

                #matched_item = QTableWidgetItem('"' + match_group.match + '"')
                start_idx = match_group.start_idx if match_group.start_idx < len(
                    test_str) else len(test_str)-1
                end_idx = match_group.end_idx if match_group.end_idx < len(
                    test_str) else len(test_str)
                matched_item = QTableWidgetItem(
                    '"' + test_str[start_idx:end_idx] + '"')
                self.main.matches_tbl.setItem(i, 3, matched_item)
                i += 1


if __name__ == "__main__":
    app = QApplication()

    # loads Roboto Mono font
    QFontDatabase.addApplicationFont(
        'resources/RobotoMono/static/RobotoMono-Regular.ttf')

    # randomize the highlight colors order
    random.shuffle(highlight_colors)

    frame = RuntimeStylesheets()
    frame.main.show()

    app.exec()
