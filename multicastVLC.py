# $language = "Python3"
# $interface = "1.0"

# Для запуска мультикаста в VLC плеере скопируй IP адрес в буфер обмена и нажми кнопку на панели SecureCRT

import pyperclip
import subprocess

crt.Screen.Synchronous = True	

path: str = 'C:\\Program Files\\VideoLAN\\VLC\\vlc.exe'

def main():
	
	multicast_ip = pyperclip.paste().strip()

	# Список аргументов для запуска VLC в свернутом виде и без отображения заголовка видео
	args = [
		"--qt-start-minimized", # Запуск VLC в свернутом виде
		"--no-video-title-show",
		"--repeat",
		f"udp://@{multicast_ip}:1234"
		]
	# Запускаем VLC с передачей аргументов
	process = subprocess.Popen([path] + args)

main()