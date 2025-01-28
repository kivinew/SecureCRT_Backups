# $language = "VBScript"
# $interface = "1.0"

crt.Screen.Synchronous = True

Sub Main

  crt.Screen.Send "am broadcast -a android.intent.action.MASTER_CLEAR" + chr(13)
  crt.Screen.WaitForString " #", 10

  Dim output
  output = crt.Screen.Get(1, 1, crt.Screen.Rows, crt.Screen.Columns)

  If InStr(output, "Aborted") Then
    crt.Screen.Send "su" + chr(13)
    crt.Screen.WaitForString " #"

    crt.Screen.Send "rm -rf /system/data/*" + chr(13)
    crt.Screen.WaitForString " #"

    crt.Screen.Send "rm -rf /system/tmp/*" + chr(13)
    crt.Screen.WaitForString " #"

    crt.Screen.Send "rm -rf /data/*" + chr(13)
    crt.Screen.WaitForString " #"

    crt.Screen.Send "rm -rf /tmp/*" + chr(13)
    crt.Screen.WaitForString " #"

    crt.Screen.Send "sync" + chr(13)
    crt.Screen.WaitForString " #"

    crt.Screen.Send "exit" + chr(13)
  End If

End Sub