# Параметры скрипта
param(
    [string]$HostName = "172.16.50.5",   # Хост для проверки (IP или имя)
    [int]$PingCount = 2,             # Количество пингов за раз
    [int]$SuccessCount = 3,          # Количество успешных пингов для срабатывания оповещения
    [int]$Interval = 1,              # Интервал проверки в секундах
    [int]$BeepFrequency = 1200,      # Частота звука при восстановлении (Гц)
    [int]$BeepFrequency2 = 800,      # Частота звука при недоступности (Гц)
    [int]$BeepDuration = 200         # Длительность звука (мс)
)

Write-Host "Мониторинг доступности хоста: $HostName" -ForegroundColor Green
Write-Host "Интервал: $Interval сек. Оповещение после $SuccessCount успешных пингов. Нажмите Ctrl+C для остановки." -ForegroundColor Yellow

$lastStatus = $null
$successStreak = 0

while ($true) {
    $currentStatus = Test-Connection -ComputerName $HostName -Count $PingCount -Quiet -ErrorAction SilentlyContinue

    # Вывод статуса
    $statusText = if ($currentStatus) { "ДОСТУПЕН" } else { "НЕДОСТУПЕН" }
    $color = if ($currentStatus) { "Green" } else { "Red" }
    Write-Host "$(Get-Date -Format 'HH:mm:ss') - $HostName : $statusText" -ForegroundColor $color

    if ($currentStatus) {
        $successStreak++
        
        # Звуковое оповещение после нескольких успешных пингов
        if ($successStreak -ge $SuccessCount) {
            if ($lastStatus -eq $false -or $lastStatus -eq $null) {
                Write-Host "ЗВУКОВОЕ ОПОВЕЩЕНИЕ: Хост доступен!" -ForegroundColor Yellow
            }
            [Console]::Beep($BeepFrequency, $BeepDuration)
            $lastStatus = $true
            $successStreak = 0  # Сброс счётчика после оповещения
        }
    }
    else {
        $successStreak = 0
        
        # Двойной сигнал при неуспешном пинге (только при первом сбое)
        if ($lastStatus -eq $true -or $lastStatus -eq $null) {
            [Console]::Beep($BeepFrequency2, $BeepDuration)
            Start-Sleep -Milliseconds 150
            [Console]::Beep($BeepFrequency2, $BeepDuration)
        }
        
        $lastStatus = $false
    }

    Start-Sleep -Seconds $Interval
}
