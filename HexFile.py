import binascii
import os

ROW_SIZE = 16
LEFT_COLUMN_SIZE = 6
DEFAULT_END = 256


class HexFile:
    def __init__(self, name=''):
        self.name = name
        self.hexbytes = self.get_hexbytes() if name else []
        self.changes = []

    def get_hexbytes(self):
        with open(self.name, 'rb') as f:
            hexbytes = f.read().hex()
            return [hexbytes[i:i + 2] for i in range(0, len(hexbytes), 2)]

    def insert(self, command):
        args = command.split()
        is_right_column = args[0] == 'insertf'
        if len(args) > 3:
            raise ValueError('undefined fourth argument')
        elif len(args) == 1:
            raise ValueError('no arguments')
        elif len(args) == 2:
            raise ValueError('no third argument')
        if len(args[2]) % 2 != 0 and not is_right_column:
            raise ValueError('odd count of chars')
        if not is_right_column:
            int(args[2], 16)  # Если есть не hex символы, то бросит ValueError
        if args[1] == 'end':
            insert_index = len(self.hexbytes)
        else:
            insert_index = int(args[1], 16)
        if insert_index > len(self.hexbytes):
            print('Warning: start is more than length of bytes, '
                  'inserted to end')
        if insert_index < 0:
            raise ValueError('start is less than 0')
        if is_right_column:
            new_bytes = list(map(lambda x: hex(ord(x))[2:], list(args[2])))
        else:
            new_bytes = [args[2][i:i + 2] for i in range(0, len(args[2]), 2)]
        for i, j in enumerate(new_bytes):
            self.hexbytes.insert(insert_index + i, j)
        change = (args[0], args[1], args[2])
        self.changes.append(change)

    def get_output_bytes(self, command):
        args = command.split()
        if len(args) > 2:
            raise ValueError('undefined second argument')
        elif len(args) == 1:
            return self._create_output_bytes(0, DEFAULT_END)
        else:
            colon_index = args[1].find(':')
            if colon_index != -1:
                start = args[1][:colon_index]
                start = 0 if start == '' else int(start, 16)
                self._check_index(len(self.hexbytes),
                                  start,
                                  '[start] out of range')
                end = args[1][colon_index + 1:]
                end = len(self.hexbytes) if end == '' else int(end, 16) + 1
                self._check_index(len(self.hexbytes),
                                  end,
                                  '[end] out of range')

                return self._create_output_bytes(start, end)
            else:
                raise ValueError('wrong first argument')

    def _create_output_bytes(self, start=0, end=None):
        if not self.hexbytes:
            return 'empty'
        if start > end - 1:
            raise ValueError('start > end')
        hexbytes = self.hexbytes[start:end]
        result = ' ' * LEFT_COLUMN_SIZE
        result += ''.join([hex(i)[2:].rjust(3, ' ') for i in range(ROW_SIZE)])
        result += '\n'
        x = 1 if start % 16 == 0 else start % 16 + 1
        y = start
        row = ''
        right_column = ''
        for i in hexbytes:
            byte = int(i, 16)
            if 31 < byte < 127:
                right_column += chr(byte)
            else:
                right_column += '.'
            row += i + ' '
            if x % ROW_SIZE == 0:
                field_name = hex(y - start % 16)[2:].rjust(LEFT_COLUMN_SIZE,
                                                           '0')
                if len(row) != 47:
                    row = row.rjust(48, ' ')
                    right_column = right_column.rjust(ROW_SIZE, ' ')
                result += '{} {} {}\n'.format(field_name, row, right_column)
                row = ''
                y += 16
                right_column = ''
            x += 1
        if row:
            field_name = hex(y - start % 16)[2:].rjust(LEFT_COLUMN_SIZE, '0')
            if (end - start) < 16:
                row = row.rjust((start % 16) * 3 + len(row), ' ')
            empty_space = ' ' * (47 - len(row))
            result += '{} {} {} {}\n'.format(field_name,
                                             row,
                                             empty_space,
                                             right_column)
        return result.rstrip()

    def delete_bytes(self, command):
        args = command.split()
        if len(args) > 2:
            raise ValueError('undefined second argument')
        elif len(args) == 1:
            raise ValueError('no arguments')
        colon_index = args[1].find(':')
        if colon_index != -1:
            start = args[1][:colon_index]
            start = 0 if start == '' else int(start, 16)
            end = args[1][colon_index + 1:]
            end = len(self.hexbytes) if end == '' else int(end, 16)
            self._check_index(len(self.hexbytes),
                              start,
                              '[start] out of range')
            self._check_index(len(self.hexbytes), end, '[end] out of range')
            if start > end:
                raise ValueError('start > end')
            change = ('delete',
                      (hex(start)[2:], hex(end)[2:]),
                      ''.join(self.hexbytes[start:end + 1]))
            del self.hexbytes[start:end + 1]
        else:
            del_index = int(args[1])
            self._check_index(len(self.hexbytes),
                              del_index,
                              'index out of range')
            change = ('delete', del_index, self.hexbytes[del_index])
            del self.hexbytes[del_index]
        self.changes.append(change)

    def replace(self, command):
        args = command.split()
        is_right_column = args[0] == 'replacef'
        if len(args) > 3:
            raise ValueError('undefined fourth argument')
        elif len(args) == 2:
            raise ValueError('no third argument')
        elif len(args) == 1:
            raise ValueError('no arguments')
        if len(args[2]) % 2 != 0 and not is_right_column:
            raise ValueError('odd count of chars')
        start = int(args[1], 16)
        if start >= len(self.hexbytes) or start < 0:
            raise ValueError('this byte not found')
        if is_right_column:
            new_bytes = list(map(lambda x: hex(ord(x))[2:], list(args[2])))
            old_bytes = self.hexbytes[start:start + len(new_bytes) * 2]
            old_bytes = ''.join(map(self._format_bytes_to_ascii, old_bytes))
        else:
            new_bytes = [args[2][i:i + 2] for i in range(0, len(args[2]), 2)]
            old_bytes = ''.join(self.hexbytes[start:start + len(new_bytes)])
        change = (args[0],
                  args[1],
                  old_bytes,
                  args[2])
        for i, j in enumerate(range(start, start + len(new_bytes))):
            if j < len(self.hexbytes):
                self.hexbytes[j] = new_bytes[i]
            else:
                self.hexbytes.append(new_bytes[i])
        self.changes.append(change)

    @staticmethod
    def _format_bytes_to_ascii(hexbyte):
        if 31 < int(hexbyte, 16) < 127:
            return chr(int(hexbyte, 16))
        return '.'

    def close(self):
        self._confirmation_to_save('Save changes? (y/n): ')

    def _confirmation_to_save(self, message):
        result = input(message)
        while result != 'y' and result != 'n':
            result = input(message)
        if result == 'y':
            self.save()

    def save(self):
        while self.name == '':
            self.name = input('Empty name of the file. Filename: ')
        with open(self.name, 'wb') as f:
            f.write(binascii.unhexlify(''.join(self.hexbytes)))

    def save_as(self, command):
        args = command.split()
        if len(args) > 3:
            raise ValueError('undefined second argument')
        elif len(args) == 2:
            raise ValueError('no arguments')
        self.name = args[2]
        if os.path.exists(self.name):
            message = 'File exists, rewrite? (y/n): '
            self._confirmation_to_save(message)
        else:
            self.save()

    def create_new_file(self, command):
        args = command.split()
        if len(args) > 2:
            raise ValueError('undefined second argument')
        message = 'Save previous file({})? (y/n): '.format(self.name)
        self._confirmation_to_save(message)
        self.hexbytes = []
        change = ('new', self.name)
        if command == 'new':
            self.name = ''
        else:
            self.name = args[1]
        self.changes.append(change)

    def open(self, command):
        args = command.split()
        if len(args) == 1:
            raise ValueError('no argument')
        elif len(args) > 2:
            raise ValueError('undefined second argument')
        if not os.path.exists(args[1]):
            raise ValueError("file don't exist")
        message = 'Save previous file({})? (y/n): '.format(self.name)
        self._confirmation_to_save(message)
        change = ('open', self.name, args[1])
        self.name = args[1]
        self.hexbytes = self.get_hexbytes()
        self.changes.append(change)

    def get_changes(self):
        result = []
        for i in self.changes:
            if i[0] == 'delete':
                deleted_bytes = self._get_reduced_bytes(i[2])
                change = 'DELETE: start={}, bytes={}\n'.format(i[1],
                                                               deleted_bytes)
            elif i[0].startswith('insert'):
                inserted_bytes = self._get_reduced_bytes(i[2])
                change = '{}: start={}, bytes={}\n'.format(i[0].upper(),
                                                           i[1],
                                                           inserted_bytes)
            elif i[0].startswith('replace'):
                replaced_bytes = self._get_reduced_bytes(i[2])
                new_bytes = self._get_reduced_bytes(i[3])
                change = '{}: start={}, old_bytes={}, ' \
                         'new_bytes={}\n'.format(i[0].upper(),
                                                 i[1],
                                                 replaced_bytes,
                                                 new_bytes)
            elif i[0] == 'open':
                change = 'OPEN: old_file={}, new_file={}\n'.format(i[1],
                                                                   i[2])
            elif i[0] == 'new':
                change = 'NEW_FILE: old_file={}\n'.format(i[1])
            else:
                change = 'Undefined change\n'
            result.append(change)
        if result == []:
            return 'no changes'
        return ''.join(result).rstrip()

    @staticmethod
    def _get_reduced_bytes(hexbytes):
        if len(hexbytes) > 16:
            return '{}[{} chars]{}'.format(hexbytes[:4],
                                           len(hexbytes) - 8,
                                           hexbytes[-4:])
        return hexbytes

    @staticmethod
    def _check_index(length, index, message):
        if index < 0 or index > length:
            raise ValueError(message)

    @staticmethod
    def get_help():
        return "  'new [filename]' - создать новый файл\n" \
               "  'open [filename]' - открыть файл\n" \
               "  'save' - сохранить файл\n" \
               "  'save as [filename]' - сохранить как [filename]\n" \
               "  'print [start]:[end]' - вывести байты с [start] до [end] " \
               "включительно\n      по умолчанию [start] равен 0, " \
               "[end] равен номеру последнего байта\n" \
               "  'print' - вывести первые 256 байт\n" \
               "  'del [start]:[end]' or 'del [index]' - удаляет байт с " \
               "номера [start] до [end] включительно\n" \
               "      или (если нет двоеточия) удаляет байт с " \
               "номером [index]\n" \
               "  'insert [start] [bytes]' - вставить [bytes], начиная с " \
               "номера [start], кол-во байт должно быть четным\n" \
               "  'insertf [start] [chars]' - вставить ascii символы " \
               "[chars], начиная с индекса [start]\n" \
               "      можно в качестве индекса использовать слово 'end' " \
               "для вставки байт в конец файла\n" \
               "  'replace [start] [bytes]' - замена [bytes], начиная с " \
               "номера [start], кол-во байт должно быть четным\n" \
               "  'replacef [start] [bytes]' - замена ascii символов " \
               "[chars], начиная с индекса [start]\n" \
               "  'changes' - показать все изменения за текущую сессию\n" \
               "  'exit' - выход"
