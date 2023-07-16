import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QDialog
from get_info import *

class MainFunction(QDialog):
    def __init__(self, session, name, stu_id):
        super().__init__()
        self.setWindowTitle("温大教务系统助手")
        self.resize(300, 100)

        self.text_label = QLabel("请选择操作")
        self.get_test_score_button = QPushButton("查询成绩")
        self.enroll_course_button = QPushButton("选课")
        self.get_course_timetable_button = QPushButton("查看课表")

        self.get_test_score_button.clicked.connect(self.test_score)
        # self.enroll_course_button.clicked.connect(self.login)
        self.get_course_timetable_button.clicked.connect(self.course_timetable)

        layout = QVBoxLayout()
        layout.addWidget(self.text_label)
        layout.addWidget(self.get_test_score_button)
        layout.addWidget(self.get_course_timetable_button)

        self.setLayout(layout)

        self.ssession = session
        self.stu_id = stu_id
        self.name = name

    def test_score(self):
        get_test_score(self.ssession, self.name, self.stu_id)

    def course_timetable(self):
        get_course_timetable(self.ssession, self.name, self.stu_id)
