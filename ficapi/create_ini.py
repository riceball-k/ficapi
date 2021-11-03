import configparser
import sys
from pathlib import Path

from ficapi.mycipher import MyCipher, input_password


def ask_yesno(text: str) -> bool:
    print()
    while True:
        yesno = input(f'  {text} (y/n): ').strip().lower()
        if yesno == 'y':
            return True
        elif yesno == 'n':
            return False
        print("% Please answer 'y' or 'n'.")


def inputstr(prompt: str, default: str = None) -> str:
    prompt = f'{prompt} [{default}]: ' if default else f'{prompt}: '
    for _ in range(3):
        result = input(prompt)
        if result.strip() == '' and default is not None:
            print('% The default value has been selected.')
            return default
        if result:
            return result
    else:
        print('\nAbort!\n')
        sys.exit(0)


def main() -> None:
    try:
        print("""
Use ctrl-c to abort this program.
Default settings are in square brackets '[]'.
"""
              )
        api_endpoint = inputstr(f'api_endpoint', default='https://api.ntt.com')
        api_key = inputstr('api_key')
        api_secret = inputstr('api_secret')
        tenant_id = inputstr('tenant_id')

        FILENAME = './ficapi.ini'
        if ask_yesno(f'Create a "{FILENAME}" file?') is False:
            sys.exit(0)

        file = Path(FILENAME)
        if file.exists():
            if ask_yesno(f'File "{FILENAME}" exists. overwrite it?') is False:
                sys.exit(0)
            # if ask_yesno('Are you sure?') is False:
            #     sys.exit(0)

        password = input_password()
        if password is None:
            print('\nError! password unmatched.')
            sys.exit(0)

        cipher = MyCipher(password)
        config = configparser.ConfigParser()
        config['DEFAULT'] = {
            'api_endpoint': api_endpoint
        }
        config['auth'] = {
            'api_key': cipher.encrypt(api_key),
            'api_secret': cipher.encrypt(api_secret),
        }
        config['tenant'] = {
            'tenant_id': tenant_id,
            'tenantId': '{tenant_id}',
        }
        with file.open('wt') as f:
            config.write(f)

        print("\nFinish!\n")
        print("-- Don't forget your password. --\n")

    except KeyboardInterrupt:
        print('\n\nAbort!\n')
        sys.exit(0)


if __name__ == '__main__':
    main()
