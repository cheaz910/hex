import argparse
import sys
from HexFile import HexFile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', nargs='?', type=str, help='Name of file')
    args = parser.parse_args()
    if args.filename:
        try:
            file = HexFile(args.filename)
        except FileNotFoundError:
            print('Error: file not found')
            sys.exit(1)
    else:
        file = HexFile()
    interactive_mode(file)


def interactive_mode(file):
    command = input('{}>'.format(file.name))
    while True:
        try:
            if command == 'help':
                print(file.get_help())
            elif command == 'exit':
                file.close()
                break
            elif command == 'save':
                file.save()
            elif command == 'changes':
                print(file.get_changes())
            elif command.startswith('print'):
                print(file.get_output_bytes(command))
            elif command.startswith('replace'):
                file.replace(command)
            elif command.startswith('open'):
                file.open(command)
            elif command.startswith('insert'):
                file.insert(command)
            elif command.startswith('del'):
                file.delete_bytes(command)
            elif command.startswith('new'):
                file.create_new_file(command)
            elif command.startswith('save as'):
                file.save_as(command)
        except ValueError as e:
            print('Error: {}'.format(e))
        command = input('{}>'.format(file.name))


if __name__ == '__main__':
    main()
