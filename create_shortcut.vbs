Set ws = CreateObject("WScript.Shell")
shortcutPath = ws.ExpandEnvironmentStrings("%USERPROFILE%\Desktop\Claude.lnk")
targetPath = ws.ExpandEnvironmentStrings("%APPDATA%\npm\claude.cmd")
Set shortcut = ws.CreateShortcut(shortcutPath)
shortcut.TargetPath = targetPath
shortcut.Save
