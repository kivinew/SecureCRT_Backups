#$language = "VBScript"
#$interface = "1.0"

crt.Screen.Synchronous = True

dim ONT
status = true
dim model
dim huawei
'##########################################'
'1=HG8245 2=HG8245T'
'##########################################'
model = 1

ONT = "0/0/4 2"


sub Main()
	if model = 1 then
		huawei = " hg8245v100r006c00spc212_full_all.bin "
	else
		huawei = " hg8245tv200r006c00spc202_full_all.bin "
	end if

	crt.Screen.Send "ont load " + ONT + huawei + "activemode immediate" & vbcr
	while (status)
		crt.Screen.Send "display ont load state " + ONT & vbcr		
		condition = crt.Screen.WaitForStrings("80%","Fail","Loading")
		Select Case condition
		Case 1
			' Готово'
			status = false
		Case 2
			' Сбой '
			crt.Sleep 500
			status = false
		Case else
			' Ожидание 10сек'
			crt.Sleep 10000
		end Select
	wend
end sub