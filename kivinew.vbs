# $language = "VBScript"
# $interface = "1.0"

' Connect to a telnet server and automate the initial login sequence.
' Note that synchronous mode is enabled to prevent server output from
' potentially being missed.

Sub Main

  crt.Screen.Synchronous = True

  crt.Screen.Send "kudryavcev.iv" & vbCr

  crt.Screen.Send "Date1001" & vbCr

  crt.Screen.Send "enable" & vbCr

  crt.Screen.Send "config" & vbCr

  crt.Screen.Synchronous = False

End Sub