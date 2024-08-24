import argparse
import os
import shutil
import winreg


def get_file_path(directory: str, name: str) -> str:
    fn: str = ''
    if directory and os.path.isdir(directory) or not directory:
        fn = directory
    else:
        print("Error: directory is not a folder path")
        exit(-1)

    if name:
        if fn:
            fn += '/' + name
        else:
            fn = name
        if os.path.isfile(fn):
            return fn
        else:
            print("Error: file does not exists")
    else:
        print("Error: name was not given")
    exit(-1)


def check_hkey(hkey_lower: str) -> int:
    if hkey_lower in ("hkcr", "classes", "classes_root"):
        return winreg.HKEY_CLASSES_ROOT
    if hkey_lower in ("hkcu", "current_user", "current_usr", "cur_usr", "cur_user"):
        return winreg.HKEY_CURRENT_USER
    if hkey_lower in ("hklm", "local", "local_machine", "lcl_mch"):
        return winreg.HKEY_LOCAL_MACHINE
    if hkey_lower in ("hku", "users"):
        return winreg.HKEY_USERS
    if hkey_lower in ("hkcc", "current_config", "current_cfg", "cur_cfg"):
        return winreg.HKEY_CURRENT_CONFIG
    print(f"Error: unknown hkey {hkey_lower}")
    exit(-1)


def create_file() -> None:
    pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", help="What to do: cf - create_file; rmf - remove file; "
                                       "wf - write file; rf - read file; cpf - copy file; rnf - rename file"
                                       "ck - create key; rmk - remove key; wk - write value to key")
    # Для файлов
    parser.add_argument("--source", '-src', default=None)
    parser.add_argument('--destination', '-dst', default=None)
    parser.add_argument('--directory', '-dir', default=None)
    parser.add_argument('--name', '-n', default=None)
    parser.add_argument('--new_name', '-nn', default=None)
    # для реестра
    parser.add_argument("--hkey", "-hk", default=None)
    parser.add_argument("--folder", "-fl", default=None)
    parser.add_argument("--key_name", "-kn", default=None)
    parser.add_argument("--key_value", "-kv", default=None)
    parser.add_argument("--key_type", "-kt", default=None)

    args = parser.parse_args()

    if args.action == 'cf':
        fn: str = ''
        if args.directory and os.path.isdir(args.directory):
            fn = args.directory + '/'
        elif not args.directory:
            print("Error: directory is not a folder path")
            exit(-1)
        if not args.name:
            print("Error: name was not given")
            exit(-1)
        fn += args.name
        with open(fn, 'w'):
            print(f"File {fn} was created successfully!")

    elif args.action == 'rmf':
        fn: str = get_file_path(args.directory, args.name)
        os.remove(fn)
        print(f"File {fn} was removed successfully!")

    elif args.action == 'wf':
        fn: str = get_file_path(args.directory, args.name)
        with open(fn, 'w') as f:
            n: int = int(input("Count of strings to write: "))
            for _ in range(n):
                write_str = input()
                f.write(write_str + '\n')
        print("File was closed and wrote successfully")

    elif args.action == 'rf':
        fn: str = get_file_path(args.directory, args.name)
        with open(fn, 'r') as f:
            while file_string := f.readline():
                print(file_string, end='')

        print("\nFile was printed successfully")

    elif args.action == 'cpf':
        fn: str = ""
        if args.source and os.path.isfile(args.source):
            fn = args.source
        else:
            print("Error: source is not a file or does not exists")
            return

        if not (args.destination and os.path.isdir(args.destination)):
            print("Error: destination folder does not exists")
            return

        shutil.copy2(fn, args.destination)
        print(f"File {fn} was copied to {args.destination} successfully")

    elif args.action == 'rnf':
        get_file_path(args.directory, args.name)
        fn1 = os.path.join(args.directory, args.name)
        if not args.new_name:
            print("Error: -nn was not given")
            return
        fn2 = os.path.join(args.directory, args.new_name)
        os.rename(fn1, fn2)
        print("File renamed successfully")

    elif args.action == "wk":
        if not all([args.hkey, args.folder, args.key_name, args.key_type, args.key_value]):
            print("Error: optional argument was not given")
            return

        path: int = check_hkey(args.hkey.lower())
        k_type: str = args.key_type.upper()

        folder: winreg.HKEYType = winreg.CreateKeyEx(path, args.folder.split('/')[0])
        for token in args.folder.split('/')[1:]:
            folder = winreg.CreateKeyEx(folder, token)

        try:
            winreg.SetValueEx(folder, args.key_name, 0, eval('winreg.' + k_type), args.key_value)
        except Exception:
            print("Error: wrong k_type or values conflict")
        else:
            print("New value was set successfully")
        finally:
            if folder:
                winreg.CloseKey(folder)

    elif args.action == "rmk":
        if not all([args.hkey, args.folder]):
            print("Error: optional argument was not given")
            return

        path: int = check_hkey(args.hkey.lower())
        folder: winreg.HKEYType = None
        try:
            folder = winreg.OpenKeyEx(path, args.folder.split('/')[0])
            for token in args.folder.split('/')[1:]:
                folder = winreg.OpenKeyEx(folder, token)
            winreg.DeleteKey(folder, "")
        except Exception:
            print("Error: wrong path")
        else:
            print("Key was deleted successfully")
        finally:
            if folder:
                winreg.CloseKey(folder)

    elif args.action == "ck":
        if not all([args.hkey, args.folder]):
            print("Error: optional argument was not given")
            return

        path: int = check_hkey(args.hkey.lower())

        folder: winreg.HKEYType = winreg.CreateKeyEx(path, args.folder.split('/')[0])
        for token in args.folder.split('/')[1:]:
            folder = winreg.CreateKeyEx(folder, token)
        if folder:
            winreg.CloseKey(folder)
        print("New key was created successfully")

    else:
        print("Error: unknown action")


if __name__ == '__main__':
    main()
