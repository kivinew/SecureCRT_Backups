# $language = "Python3"
# $interface = "1.0"

# Проверка версии python, используемой SecureCRT

import sys
import platform
crt.Dialog.MessageBox(
    "sys.version_info:\r\n{}\r\n\r\nsys.version:\r\n{}\r\n\r\nsys.hexversion:\r\n{}\r\n\r\nplatform.python_version:\r\n{}".format(
        sys.version_info,
        sys.version,
        sys.hexversion,
        platform.python_version()))