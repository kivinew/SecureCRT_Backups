#$language = "VBScript"
#$interface = "1.0"

crt.Screen.Synchronous = True

' This automatically generated script may need to be
' edited in order to work correctly.

Sub Main
	crt.Screen.Send "config" & chr(13)
	crt.Screen.Send "aaa authentication login radius local" & chr(13)
	crt.Screen.Send "aaa authentication enable radius enable" & chr(13)
	crt.Screen.Send "aaa accounting system radius" & chr(13)
	crt.Screen.Send "aaa accounting exec start-stop radius" & chr(13)
	crt.Screen.Send "aaa accounting dot1x start-stop radius" & chr(13)
	crt.Screen.Send "radius-server timeout 5" & chr(13)
	crt.Screen.Send "radius-server mode index-priority" & chr(13)
	crt.Screen.Send "radius-server host 1 10.2.1.1 auth-port 1812 key cl-182v1" & chr(13)
	crt.Screen.Send "radius-accounting timeout 5" & chr(13)
	crt.Screen.Send "radius-accounting host 1 10.2.1.1 acct-port 1813 key cl-182v1" & chr(13)
	crt.Screen.Send "exit" & chr(13)
	crt.Screen.Send "wri mem" & chr(13)
End Sub
