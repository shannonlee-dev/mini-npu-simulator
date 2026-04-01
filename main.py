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
    size = extract_size_from_pattern_key(pattern_key)
    pattern = pattern_info.get("input")
    expected = normalize_label(pattern_info.get("expected"))

    if size not in filters_by_size:
        raise ValueError(f"해당 크기의 필터가 없습니다: size_{size}")

    validate_square_matrix(pattern, size)

    cross_filter = filters_by_size[size]["Cross"]
    x_filter = filters_by_size[size]["X"]

    score_cross = mac(pattern, cross_filter)
    score_x = mac(pattern, x_filter)
    predicted = judge_scores(score_cross, score_x)
    result = "PASS" if predicted == expected else "FAIL"

    return {
        "pattern_key": pattern_key,
        "size": size,
        "score_cross": score_cross,
        "score_x": score_x,
        "predicted": predicted,
        "expected": expected,
        "result": result,
    }


def print_performance_table():
    size_3_cross = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ]
    size_3_x = [
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1],
    ]

    examples = {
        3: (size_3_cross, size_3_x),
    }

    print()
    print("#---------------------------------------")
    print("# [성능 분석] 평균/10회")
    print("#---------------------------------------")
    print(f"{'크기':<10}{'평균 시간(ms)':<20}{'연산 횟수(N^2)':<15}")
    print("-" * 45)

    for size, matrices in examples.items():
        avg_ms = measure_average_ms(mac, matrices[0], matrices[1])
        print(f"{size}x{size:<7}{avg_ms:<20.6f}{size * size:<15}")


def run_user_mode():
    print()
    print("#---------------------------------------")
    print("# [1] 필터 입력")
    print("#---------------------------------------")
    filter_a = read_matrix_from_console("필터 A", 3)
    filter_b = read_matrix_from_console("필터 B", 3)

    print()
    print("#---------------------------------------")
    print("# [2] 패턴 입력")
    print("#---------------------------------------")
    pattern = read_matrix_from_console("패턴", 3)

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    avg_ms = measure_average_ms(mac, pattern, filter_a)

    if abs(score_a - score_b) < EPSILON:
        decision = "판정 불가"
    elif score_a > score_b:
        decision = "A"
    else:
        decision = "B"

    print()
    print("#---------------------------------------")
    print("# [3] MAC 결과")
    print("#---------------------------------------")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"연산 시간(평균/10회): {avg_ms:.6f} ms")
    print(f"판정: {decision}")

    print_performance_table()


def run_json_mode():
    print()
    print("#---------------------------------------")
    print("# [1] 필터 로드")
    print("#---------------------------------------")

    data = load_json_file("data.json")
    filters_by_size = load_filters_from_json(data)

    for size in sorted(filters_by_size.keys()):
        print(f"✓ size_{size} 필터 로드 완료 (Cross, X)")

    print()
    print("#---------------------------------------")
    print("# [2] 패턴 분석")
    print("#---------------------------------------")

    patterns = data.get("patterns", {})
    total = 0
    passed = 0
    failed = 0
    failures = []

    for pattern_key, pattern_info in patterns.items():
        total += 1

        print(f"--- {pattern_key} ---")

        try:
            analysis = analyze_single_pattern(pattern_key, pattern_info, filters_by_size)

            print(f"Cross 점수: {analysis['score_cross']:.6f}")
            print(f"X 점수: {analysis['score_x']:.6f}")
            print(
                f"판정: {analysis['predicted']} | expected: {analysis['expected']} | {analysis['result']}"
            )

            if analysis["result"] == "PASS":
                passed += 1
            else:
                failed += 1
                failures.append(
                    f"{pattern_key}: expected={analysis['expected']}, predicted={analysis['predicted']}"
                )

        except Exception as err:
            failed += 1
            print(f"판정 실패: FAIL | 사유: {err}")
            failures.append(f"{pattern_key}: {err}")

        print()

    print("#---------------------------------------")
    print("# [3] 성능 분석")
    print("#---------------------------------------")
    print(f"{'크기':<10}{'평균 시간(ms)':<20}{'연산 횟수(N^2)':<15}")
    print("-" * 45)

    size_3_cross = [
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ]
    size_3_x = [
        [1, 0, 1],
        [0, 1, 0],
        [1, 0, 1],
    ]

    avg_ms_3 = measure_average_ms(mac, size_3_cross, size_3_x)
    print(f"{'3x3':<10}{avg_ms_3:<20.6f}{9:<15}")

    for size in sorted(filters_by_size.keys()):
        cross_filter = filters_by_size[size]["Cross"]
        x_filter = filters_by_size[size]["X"]
        avg_ms = measure_average_ms(mac, cross_filter, x_filter)
        print(f"{f'{size}x{size}':<10}{avg_ms:<20.6f}{size * size:<15}")

    print()
    print("#---------------------------------------")
    print("# [4] 결과 요약")
    print("#---------------------------------------")
    print(f"총 테스트: {total}개")
    print(f"통과: {passed}개")
    print(f"실패: {failed}개")

    if failures:
        print()
        print("실패 케이스:")
        for failure in failures:
            print(f"- {failure}")


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
