# $language = "VBScript"
# $interface = "1.0"

crt.Screen.Synchronous = True

Sub Main
  strSelection = Trim(crt.Screen.Selection)
  crt.Screen.Send "pm clear --user 0 " & strSelection & chr(13)
End Sub