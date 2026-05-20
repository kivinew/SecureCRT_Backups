# $language = "Python3"
# $interface = "1.0"

import os
import sys
import pyperclip
import importlib

script_dir = os.path.dirname(
    os.path.abspath(__file__)
)

sys.path.insert(
    0,
    script_dir
)

import GPON_class

importlib.reload(
    GPON_class
)

from GPON_class import (
    Ont,
    GPON,
    inject_crt
)

inject_crt(
    crt
)


def main():

    buffer = (
        pyperclip
        .paste()
        .strip()
    )

    if "/" in buffer:

        ont = Ont()

    else:

        gpon = GPON()

        ont = (
            gpon
            .find_by_serial(
                buffer
            )
        )

        if not ont:

            ont = (
                gpon
                .find_by_description(
                    buffer
                )
            )

    if not ont:

        crt.Dialog.MessageBox(
            "ONT не найдена"
        )

        return

    diag = GPON(
        ont
    )

    result = (
        diag
        .diagnose()
    )

    pyperclip.copy(
        result
    )


main()
