import unittest
import os
import yaml
import subprocess

class TestUVM(unittest.TestCase):

    def setUp(self):
        # Пути к файлам
        self.input_file = 'input.txt'
        self.output_bin = 'output.bin'
        self.log_file = 'log.yaml'
        self.result_file = 'result.yaml'
        self.memory_range = '0:5'

        # Создание тестового файла
        with open(self.input_file, 'w') as f:
            f.write("""A=1, B=5
A=2, B=0
A=1, B=10
A=2, B=1
A=1, B=15
A=2, B=2
A=1, B=20
A=2, B=3
A=1, B=25
A=2, B=4
A=1, B=185
A=3, B=0
A=1, B=185
A=3, B=1
A=1, B=185
A=3, B=2
A=1, B=185
A=3, B=3
A=1, B=185
A=3, B=4
""")

    def tearDown(self):
        # Удаление временных файлов
        if os.path.exists(self.output_bin):
            os.remove(self.output_bin)
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
        if os.path.exists(self.result_file):
            os.remove(self.result_file)
        if os.path.exists(self.input_file):
            os.remove(self.input_file)

    def test_assemble(self):
        # Выполнение ассемблирования
        subprocess.run(['python', 'filr.py', 'assemble', self.input_file, self.output_bin, self.log_file], check=True)

        # Проверка существования файлов
        self.assertTrue(os.path.exists(self.output_bin))
        self.assertTrue(os.path.exists(self.log_file))

        # Проверка содержимого лога
        with open(self.log_file, 'r') as f:
            log_data = yaml.safe_load(f)
            self.assertEqual(len(log_data), 20)
            self.assertEqual(log_data[0]['A'], 1)
            self.assertEqual(log_data[0]['B'], 5)

    def test_interpret(self):
        # Выполнение ассемблирования
        subprocess.run(['python', 'filr.py', 'assemble', self.input_file, self.output_bin, self.log_file], check=True)

        # Выполнение интерпретации
        subprocess.run(['python', 'filr.py', 'interpret', self.output_bin, self.result_file, self.log_file, '--result_file', self.result_file, '--memory_range', self.memory_range], check=True)

        # Проверка существования файлов
        self.assertTrue(os.path.exists(self.result_file))

        # Проверка содержимого результата
        with open(self.result_file, 'r') as f:
            result_data = yaml.safe_load(f)
            self.assertEqual(result_data['memory'], [925, 1850, 2775, 3700, 4625])

if __name__ == '__main__':
    unittest.main()
