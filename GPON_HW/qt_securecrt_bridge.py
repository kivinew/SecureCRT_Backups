"""
SecureCRT Bridge для Qt приложения

Это МОДУЛЬ для использования в отдельном Qt приложении.
Требует pywin32: pip install pywin32

Использование:
    from qt_securecrt_bridge import SecureCRTBridge
    
    bridge = SecureCRTBridge()
    if bridge.connect():
        bridge.send_command("display ont info 0 1 0 1")
        output = bridge.read_output(10)
        print(output)
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

try:
    import win32com.client  # type: ignore
    import pythoncom  # type: ignore
    WIN32_AVAILABLE: bool = True
except ImportError:
    WIN32_AVAILABLE = False
    print("WARNING: pywin32 не установлен. Установите через: pip install pywin32")


class SecureCRTBridge:
    """Бридж для взаимодействия с SecureCRT через COM"""
    
    def __init__(self) -> None:
        self.securecrt: Any = None
        self.active_session: Any = None
        self._last_output: str = ""
        
    def connect(self, create_new: bool = False) -> bool:
        """
        Подключение к SecureCRT
        
        Args:
            create_new: Если True, запускает новый экземпляр SecureCRT
                       Если False, пытается подключиться к существующему
        
        Returns:
            bool: True если подключение успешно
        """
        if not WIN32_AVAILABLE:
            print("ERROR: pywin32 не установлен")
            return False
        
        try:
            if create_new:
                # Запуск нового экземпляра
                self.securecrt = win32com.client.Dispatch("SecureCRT.Application")
                print("[OK] Запущен новый экземпляр SecureCRT")
            else:
                # Подключение к существующему
                try:
                    self.securecrt = win32com.client.GetActiveObject("SecureCRT.Application")
                    print("[OK] Подключен к существующему SecureCRT")
                except:
                    # Если не удалось, запускаем новый
                    self.securecrt = win32com.client.Dispatch("SecureCRT.Application")
                    print("[OK] Запущен новый экземпляр SecureCRT")
            
            # Проверка подключения
            if self.securecrt is not None:
                print(f"[OK] Версия SecureCRT: {self.securecrt.Version}")
                return True
            else:
                print("[ERROR] SecureCRT объект не создан")
                return False
                
        except Exception as e:
            print(f"[ERROR] Ошибка подключения: {e}")
            return False
    
    def disconnect(self) -> None:
        """Отключение от SecureCRT"""
        self.active_session = None
        self.securecrt = None
        print("[INFO] Отключено от SecureCRT")
    
    def get_session(self, session_name: Optional[str] = None) -> Any:
        """
        Получение объекта сессии
        
        Args:
            session_name: Имя сессии (опционально). 
                         Если None, возвращается активная сессия
        
        Returns:
            Session object или None
        """
        if self.securecrt is None:
            print("[ERROR] Нет подключения к SecureCRT")
            return None
        
        try:
            if session_name:
                # Поиск по имени
                for i in range(1, self.securecrt.SessionCount + 1):
                    session = self.securecrt.Session(i)
                    if session.Name == session_name:
                        self.active_session = session
                        return session
                
                print(f"[ERROR] Сессия '{session_name}' не найдена")
                return None
            else:
                # Активная сессия
                self.active_session = self.securecrt.GetActiveSession()
                return self.active_session
                
        except Exception as e:
            print(f"[ERROR] Ошибка получения сессии: {e}")
            return None
    
    def switch_to_session(self, session_name: str) -> bool:
        """
        Переключение на указанную сессию
        
        Args:
            session_name: Имя сессии
        
        Returns:
            bool: True если успешно
        """
        session = self.get_session(session_name)
        if session:
            try:
                session.Activate()
                print(f"[OK] Переключено на сессию: {session_name}")
                return True
            except Exception as e:
                print(f"[ERROR] Ошибка активации сессии: {e}")
                return False
        return False
    
    def send_command(self, command: str, session_name: Optional[str] = None) -> bool:
        """
        Отправка команды в терминал
        
        Args:
            command: Команда для отправки
            session_name: Имя сессии (опционально)
        
        Returns:
            bool: True если успешно
        """
        session = self.get_session(session_name) if session_name else self.active_session
        
        if session is None:
            print("[ERROR] Сессия не выбрана")
            return False
        
        try:
            session.Screen.Send(command + "\r")
            return True
        except Exception as e:
            print(f"[ERROR] Ошибка отправки команды: {e}")
            return False
    
    def read_output(self, timeout: int = 10, session_name: Optional[str] = None) -> str:
        """
        Чтение вывода терминала до промпта
        
        Args:
            timeout: Таймаут ожидания (сек)
            session_name: Имя сессии (опционально)
        
        Returns:
            str: Вывод терминала
        """
        session = self.get_session(session_name) if session_name else self.active_session
        
        if session is None:
            print("[ERROR] Сессия не выбрана")
            return ""
        
        try:
            output = session.Screen.ReadString(["#", "$", "Press 'Q'"], timeout)
            self._last_output = output
            return output
        except Exception as e:
            print(f"[ERROR] Ошибка чтения вывода: {e}")
            return ""
    
    def wait_for_string(self, patterns: Any, timeout: int = 10, session_name: Optional[str] = None) -> int:
        """
        Ожидание одного из паттернов в выводе
        
        Args:
            patterns: Список паттернов для ожидания (list of str)
                     Или один паттерн (str)
            timeout: Таймаут ожидания (сек)
            session_name: Имя сессии (опционально)
        
        Returns:
            int: 1-based индекс совпавшего паттерна, или 0 если таймаут
        """
        session = self.get_session(session_name) if session_name else self.active_session
        
        if session is None:
            print("[ERROR] Сессия не выбрана")
            return 0
        
        try:
            # Приводим к списку если передана строка
            if isinstance(patterns, str):
                patterns = [patterns]
            
            index = session.Screen.WaitForString(patterns, timeout)
            return index
        except Exception as e:
            print(f"[ERROR] Ошибка ожидания: {e}")
            return 0
    
    def read_until_prompt(self, prompt: str = "#", timeout: int = 10, delay: float = 0.5) -> str:
        """
        Чтение всего вывода до промпта (с пагинацией)
        
        Args:
            prompt: Промпт ожидания
            timeout: Таймаут между чтениями
            delay: Задержка перед первым чтением
        
        Returns:
            str: Полный вывод
        """
        time.sleep(delay)  # Даем время на вывод
        
        output = ""
        start_time = time.time()
        
        while True:
            remaining = timeout - (time.time() - start_time)
            if remaining <= 0:
                print("[WARN] Таймаут при чтении вывода")
                break
            
            chunk = self.read_output(remaining)
            if not chunk:
                break
            
            output += chunk
            
            # Если появился промпт, выходим
            if prompt in chunk:
                break
            
            # Если есть "Press 'Q'", отправляем q
            if "Press 'Q'" in chunk:
                self.send_command("q")
        
        return output
    
    def execute_command(self, command: str, timeout: int = 10) -> str:
        """
        Выполнение команды и получение полного вывода
        
        Args:
            command: Команда для выполнения
            timeout: Таймаут ожидания вывода
        
        Returns:
            str: Вывод команды
        """
        self.send_command(command)
        return self.read_until_prompt(timeout=timeout)
    
    def get_session_list(self) -> List[str]:
        """
        Получение списка всех сессий
        
        Returns:
            list: Список имен сессий
        """
        if self.securecrt is None:
            return []
        
        sessions: List[str] = []
        try:
            for i in range(1, self.securecrt.SessionCount + 1):
                session = self.securecrt.Session(i)
                sessions.append(session.Name)
        except Exception as e:
            print(f"[ERROR] Ошибка получения списка сессий: {e}")
        
        return sessions
    
    def is_connected(self) -> bool:
        """Проверка наличия подключения"""
        return self.securecrt is not None


# Пример использования
if __name__ == "__main__":
    print("SecureCRT Bridge Test")
    print("=" * 50)
    
    bridge = SecureCRTBridge()
    
    # Подключение
    if not bridge.connect():
        print("Не удалось подключиться к SecureCRT")
        sys.exit(1)
    
    # Список сессий
    print("\nДоступные сессии:")
    for session in bridge.get_session_list():
        print(f"  - {session}")
    
    # Выполнение команды
    print("\nВыполнение команды: display version")
    output = bridge.execute_command("display version", timeout=10)
    print(f"\nВывод ({len(output)} символов):")
    print(output[:500] + "..." if len(output) > 500 else output)
    
    # Отключение
    bridge.disconnect()
