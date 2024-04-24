# $language = "VBScript"
# $interface = "1.0"

crt.Screen.Synchronous = True

Sub Main
  strSelection = Trim(crt.Screen.Selection)
  crt.Screen.Send "su" & chr(13)
  crt.Screen.WaitForString " #"
  crt.Screen.Send "pm uninstall " & strSelection & chr(13)
  crt.Screen.WaitForString " #"
  crt.Screen.Send "exit" & chr(13)
End Sub