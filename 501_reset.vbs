# $language = "VBScript"
# $interface = "1.0"

crt.Screen.Synchronous = True

Sub Main

  crt.Screen.Send "uptime" + chr(13)
  crt.Screen.WaitForString " #"

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
End Sub