Set ws = CreateObject("WScript.Shell")
shortcutPath = ws.ExpandEnvironmentStrings("%USERPROFILE%\Desktop\Claude Desktop.lnk")
targetPath = ws.ExpandEnvironmentStrings("%LOCALAPPDATA%\Claude-3p\claude-code\2.1.165\claude.exe")
Set shortcut = ws.CreateShortcut(shortcutPath)
shortcut.TargetPath = targetPath
shortcut.WorkingDirectory = ws.ExpandEnvironmentStrings("%LOCALAPPDATA%\Claude-3p\claude-code\2.1.165")
shortcut.Save
