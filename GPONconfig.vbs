#$language = "VBScript"
#$interface = "1.0"

crt.Screen.Synchronous = True
'########################################################################################################'
' HS8545M5_WAN - 80 порт
' WanAccess - порт 88
' WanAccess_HG8245 - порт 80
' WanAccess | WanAccess_HG8245 | ALL_for_HS8545M5 | ALL_for_HG8245H | IP | all_dlya_abonov
'########################################################################################################'
' переменные ont
dim slot
dim port
dim ont
' номер лицевого счёта для дескрипшена
dim description
' файл конфигурации
dim conf
' опрос вывода в цикле while/wend
dim condition
' состояние заливки конфига в цикле while/wend
status=true

'########################################################################################################'
' Указать slot, port, ont и имя файла для заливки'
' frame = 0 всегда'
slot        = "10"
port        = "0"
ont         = "6"
conf        = ""
description = ""
'########################################################################################################'

Sub Main()
	crt.Screen.Send "display ont version 0 " + slot + " " + port + " " + ont & vbcr
	crt.Screen.Send "diagnose" & vbcr
	crt.Screen.Send "ont-load info configuration " + conf + ".xml ftp 10.2.1.3 huawei ksa5oz6y" & vbcr
	crt.Screen.Send "ont-load select 0/" + slot + " " + port + " " + ont & vbcr
	crt.Screen.Send "ont-load start" & vbcr & vbcr	
	while (status)
		crt.Screen.Send "display ont-load select 0/" + slot + " " + port + " " + ont & vbcr		
		condition = crt.Screen.WaitForStrings("Success","Fail","Loading")
		Select Case condition
			Case 1
				' Конфига залита - выход из цикла опроса'
				status=false
			Case 2
				' Сбой конфигурации - выход из цикла опроса
				status=false
				crt.Dialog.MessageBox("Сбой конфигурации")
			Case Else
				' Пауза 2 сек'
				crt.Sleep 2000
			End Select
	wend 
' Завершение конфигурации в режиме diagnoseS'
	crt.Screen.Send "ont-load stop" & vbcr
	crt.Screen.Send	"config" & vbcr

' Если конфига с пропиской IP то вывести настройки WAN интерфейса'    
	if conf = "all" or conf = "IP" or conf = "inet_tv_wifi_vlan2" then
		crt.Screen.Send "display ont wan-info 0/" + slot + " " + port + " " + ont & vbcr
		crt.Screen.Send " " & vbcr
	end if
	crt.Screen.Send "interface gpon 0/" + slot & vbcr
	if description <> "" then
		crt.Screen.Send "ont modify " + port + " " + ont + " desc " + description & vbcr
	end if
	crt.Screen.Send "ont remote-ping " + port + " " + ont + " ip-address 8.8.8.8" & vbcr
	crt.Screen.Send "quit" & vbcr
End Sub