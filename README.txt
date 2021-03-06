HEX
Версия 1.1
Автор: Акбаров Ильнур

Описание:
Данное приложение позволяет просматривать и редактировать hex код файла.

Состав:
    Консольная версия: cmain.py
    Логика: HexFile.py
    Тесты: test_hexfile.py
    Файлы для проверки чтения/записи: files_for_test/

Консольная версия:
    Запуск: ./cmain.py [fileName]
        [filename] - (необязательный аргумент) - файл, открываемый при старте программы
    Справка: --help

Подробности реализации:
    Программа считывает все байты файла и переводит их в hex, создавая список, где
        каждый элемент = 1 байт в 16-ой системе счисления/
    Доступные команды:
        open [filename]          - открыть файл (аргумент обязателен)
        save                     - сохранить файл
        save as [filename]       - сохранить файл как [filename]
        exit                     - выход из программы
        new [filename ]          - создать новый файл (аргумент необязателен)
        print [start]:[end]      - вывод байт с [start] по [end] включительно
                                   можно не указывать [start] и(или) [end], тогда
                                   по умолчанию [start] равен 0, а [end] равен номеру последнего байта
        print                    - вывод с 0 по 256 байт включительно
        insert [start] [bytes]   - вставить [bytes], начиная с индекса [start]
        insertf [start] [chars]  - вставить ascii символы [chars], начиная с индекса [start]
        replace [start] [bytes]  - заменить [bytes], начиная с индекса [start]
                                   при этом, если [bytes] больше, чем байт в файле с индекса [start]
                                   до конца файла, то лишние байты вставятся в конец
        replacef [start] [chars] - заменить ascii символы [chars], начиная с индекса [start]
        changes                  - показать все изменения за текущую сессию
        del [start]:[end]        - удалить байты с [start] по [end] включительно
                                   байты с индексами [start] и [end] должны существовать
        del [index]              - удаляет байт с индексом [index]

    На логический модуль (HexFile.py) и cmain.py написаны тесты, покрытие по строкам 99%
    Module              statements  missing  excluded   coverage
    test_hexfile.py     233         0        0          100%
    HexFile.py          225         1        0          99%
    cmain.py            47          4        0          91%
    Total               124         10       0          99%

Коды выхода:
    1: файл не найден