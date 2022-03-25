from PySide6 import QtGui, QtWidgets
from pyregexp.engine import RegexEngine


highlight_colors = [
    "#EF5350", "#D50000", "#880E4F", "#AB47BC", "#D500F9",
    "#311B92", "#7986CB", "#1A237E", "#304FFE", "#2196F3",
    "#18FFFF", "#1B5E20", "#00E676", "#A5D6A7", "#76FF03",
    "#C6FF00", "#FFD600", "#E65100", "#DD2C00", "#FFAB91",
    "#4E342E", "#BDBDBD", "#00695C", "#607D8B", "#7C4DFF"
]


class RegexSyntaxHighlighter(QtGui.QSyntaxHighlighter):
    """ Highlights groups matched by a regex. 

    Uses the pyregexp library's regular expression engine to search through
    some text and highlight the recognized regexes (using a different color)
    for each matched group. 
    """

    def __init__(self, parent: QtGui.QTextDocument, mainwindow: QtWidgets.QMainWindow) -> None:
        super().__init__(parent)
        self.mainwindow = mainwindow
        self.regex: QtWidgets.QLineEdit = mainwindow.main.regex_le
        self.reng: RegexEngine = mainwindow.reng
        self.match_all_cb: QtWidgets.QCheckBox = mainwindow.main.find_all_matches_cb

    def __format_block__(self, group_id: int) -> QtGui.QTextCharFormat:
        """ Returns the format to use.

        Returns the format with the foreground and background colors to use for
        the passed group_id
        """

        format = QtGui.QTextCharFormat()
        color = QtGui.QColor(
            highlight_colors[group_id % len(highlight_colors)])
        if (color.red() * 0.299 + color.green() * 0.587 + color.blue() * 0.114) > 186:
            format.setForeground(QtGui.QColor("#050505"))
        format.setBackground(color)
        return format

    def highlightBlock(self, text: str) -> None:
        """ Highlight text matching a regex.

        Highlights the text matching the regex present in the QLineEdit passed
        to the constructor.

        The regex engine used is from the pyregexp library.
        """
        # clears any error previously shown
        self.mainwindow.main.error_pte.setPlainText('')

        try:
            case_sensitivity = self.mainwindow.get_case_sensitivity()
            res, _, matches = self.reng.match(
                self.regex.text(), text, True, self.match_all_cb.isChecked(), case_sensitivity)
            if not res:
                return
            for matched_groups in matches:
                for match in matched_groups:
                    if match is None or match.group_id < 0:
                        err = "'None'" if match is None else "'negative group_id'"
                        raise Exception(f"Unexpected match result: {err}.")
                    self.setFormat(match.start_idx, match.end_idx-match.start_idx,
                                   self.__format_block__(match.group_id))
        except Exception as e:
            self.mainwindow.main.error_pte.setPlainText(repr(e))
            pass
        self.setCurrentBlockState(0)
