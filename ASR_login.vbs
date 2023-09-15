#$language = "VBScript"
#$interface = "1.0"

crt.Screen.Synchronous = True

Sub Main()
	crt.Screen.WaitForStrings("name: ")
	crt.Screen.Send "admin" + chr(13)

	crt.Screen.WaitForStrings("word: ")
	crt.Screen.Send "xmzpMMe01" + chr(13)

	crt.Screen.WaitForStrings(">")
	crt.Screen.Send "enable" + chr(13)

	crt.Screen.WaitForStrings("word: ")
	crt.Screen.Send "xmzpMMe01" + chr(13)	
	
	crt.Screen.Send "show subscriber session | include "
End Sub