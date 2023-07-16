import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from get_info import login_zhengfang
from interface_mainFunction import MainFunction

class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("登录界面")
        self.resize(300, 100)

        self.username_label = QLabel("用户名:")
        self.password_label = QLabel("密码:")
        self.login_button = QPushButton("登录")

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button.clicked.connect(self.login)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # 登录
        ret = login_zhengfang(username, password)
        if ret[1] == 503:
            QMessageBox.warning(self, "登录失败", "登录次数过多，请在一段时间后重试！")
        elif ret[0] == 401:
            QMessageBox.warning(self, "登录失败", "请检查账号密码，在校园网环境下登录！")
        elif ret[0] == 200 and ret[1] == 200:
            QMessageBox.warning(self, "登录成功", "登录成功！")
            dialog = MainFunction(ret[2], ret[3], ret[4])
            dialog.exec_()
        else:
            QMessageBox.warning(self, "登录失败", "未知错误，请重试！")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    login_widget = Login()
    login_widget.show()

    sys.exit(app.exec_())
