# $Language="Python3"
# $Interface="1.0"
"""
GPON Huawei Diagnostic Tool - Qt Application

Полноценное GUI приложение для диагностики ONT Huawei.
Работает с SecureCRT через COM или встроенный Python.

Требования:
    pip install PyQt6 pywin32 pyperclip
"""

import sys
import os
import re
from datetime import datetime

# Добавляем путь к модулям проекта
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from PyQt6.QtGui import *
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    PyQt6_AVAILABLE = True
except ImportError:
    PyQt6_AVAILABLE = False
    print("ERROR: PyQt6 не установлен. Установите через: pip install PyQt6")
    sys.exit(1)

# Импортируем GPON классы
try:
    from GPON_class import GPON, Ont, inject_crt
except ImportError:
    print("ERROR: GPON_class.py не найден")
    sys.exit(1)

# Импортируем бридж для SecureCRT
try:
    from GPON_HW.qt_securecrt_bridge import SecureCRTBridge
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False
    print("WARNING: SecureCRTBridge не доступен (pywin32)")


class GPONWorker(QThread):
    """Фоновый поток для диагностики ONT"""
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(str)
    log_message = pyqtSignal(str)

    def __init__(self, ont_data, mode="securecrt"):
        super().__init__()
        self.ont_data = ont_data
        self.mode = mode  # "securecrt" или "internal"
        self.crt = None
        
    def run(self):
        try:
            # Парсинг ONT ID
            self.progress_update.emit("Парсинг ONT ID...")
            ont_parts = self.ont_data.split()
            
            if len(ont_parts) < 4:
                raise ValueError("Некорректный формат ONT ID. Ожидается: F S P O [SN]")
            
            ont = Ont(ont_parts)
            self.log_message.emit(f"ONT: {ont.frame}/{ont.slot}/{ont.port}/{ont.ont}")
            if ont.sn:
                self.log_message.emit(f"SN: {ont.sn}")
            
            # Режим 1: Встроенный Python в SecureCRT
            if self.mode == "securecrt" and self.crt:
                self.log_message.emit("Режим: Встроенный Python SecureCRT")
                gpon = GPON(ont)
                report = gpon.diagnose()
                self.result_ready.emit(report)
                
            # Режим 2: COM автоматизация
            elif self.mode == "com" and COM_AVAILABLE:
                self.log_message.emit("Режим: COM автоматизация")
                bridge = SecureCRTBridge()
                
                if not bridge.connect():
                    self.error_occurred.emit("Не удалось подключиться к SecureCRT")
                    return
                
                # Выполнение команд через bridge
                self.progress_update.emit("Отправка команд...")
                
                # display ont info
                cmd = f"display ont info {ont.frame} {ont.slot} {ont.port} {ont.ont}"
                bridge.send_command(cmd)
                output = bridge.read_until_prompt(timeout=15)
                self.log_message.emit(f"Команда: {cmd}")
                
                bridge.disconnect()
                self.result_ready.emit(output)
                
            # Режим 3: Внутренний (без SecureCRT, только парсинг)
            elif self.mode == "internal":
                self.log_message.emit("Режим: Внутренний (парсинг)")
                self.result_ready.emit("Внутренний режим: используйте SecureCRT для реальных данных")
                
            else:
                raise RuntimeError("Нет доступного режима работы")
                
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            self.error_occurred.emit(f"Ошибка:\n{error_details}")


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self, crt_obj=None):
        super().__init__()
        self.crt = crt_obj  # Глобальный crt из SecureCRT (если внутри)
        self.bridge = None  # COM бридж (если снаружи)
        self.worker = None
        
        self.init_ui()
        self.check_mode()
        
    def check_mode(self):
        """Определение режима работы"""
        if self.crt:
            self.mode = "securecrt"
            self.statusBar().showMessage("Режим: Встроенный Python SecureCRT")
        elif COM_AVAILABLE:
            self.mode = "com"
            self.statusBar().showMessage("Режим: COM автоматизация (требует запущенный SecureCRT)")
        else:
            self.mode = "internal"
            self.statusBar().showMessage("Режим: Внутренний (ограниченный функционал)")
    
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("GPON Huawei Diagnostic Tool")
        self.setGeometry(100, 100, 900, 700)
        
        # Центральное виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # === Группа параметров ONT ===
        ont_group = QGroupBox("Параметры ONT")
        ont_layout = QGridLayout(ont_group)
        ont_layout.setSpacing(8)
        
        # Frame
        ont_layout.addWidget(QLabel("Frame:"), 0, 0)
        self.ont_frame = QSpinBox()
        self.ont_frame.setRange(0, 7)
        self.ont_frame.setValue(0)
        self.ont_frame.setFixedSize(80, 30)
        ont_layout.addWidget(self.ont_frame, 0, 1)
        
        # Slot
        ont_layout.addWidget(QLabel("Slot:"), 0, 2)
        self.ont_slot = QSpinBox()
        self.ont_slot.setRange(0, 7)
        self.ont_slot.setValue(1)
        self.ont_slot.setFixedSize(80, 30)
        ont_layout.addWidget(self.ont_slot, 0, 3)
        
        # Port
        ont_layout.addWidget(QLabel("Port:"), 0, 4)
        self.ont_port = QSpinBox()
        self.ont_port.setRange(0, 31)
        self.ont_port.setValue(0)
        self.ont_port.setFixedSize(80, 30)
        ont_layout.addWidget(self.ont_port, 0, 5)
        
        # ONT ID
        ont_layout.addWidget(QLabel("ONT ID:"), 0, 6)
        self.ont_id = QSpinBox()
        self.ont_id.setRange(0, 127)
        self.ont_id.setValue(1)
        self.ont_id.setFixedSize(80, 30)
        ont_layout.addWidget(self.ont_id, 0, 7)
        
        # SN
        ont_layout.addWidget(QLabel("SN:"), 1, 0, 1, 4)
        self.sn_input = QLineEdit()
        self.sn_input.setPlaceholderText("ALCLXXXXXXXX (опционально)")
        self.sn_input.setMaxLength(12)
        ont_layout.addWidget(self.sn_input, 1, 4, 1, 4)
        
        # === Кнопки ===
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_diagnose = QPushButton("🔍 Диагностика")
        self.btn_diagnose.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.btn_diagnose.clicked.connect(self.start_diagnosis)
        btn_layout.addWidget(self.btn_diagnose)
        
        self.btn_clear = QPushButton("🗑 Очистить")
        self.btn_clear.clicked.connect(self.clear_output)
        btn_layout.addWidget(self.btn_clear)
        
        self.btn_save = QPushButton("💾 Сохранить")
        self.btn_save.clicked.connect(self.save_report)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_copy = QPushButton("📋 Копировать")
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        btn_layout.addWidget(self.btn_copy)
        
        btn_layout.addStretch()
        
        # === Прогресс ===
        progress_layout = QHBoxLayout()
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        progress_layout.addWidget(self.progress)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: gray;")
        progress_layout.addWidget(self.status_label)
        
        # === Вывод ===
        output_group = QGroupBox("Результат")
        output_layout = QVBoxLayout(output_group)
        
        self.output_text = QPlainTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 10))
        self.output_text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3c3c3c;
                padding: 5px;
            }
        """)
        output_layout.addWidget(self.output_text)
        
        # Лог
        log_group = QGroupBox("Журнал")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setMaximumHeight(150)
        self.log_text.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2d2d2d;
                color: #9cdcfe;
                border: 1px solid #3c3c3c;
                padding: 5px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        # Добавляем все в главный layout
        main_layout.addWidget(ont_group)
        main_layout.addLayout(btn_layout)
        main_layout.addLayout(progress_layout)
        main_layout.addWidget(output_group, 2)
        main_layout.addWidget(log_group, 1)
        
        # Меню
        self.create_menu()
        
        # Статус бар
        self.statusBar().showMessage("Готов")
        
    def create_menu(self):
        """Создание меню"""
        menubar = self.menuBar()
        
        # Файл
        file_menu = menubar.addMenu("Файл")
        
        save_action = QAction("Сохранить отчет", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_report)
        file_menu.addAction(save_action)
        
        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Настройки
        settings_menu = menubar.addMenu("Настройки")
        
        com_action = QAction("Проверить COM соединение", self)
        com_action.triggered.connect(self.test_com_connection)
        settings_menu.addAction(com_action)
        
        # Помощь
        help_menu = menubar.addMenu("Помощь")
        
        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def start_diagnosis(self):
        """Запуск диагностики"""
        # Сбор данных
        ont_data = f"{self.ont_frame.value()} {self.ont_slot.value()} {self.ont_port.value()} {self.ont_id.value()}"
        if self.sn_input.text().strip():
            ont_data += f" {self.sn_input.text().strip()}"
        
        # Валидация
        if len(ont_data.split()) < 4:
            QMessageBox.warning(self, "Ошибка", "Укажите Frame, Slot, Port, ONT ID")
            return
        
        # UI обновления
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # Бесконечный прогресс
        self.btn_diagnose.setEnabled(False)
        self.clear_output()
        
        # Создание worker
        self.worker = GPONWorker(ont_data, mode=self.mode)
        
        # Сигналы
        self.worker.result_ready.connect(self.on_diagnosis_complete)
        self.worker.error_occurred.connect(self.on_diagnosis_error)
        self.worker.progress_update.connect(self.on_progress)
        self.worker.log_message.connect(self.on_log)
        
        # Запуск
        self.worker.start()
        self.statusBar().showMessage("Выполняется диагностика...")
        
    def on_progress(self, message):
        """Обновление прогресса"""
        self.status_label.setText(message)
        
    def on_log(self, message):
        """Добавление в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.appendPlainText(f"[{timestamp}] {message}")
        
    def on_diagnosis_complete(self, report):
        """Завершение диагностики"""
        self.output_text.appendPlainText(report)
        
        self.progress.setVisible(False)
        self.btn_diagnose.setEnabled(True)
        self.statusBar().showMessage("Диагностика завершена", 5000)
        self.status_label.setText("")
        
    def on_diagnosis_error(self, error):
        """Ошибка диагностики"""
        self.output_text.appendPlainText(f"[ERROR] {error}")
        
        self.progress.setVisible(False)
        self.btn_diagnose.setEnabled(True)
        self.statusBar().showMessage("Ошибка диагностики", 5000)
        self.status_label.setText("Ошибка")
        
        QMessageBox.critical(self, "Ошибка", f"Диагностика не выполнена:\n{error}")
        
    def clear_output(self):
        """Очистка вывода"""
        self.output_text.clear()
        self.log_text.clear()
        self.status_label.setText("")
        
    def save_report(self):
        """Сохранение отчета"""
        content = self.output_text.toPlainText()
        if not content:
            QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"GPON_report_{timestamp}.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчет",
            default_name,
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.statusBar().showMessage(f"Сохранено: {file_path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{e}")
                
    def copy_to_clipboard(self):
        """Копирование в буфер"""
        content = self.output_text.toPlainText()
        if not content:
            QMessageBox.warning(self, "Ошибка", "Нет данных для копирования")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(content)
        self.statusBar().showMessage("Скопировано в буфер", 2000)
        
    def test_com_connection(self):
        """Тест COM подключения"""
        if not COM_AVAILABLE:
            QMessageBox.warning(self, "Ошибка", "pywin32 не установлен")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Проверка COM соединения")
        dialog.setMinimumSize(500, 300)
        
        layout = QVBoxLayout(dialog)
        
        status_label = QLabel("Проверка...")
        layout.addWidget(status_label)
        
        log_text = QPlainTextEdit()
        log_text.setReadOnly(True)
        layout.addWidget(log_text)
        
        close_btn = QPushButton("Закрыть")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
        
    def show_about(self):
        """О программе"""
        QMessageBox.about(
            self,
            "О программе",
            "<h2>GPON Huawei Diagnostic Tool</h2>"
            "<p>Версия: 1.0</p>"
            "<p>Инструмент для диагностики ONT Huawei MA5600/MA5800</p>"
            "<p>Работает с SecureCRT через COM или встроенный Python</p>"
        )
        
    def closeEvent(self, event):
        """Обработка закрытия"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                "Диагностика выполняется. Закрыть приложение?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        
        event.accept()


# Запуск приложения
def main():
    """Точка входа"""
    app = QApplication(sys.argv)
    app.setApplicationName("GPON Huawei Diagnostic Tool")
    app.setStyle("Fusion")
    
    # Проверка CRT (если запускается внутри SecureCRT)
    crt_obj = None
    if "crt" in globals():
        crt_obj = crt
        print("[OK] SecureCRT объект доступен")
    
    window = MainWindow(crt_obj)
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
