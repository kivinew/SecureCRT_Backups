#$language = "VBScript"
#$interface = "1.0"


Sub Main
 ' Extract SecureCRT's version components to determine how to go about
 ' getting the current selection (version 6.1 provides a scripting API
 ' for accessing the screen's selection, but earlier versions do not)
 strVersionPart = Split(crt.Version, " ")(0)
 vVersionElements = Split(strVersionPart, ".")
 nMajor = vVersionElements(0)
 nMinor = vVersionElements(1)
 nMaintenance = vVersionElements(2)

 If nMajor >= 6 And nMinor > 0 Then
 ' Use available API to get the selected text:
 strSelection = Trim(crt.Screen.Selection)
 Else
 MsgBox "The Screen.Selection object is available" & vbcrlf & _
 "in SecureCRT version 6.1 and later." & vbcrlf & _
 vbcrlf & _
 "Exiting script."
 Exit Sub
 End If

 ' Now search on Google for the information.
 g_strSearchBase = "https://www.deepl.com/translator#en/ru/"

 Set g_shell = CreateObject("WScript.Shell")

 ' Instead of launching Internet Explorer, we'll run the URL, so that the
 ' default browser gets used :).
 If strSelection = "" Then
 g_shell.Run chr(34) & "https://www.deepl.com/translator#en/ru/" & chr(34)
 Else
 g_shell.Run chr(34) & g_strSearchBase & strSelection & chr(34)
 End If
End Sub
