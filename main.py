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
    parts = line.strip().split()

    if len(parts) != expected_size:
        raise ValueError(
            f"입력 형식 오류: 각 줄에 {expected_size}개의 숫자를 공백으로 구분해 입력하세요."
        )

    row = []
    for part in parts:
        try:
            row.append(float(part))
        except ValueError as exc:
            raise ValueError(
                f"입력 형식 오류: 숫자만 입력하세요. 잘못된 값: {part}"
            ) from exc

    return row


def read_matrix_from_console(name, size):
    print(f"{name} ({size}줄 입력, 공백 구분)")

    matrix = []
    row_index = 0

    while row_index < size:
        line = input().strip()

        try:
            row = parse_matrix_row(line, size)
            matrix.append(row)
            row_index += 1
        except ValueError as err:
            print(err)

    return matrix


def validate_square_matrix(matrix, size):
    if not isinstance(matrix, list):
        raise ValueError("행렬 데이터가 리스트가 아닙니다.")

    if len(matrix) != size:
        raise ValueError(f"행 개수 불일치: 기대값={size}, 실제값={len(matrix)}")

    for row in matrix:
        if not isinstance(row, list):
            raise ValueError("행렬의 각 행은 리스트여야 합니다.")
        if len(row) != size:
            raise ValueError(f"열 개수 불일치: 기대값={size}, 실제값={len(row)}")


def mac(pattern, filt):
    size = len(pattern)
    total = 0.0

    for i in range(size):
        for j in range(size):
            total += pattern[i][j] * filt[i][j]

    return total


def judge_scores(score_cross, score_x, epsilon=EPSILON):
    if abs(score_cross - score_x) < epsilon:
        return "UNDECIDED"

    if score_cross > score_x:
        return "Cross"

    return "X"


def measure_average_ms(func, *args, repeat=MEASURE_REPEAT):
    total = 0.0

    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        end = time.perf_counter()
        total += (end - start) * 1000.0

    return total / repeat


def load_json_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def extract_size_from_pattern_key(pattern_key):
    parts = pattern_key.split("_")

    if len(parts) < 3 or parts[0] != "size":
        raise ValueError(f"패턴 키 형식 오류: {pattern_key}")

    try:
        return int(parts[1])
    except ValueError as exc:
        raise ValueError(f"패턴 크기 파싱 실패: {pattern_key}") from exc


def load_filters_from_json(data):
    filters = data.get("filters", {})
    filters_by_size = {}

    for size_key, filter_info in filters.items():
        size = int(size_key.split("_")[1])

        cross_filter = None
        x_filter = None

        for raw_label, matrix in filter_info.items():
            label = normalize_label(raw_label)

            if label == "Cross":
                cross_filter = matrix
            elif label == "X":
                x_filter = matrix

        if cross_filter is None or x_filter is None:
            raise ValueError(f"{size_key} 필터에 Cross 또는 X가 없습니다.")

        validate_square_matrix(cross_filter, size)
        validate_square_matrix(x_filter, size)

        filters_by_size[size] = {
            "Cross": cross_filter,
            "X": x_filter,
        }

    return filters_by_size


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
