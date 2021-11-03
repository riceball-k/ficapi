from __future__ import annotations

import tkinter as tk
import tkinter.filedialog as fd

from requests import Response

from ficapi import FicAPI


def print_response(r: Response) -> None:
    print(f'{"-- url ":-<60}', r.url, sep='\n')
    print(f'{"-- status code ":-<60}', r.status_code, sep='\n')
    print(f'{"-- header ":-<60}', r.headers, sep='\n')
    print(f'{"-- body ":-<60}', r.text, sep='\n')
    print()


def main() -> None:
    fic = FicAPI('./ficapi.ini')
    fic.get_resources()

    tk.Tk().withdraw()
    initialdir: str | None = '.'
    while True:
        filename = fd.askopenfilename(
            initialdir=initialdir,
            filetypes=(('.json', '*.json'), ('すべて', '*.*')),
        )
        if filename:
            print_response(fic.request(filename))
            initialdir = None
        else:
            break


if __name__ == '__main__':
    main()
