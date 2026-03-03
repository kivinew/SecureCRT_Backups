# Параметры скрипта
param(
    [string]$HostName = "8.8.8.0",  # Хост для проверки (IP или имя)
    [int]$PingCount = 2,             # Количество пингов за раз
    [int]$Interval = 1,              # Интервал проверки в секундах
    [int]$BeepFrequency = 1200,      # Частота звука (Гц)
    [int]$BeepFrequency2 = 800,      # Частота звука (Гц)
    [int]$BeepDuration = 200         # Длительность звука (мс)
)

Write-Host "Мониторинг доступности хоста: $HostName" -ForegroundColor Green
Write-Host "Интервал: $Interval сек. Нажмите Ctrl+C для остановки." -ForegroundColor Yellow

$lastStatus = $null

while ($true) {
    $currentStatus = Test-Connection -ComputerName $HostName -Count $PingCount -Quiet -ErrorAction SilentlyContinue
    
    # Вывод статуса
    $statusText = if ($currentStatus) { "ДОСТУПЕН" } else { "НЕДОСТУПЕН" }
    $color = if ($currentStatus) { "Green" } else { "Red" }
    Write-Host "$(Get-Date -Format 'HH:mm:ss') - $HostName : $statusText" -ForegroundColor $color
    
    # Звуковое оповещение только при изменении статуса на "доступен"
    if ($currentStatus -and $lastStatus -eq $false) {
        [Console]::Beep($BeepFrequency, $BeepDuration)
        Write-Host "ЗВУКОВОЕ ОПОВЕЩЕНИЕ: Хост восстановил доступность!" -ForegroundColor Yellow
    }
    else
    	[Console]::Beep($BeepFrequency2, #BeepDuration)
    
    $lastStatus = $currentStatus
    Start-Sleep -Seconds $Interval
}
