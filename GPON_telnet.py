# $language = "Python3"
# $interface = "1.0"

import pyperclip
# import SU_challenge

# crt.Screen.Synchronous = True	

def main() -> None:
    memBuffer = pyperclip.paste()
    ONT = memBuffer.replace('/', ' ').split()
    frame: str    = ONT[0]
    slot: str     = ONT[1]
    port: str     = ONT[2]
    ont_id: str   = ONT[3]
    crt.Screen.Send(f"diagnose\rtelnet {frame}/{slot}/{port} {ont_id}\r\r")
    crt.Screen.WaitForString("Login:")
    crt.Screen.Send("root\r")
    crt.Screen.WaitForString("Password:")
    crt.Screen.Send("GhjuhtcC\r")
    crt.Screen.WaitForString("WAP>")
    crt.Screen.Send("su\r")
    # if (crt.Screen.WaitForString("password:", 1)):
    #     try:
    #         challenge = "BK7BK5TO"
    #         SU_challenge.suPassword(challenge=challenge)
    #     except Exception as e:
    #         crt.Dialog.MessageBox(f"ERROR! {e}\n Copy a challenge and use a SU_challenge button.")
           
main()