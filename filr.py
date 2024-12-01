import argparse
import struct
import yaml
import sys

# Данные для логирования и результатов
result_data = []
log_file_data = []

# Память УВМ
memory = [0] * 10000
stack = []

# Команды УВМ
COMMANDS = {
    1: "LOAD_CONSTANT",
    7: "LOAD_FROM_MEMORY",
    2: "STORE_TO_MEMORY",
    3: "MULTIPLY"
}

def parse_args():
    parser = argparse.ArgumentParser(description="Assembler and Interpreter for UVM")
    parser.add_argument("mode", choices=["assemble", "interpret"], help="Mode: 'assemble' or 'interpret'")
    parser.add_argument("input_file", help="Input file path")
    parser.add_argument("output_file", help="Output file path (binary for assemble, YAML for interpret)")
    parser.add_argument("log_file", help="Log file path (YAML format)")
    parser.add_argument("--result_file", help="Result file path (YAML format, for interpretation)")
    parser.add_argument("--memory_range", help="Memory range for interpretation (start:end)", type=str)
    return parser.parse_args()

def parse_instruction(line):
    """Парсинг строки инструкции в формате A=1, B=803."""
    parts = line.split(',')
    instruction = {}
    for part in parts:
        key, value = part.split('=')
        instruction[key.strip()] = int(value.strip())
    return instruction

def assemble_instruction(instruction):
    """Ассемблирование инструкции в 5-байтный бинарный формат."""
    global result_data, log_file_data
    A = instruction.get("A", 0) & 0x7
    B = instruction.get("B", 0) & 0xFFFFFF
    command = (A << 29) | B

    # Разбиваем на 5 байт
    bytes_repr = [(command >> (8 * i)) & 0xFF for i in range(5)]
    result_data.extend(bytes_repr)
    log_file_data.append({
        "A": A,
        "B": B,
        "command": [hex(b) for b in bytes_repr]
    })

result_vector = []  # Новый вектор для хранения результатов

def execute_command(opcode, arg):
    """Выполнение команды УВМ."""
    global memory, stack, result_vector  # Используем глобальные переменные
    if opcode == 1:  # LOAD_CONSTANT
        stack.append(arg)
    elif opcode == 7:  # LOAD_FROM_MEMORY
        if not stack:
            raise ValueError("Stack is empty, cannot load from memory")
        address = stack.pop()
        stack.append(memory[address])
    elif opcode == 2:  # STORE_TO_MEMORY
        if not stack:
            raise ValueError("Stack is empty, cannot store to memory")
        value = stack.pop()
        memory[arg] = value
    elif opcode == 3:  # MULTIPLY
        if not stack:
            raise ValueError("Stack is empty, cannot multiply")
        value = stack.pop()
        result = value * memory[arg]
        stack.append(result)
        memory[arg] = result
        result_vector.append(result)  # Сохраняем результат в вектор
    else:
        raise ValueError(f"Unknown opcode: {opcode}")



def assemble(input_file, output_file, log_file):
    """Ассемблирование из текстового файла в бинарный."""
    global result_data, log_file_data
    result_data.clear()
    log_file_data.clear()

    # Чтение и обработка исходных инструкций
    with open(input_file, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            instruction = parse_instruction(line)
            assemble_instruction(instruction)

    # Запись бинарного файла
    with open(output_file, "wb") as file:
        file.write(bytearray(result_data))

    # Запись логов в YAML
    with open(log_file, "w", encoding="utf-8") as file:
        yaml.dump(log_file_data, file, allow_unicode=True)

    print(f"Assembly completed. Binary saved to {output_file}, log saved to {log_file}")

def interpret(input_file, output_file, log_file, result_file, memory_range):
    """Интерпретация бинарного файла."""
    global memory, stack
    memory = [0] * 10000
    stack = []
    log_file_data.clear()

    # Чтение бинарного файла
    with open(input_file, "rb") as file:
        binary_data = file.read()

    # Интерпретация команд
    for i in range(0, len(binary_data), 5):
        chunk = binary_data[i:i + 5]
        if len(chunk) < 5:
            break
        command = struct.unpack("<I", chunk[:4])[0]
        opcode = (command >> 29) & 0x7
        arg = command & 0xFFFFFF
        execute_command(opcode, arg)
        log_file_data.append({"opcode": opcode, "arg": arg, "stack": list(stack)})

    # Сохранение лога в YAML
    with open(log_file, "w", encoding="utf-8") as file:
        yaml.dump(log_file_data, file, allow_unicode=True)

    # Сохранение результата в YAML
    start, end = map(int, memory_range.split(":"))
    memory_slice = memory[start:end]
    with open(result_file, "w", encoding="utf-8") as file:
        yaml.dump({"memory": memory_slice}, file, allow_unicode=True)

    print(f"Interpretation completed. Results saved to {result_file}, log saved to {log_file}")

def main():
    args = parse_args()

    if args.mode == "assemble":
        assemble(args.input_file, args.output_file, args.log_file)
    elif args.mode == "interpret":
        if not args.result_file or not args.memory_range:
            print("Error: result_file and memory_range are required for interpretation")
            sys.exit(1)
        interpret(args.input_file, args.output_file, args.log_file, args.result_file, args.memory_range)

if __name__ == "__main__":
    main()
