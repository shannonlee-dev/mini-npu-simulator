import json
import time

EPSILON = 1e-9
MEASURE_REPEAT = 10
STANDARD_LABELS = ("Cross", "X")


def print_title():
    print("=== Mini NPU Simulator ===")
    print()
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")


def normalize_label(value):
    text = str(value).strip().lower()

    if text == "+" or text == "cross":
        return "Cross"
    if text == "x":
        return "X"

    return str(value).strip()


def parse_matrix_row(line, expected_size):
    pass


def read_matrix_from_console(name, size):
    pass


def validate_square_matrix(matrix, size):
    pass


def mac(pattern, filt):
    pass


def judge_scores(score_cross, score_x, epsilon=EPSILON):
    pass


def measure_average_ms(func, *args, repeat=MEASURE_REPEAT):
    pass


def load_json_file(path):
    pass


def extract_size_from_pattern_key(pattern_key):
    pass


def load_filters_from_json(data):
    pass


def analyze_single_pattern(pattern_key, pattern_info, filters_by_size):
    pass


def print_performance_table():
    pass


def run_user_mode():
    pass


def run_json_mode():
    pass


def main():
    print_title()
    choice = input("선택: ").strip()

    if choice == "1":
        run_user_mode()
    elif choice == "2":
        run_json_mode()
    else:
        print("잘못된 입력입니다. 1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()
