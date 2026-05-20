' $Language="VBScript"
' $Interface="1.0"
' Тест COM-поддержки SecureCRT для интеграции с Qt

Option Explicit

Sub Main()
    Dim fso, outputFile
    Set fso = CreateObject("Scripting.FileSystemObject")
    
    ' Файл результата в той же папке
    outputFile = fso.GetParentFolderName(WScript.ScriptFullName) & "\com_test_result.txt"
    
    Dim report
    report = "SecureCRT COM Проверка" & vbCrLf
    report = report & "====================" & vbCrLf
    report = report & "Дата: " & Now & vbCrLf & vbCrLf
    
    ' 1. Версия SecureCRT
    On Error Resume Next
    report = report & "1. Версия SecureCRT:" & vbCrLf
    report = report & "   Версия: " & crt.Version & vbCrLf
    report = report & "   Build: " & crt.Build & vbCrLf
    report = report & "   License: " & crt.LicenseType & vbCrLf
    If Err.Number <> 0 Then
        report = report & "   [Ошибка получения версии: " & Err.Description & "]" & vbCrLf
        Err.Clear
    End If
    report = report & vbCrLf
    
    ' 2. Информация о сессии
    report = report & "2. Информация о сессии:" & vbCrLf
    report = report & "   Файл сессии: " & crt.Session.Filename & vbCrLf
    report = report & "   Протокол: " & crt.Session.Protocol & vbCrLf
    report = report & "   Хост: " & crt.Session.Host & vbCrLf
    report = report & "   Порт: " & crt.Session.Port & vbCrLf
    report = report & vbCrLf
    
    ' 3. Screen объект
    report = report & "3. Screen объект:" & vbCrLf
    If Not crt.Screen Is Nothing Then
        report = report & "   Статус: доступен" & vbCrLf
        report = report & "   Rows: " & crt.Screen.Rows & vbCrLf
        report = report & "   Columns: " & crt.Screen.Columns & vbCrLf
        report = report & "   Buffer Rows: " & crt.Screen.BufferRows & vbCrLf
        report = report & "   Buffer Columns: " & crt.Screen.BufferColumns & vbCrLf
    Else
        report = report & "   Статус: НЕ доступен" & vbCrLf
    End If
    report = report & vbCrLf
    
    ' 4. Тест отправки команды
    report = report & "4. Тест отправки команды:" & vbCrLf
    On Error Resume Next
    crt.Screen.Send "display version" & chr(13)
    If Err.Number <> 0 Then
        report = report & "   [Ошибка отправки: " & Err.Description & "]" & vbCrLf
        Err.Clear
    Else
        report = report & "   Команда отправлена успешно" & vbCrLf
    End If
    report = report & vbCrLf
    
    ' 5. Тест ожидания
    report = report & "5. Тест WaitForString:" & vbCrLf
    On Error Resume Next
    Dim waitResult
    waitResult = crt.Screen.WaitForString("#", 5)
    If Err.Number <> 0 Then
        report = report & "   [Ошибка WaitForString: " & Err.Description & "]" & vbCrLf
        Err.Clear
    Else
        report = report & "   Результат: " & waitResult & " (1-based индекс)" & vbCrLf
    End If
    report = report & vbCrLf
    
    ' 6. Проверка COM автоматизации (извне)
    report = report & "6. COM автоматизация (SecureCRT.Application):" & vbCrLf
    Dim testCom, comError
    On Error Resume Next
    Set testCom = CreateObject("SecureCRT.Application")
    If Err.Number <> 0 Then
        comError = Err.Description
        report = report & "   Статус: НЕ доступна" & vbCrLf
        report = report & "   Ошибка: " & comError & vbCrLf
        Err.Clear
    Else
        report = report & "   Статус: доступна" & vbCrLf
        report = report & "   Версия через COM: " & testCom.Version & vbCrLf
        report = report & "   Сессий: " & testCom.SessionCount & vbCrLf
        Set testCom = Nothing
    End If
    report = report & vbCrLf
    
    ' 7. Session Collection
    report = report & "7. Доступные сессии:" & vbCrLf
    On Error Resume Next
    Dim sessionCount, i, sessionName
    sessionCount = crt.SessionCount
    report = report & "   Всего сессий: " & sessionCount & vbCrLf
    If sessionCount > 0 Then
        For i = 1 To sessionCount
            On Error Resume Next
            sessionName = crt.Session(i).Name
            If Err.Number = 0 Then
                report = report & "   [" & i & "] " & sessionName & vbCrLf
                Err.Clear
            Else
                report = report & "   [" & i & "] [Недоступно]" & vbCrLf
                Err.Clear
            End If
        Next
    End If
    report = report & vbCrLf
    
    ' 8. Рекомендации для Qt интеграции
    report = report & "8. Рекомендации для Qt интеграции:" & vbCrLf
    report = report & "   " & vbCrLf
    If InStr(comError, "ActiveX") > 0 Or InStr(comError, "class") > 0 Then
        report = report & "   [!] COM НЕ доступен" & vbCrLf
        report = report & "       Используйте вариант: встроенный Python в SecureCRT" & vbCrLf
        report = report & "       Или файловый обмен (commands.txt)" & vbCrLf
    Else
        report = report & "   [+] COM доступен" & vbCrLf
        report = report & "       Используйте вариант: pywin32 автоматизация" & vbCrLf
        report = report & "       Пример: SecureCRTBridge через win32com.client" & vbCrLf
    End If
    report = report & vbCrLf
    
    ' Запись в файл
    Dim stream
    On Error Resume Next
    Set stream = fso.CreateTextFile(outputFile, True)
    If Err.Number <> 0 Then
        MsgBox "Не удалось создать файл: " & outputFile & vbCrLf & _
               "Ошибка: " & Err.Description, vbCritical
        Exit Sub
    End If
    
    stream.Write report
    stream.Close
    
    ' Вывод результата
    MsgBox "Тест завершен!" & vbCrLf & vbCrLf & _
           "Результат сохранен в:" & vbCrLf & _
           outputFile, vbInformation
    
    ' Также выводим в окно сообщения
    Dim msgBoxText
    msgBoxText = "=== Краткий результат ===" & vbCrLf & vbCrLf
    msgBoxText = msgBoxText & "Версия: " & crt.Version & vbCrLf
    msgBoxText = msgBoxText & "COM: " & IIf(InStr(comError, "ActiveX") > 0, "НЕТ", "ДА") & vbCrLf
    msgBoxText = msgBoxText & "Screen: " & IIf(crt.Screen Is Nothing, "НЕТ", "ДА") & vbCrLf
    MsgBox msgBoxText, vbInformation
End Sub

File → Run Script → GPON_HW/test_securecrt_com.vbs