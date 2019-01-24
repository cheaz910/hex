import unittest
import os
import sys
from io import StringIO
from unittest.mock import patch
from HexFile import HexFile
import cmain


class HexFileTest(unittest.TestCase):
    def test_get_hexbytes(self):
        hexbytes = ''.join(HexFile('files_for_test/test_file.txt').hexbytes)
        self.assertTrue(hexbytes.startswith('6162636465666768696a6b'))
        self.assertTrue(hexbytes.endswith('696a6b6c'))
        self.assertEqual(144, len(hexbytes))

    def test_insert_errors(self):
        file = HexFile('files_for_test/test_file.txt')
        with self.assertRaises(ValueError):
            file.insert('insert a b c')
        with self.assertRaises(ValueError):
            file.insert('insert ')
        with self.assertRaises(ValueError):
            file.insert('insert a')
        with self.assertRaises(ValueError):
            file.insert('insert a bcd')
        with self.assertRaises(ValueError):
            file.insert('insert a uouo')
        with self.assertRaises(ValueError):
            file.insert('insert -1 bcdf')

    def test_insert_right_column(self):
        file = HexFile('files_for_test/test_file.txt')
        old_length = len(file.hexbytes)
        file.insert('insertf 1 ILNUR')
        expected_first_bytes = '61494c4e555262636465666768696a6b'
        actual_bytes = ''.join(file.hexbytes)
        self.assertTrue(actual_bytes.startswith(expected_first_bytes))
        self.assertEqual(old_length + 5, len(file.hexbytes))

    def test_insert_end(self):
        file = HexFile('files_for_test/test_file.txt')
        last_byte = file.hexbytes[-1]
        file.insert('insert end aabb')
        self.assertEqual(last_byte, file.hexbytes[-3])
        self.assertEqual('aa', file.hexbytes[-2])
        self.assertEqual('bb', file.hexbytes[-1])

    def test_insert_index_greater_than_length(self):
        file = HexFile('files_for_test/test_file.txt')
        last_byte = file.hexbytes[-1]
        sys.stdout = StringIO()
        file.insert('insert ffffff aabb')
        self.assertEqual(last_byte, file.hexbytes[-3])
        self.assertEqual('aa', file.hexbytes[-2])
        self.assertEqual('bb', file.hexbytes[-1])

    def test_insert(self):
        file = HexFile('files_for_test/test_file.txt')
        first_byte = file.hexbytes[0]
        length = len(file.hexbytes)
        file.insert('insert 1 aabb')
        self.assertEqual(first_byte, file.hexbytes[0])
        self.assertEqual('aa', file.hexbytes[1])
        self.assertEqual('bb', file.hexbytes[2])
        self.assertEqual(length + 2, len(file.hexbytes))

    def test_get_output_bytes(self):
        file = HexFile()
        file.hexbytes = ['11', '99', 'bb', '00', 'dd', '34', 'da', 'fe']
        expected_result = '        0  1  2  3  4  5  6  7  8  9  a  b  c  d' \
                          '  e  f\n000000    99 bb 00 dd 34 da' \
                          '                             ....4.'
        actual_result = file.get_output_bytes('print 1:6')
        self.assertEqual(expected_result, actual_result)
        expected_result = '        0  1  2  3  4  5  6  7  8  9  a  b  c  d' \
                          '  e  f\n000000 11 99 bb 00 dd 34 da fe' \
                          '                          .....4..'
        actual_result = file.get_output_bytes('print')
        self.assertEqual(expected_result, actual_result)
        actual_result = file.get_output_bytes('print :')
        self.assertEqual(expected_result, actual_result)
        file.hexbytes = []
        self.assertEqual('empty', file.get_output_bytes('print'))
        file = HexFile('files_for_test/test_file.txt')
        expected_result = '        0  1  2  3  4  5  6  7  8  9  a  b  c  d' \
                          '  e  f\n000000 61 62 63 64 65 66 67 68 69 6a 6b 6' \
                          'c 61 62 63 64  abcdefghijklabcd\n000010 65 66 67 ' \
                          '68 69 6a 6b 6c 61 62 63 64 65 66 67 68  efghijkla' \
                          'bcdefgh'
        actual_result = file.get_output_bytes('print :1f')
        print(actual_result)
        self.assertEqual(expected_result, actual_result)

    def test_get_output_bytes_errors(self):
        file = HexFile()
        file.hexbytes = ['11', '99', 'bb', '00', 'dd', '34', 'da', 'fe']
        with self.assertRaises(ValueError):
            file.get_output_bytes('print 1:6 f')
        with self.assertRaises(ValueError):
            file.get_output_bytes('print 1d')
        with self.assertRaises(ValueError):
            file.get_output_bytes('print 5:4')

    def test_delete_bytes_error(self):
        file = HexFile()
        file.hexbytes = ['11', '22']
        with self.assertRaises(ValueError):
            file.delete_bytes('delete')
        with self.assertRaises(ValueError):
            file.delete_bytes('delete a b')
        with self.assertRaises(ValueError):
            file.delete_bytes('delete -1:')
        with self.assertRaises(ValueError):
            file.delete_bytes('delete 0:999')
        with self.assertRaises(ValueError):
            file.delete_bytes('delete 1:0')
        with self.assertRaises(ValueError):
            file.delete_bytes('delete 1000')

    def test_delete_bytes(self):
        file = HexFile()
        file.hexbytes = ['11', '22', '33', '44', '55', '66']
        file.delete_bytes('delete 1')
        expected_result = ['11', '33', '44', '55', '66']
        self.assertEqual(expected_result, file.hexbytes)
        file.delete_bytes('delete 1:3')
        self.assertEqual(['11', '66'], file.hexbytes)

    def test_replace_errors(self):
        file = HexFile()
        file.hexbytes = ['11', '22', '33', '44']
        with self.assertRaises(ValueError):
            file.replace('replace 1 2 3')
        with self.assertRaises(ValueError):
            file.replace('replace 1')
        with self.assertRaises(ValueError):
            file.replace('replace')
        with self.assertRaises(ValueError):
            file.replace('replace 1 abc')
        with self.assertRaises(ValueError):
            file.replace('replace 1000 ab')

    def test_replace_right_column(self):
        file = HexFile('files_for_test/test_file.txt')
        old_length = len(file.hexbytes)
        file.replace('replacef 1 ILNUR')
        expected_first_bytes = '61494c4e55526768696a6b'
        actual_bytes = ''.join(file.hexbytes)
        self.assertTrue(actual_bytes.startswith(expected_first_bytes))
        self.assertEqual(old_length, len(file.hexbytes))

    def test_replace(self):
        file = HexFile()
        file.hexbytes = ['11', '22', 'aa', '44', '55']
        file.replace('replace 3 bbccdd')
        expected_result = ['11', '22', 'aa', 'bb', 'cc', 'dd']
        self.assertEqual(expected_result, file.hexbytes)

    def test_close(self):
        user_input = ['t', 't', 'y']
        filename = 'files_for_test/test_save.txt'
        file = HexFile(filename)
        file.hexbytes = ['50', '51', '52', '53']
        with patch('builtins.input', side_effect=user_input):
            file.close()
        expected_result = ['50', '51', '52', '53']
        self.assertEqual(file.get_hexbytes(), expected_result)

    def test_save_empty_name(self):
        user_input = ['', '', 'files_for_test/test_save_empty.txt']
        file = HexFile()
        file.hexbytes = ['50', '51', '52', '53']
        with patch('builtins.input', side_effect=user_input):
            file.save()
        expected_result = ['50', '51', '52', '53']
        self.assertEqual(file.get_hexbytes(), expected_result)

    def test_save_as_errors(self):
        file = HexFile()
        with self.assertRaises(ValueError):
            file.save_as('save as test_save_as.txt undefined')
        with self.assertRaises(ValueError):
            file.save_as('save as')

    def test_save_as(self):
        file = HexFile()
        filename = 'files_for_test/test_save_as_temp.txt'
        file.hexbytes = ['50', '51', '52', '53']
        file.save_as('save as {}'.format(filename))
        self.assertEqual(file.get_hexbytes(), ['50', '51', '52', '53'])
        os.remove(filename)

    def test_save_as_exist(self):
        user_input = ['', '', 'y']
        file = HexFile()
        file.hexbytes = ['50', '51', '52', '53']
        with patch('builtins.input', side_effect=user_input):
            file.save_as('save as files_for_test/test_save_as_exist.txt')
        expected_result = ['50', '51', '52', '53']
        self.assertEqual(file.get_hexbytes(), expected_result)

    def test_create_new_file(self):
        file = HexFile('files_for_test/test_save.txt')
        user_input = ['', '', 'y']
        with patch('builtins.input', side_effect=user_input):
            file.create_new_file('new files_for_test/test_new.txt')
        file.save()
        self.assertEqual(file.get_hexbytes(), [])

    def test_create_new_file_no_name(self):
        file = HexFile('files_for_test/test_save.txt')
        user_input = ['', '', 'y']
        with patch('builtins.input', side_effect=user_input):
            file.create_new_file('new')
        self.assertEqual(file.hexbytes, [])

    def test_create_new_file_error(self):
        file = HexFile()
        with self.assertRaises(ValueError):
            file.create_new_file('new asdf asdf')

    def test_open_errors(self):
        file = HexFile()
        with self.assertRaises(ValueError):
            file.open('open')
        with self.assertRaises(ValueError):
            file.open('open filename undefined')
        with self.assertRaises(ValueError):
            file.open('open FILE_DONT_EXIST')

    def test_open(self):
        file = HexFile('files_for_test/test_save.txt')
        user_input = ['', '', 'y']
        with patch('builtins.input', side_effect=user_input):
            file.open('open files_for_test/test_save_as_exist.txt')
        self.assertEqual(file.hexbytes, ['50', '51', '52', '53'])

    def test_get_changes(self):
        file = HexFile('files_for_test/test_file.txt')
        file.insert('insert 0 50')
        file.delete_bytes('delete :10')
        file.replace('replace 3 abcd')
        user_input = ['', 'n']
        with patch('builtins.input', side_effect=user_input):
            file.open('open files_for_test/test_save.txt')
        with patch('builtins.input', side_effect=user_input):
            file.create_new_file('new')
        expected_result = "INSERT: start=0, bytes=50\n" \
                          "DELETE: start=('0', '10'), bytes=5061[26 chars]" \
                          "6364\nREPLACE: start=3, old_bytes=6869, new_byt" \
                          "es=abcd\nOPEN: old_file=files_for_test/test_fil" \
                          "e.txt, new_file=files_for_test/test_save.txt\n" \
                          "NEW_FILE: old_file=files_for_test/test_save.txt"
        actual_result = file.get_changes()
        self.assertEqual(expected_result, actual_result)


class CMainTest(unittest.TestCase):
    def test_main(self):
        del sys.argv[1:]
        sys.argv.append('files_for_test/test_file.txt')
        user_input = ['help', 'save', 'changes', 'print :20', 'replace 0 55',
                      'insert 0 59', 'del 0:2', 'open', 'new', 'n', 'save as',
                      'files_for_test/test_save.txt', 'n', 'exit', 'n']
        sys.stdout = StringIO()
        with patch('builtins.input', side_effect=user_input):
            cmain.main()

    def test_main_without_name(self):
        del sys.argv[1:]
        user_input = ['exit', 'n']
        sys.stdout = StringIO()
        with patch('builtins.input', side_effect=user_input):
            cmain.main()


if __name__ == '__main__':
    unittest.main()
