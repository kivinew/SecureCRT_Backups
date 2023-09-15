#$language = "VBScript"
#$interface = "1.0"

crt.Screen.Synchronous = True

Sub Main()
	crt.Screen.WaitForStrings(">")
	crt.Screen.Send " show arp no-resolve | match "
End Sub