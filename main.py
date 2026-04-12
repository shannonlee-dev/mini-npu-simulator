import json
import sys
import time

EPSILON = 1e-9
MEASURE_REPEAT = 10
STANDARD_LABELS = ("Cross", "X")
ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_CYAN = "\033[96m"
ANSI_GOLD = "\033[93m"
ANSI_MAGENTA = "\033[95m"
ANSI_GREEN = "\033[92m"
ANSI_RED = "\033[91m"
ANSI_BLUE = "\033[94m"


# 출력 영역
# 프로그램 제목과 모드 선택 메뉴를 보여준다.
def print_title():
    print("=== Mini NPU Simulator ===")
    print()
    print("[모드 선택]")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")


# 문자열에 ANSI 색상을 입힌다.
def colorize(text, *styles):
    return "".join(styles) + str(text) + ANSI_RESET


# 숨겨진 3번 모드 진입 시 화려한 연출을 출력한다.
def print_secret_mode_banner():
    fireworks = [
        colorize("        *         .        +        *", ANSI_MAGENTA, ANSI_BOLD),
        colorize("   .        *   SECRET MODE   *      .", ANSI_CYAN, ANSI_BOLD),
        colorize("        +       BOOM! BOOM!       +   ", ANSI_GOLD, ANSI_BOLD),
    ]
    title = colorize(">>> 2D vs 1D FLATTEN BENCHMARK UNLOCKED <<<", ANSI_GREEN, ANSI_BOLD)

    print()
    for line in fireworks:
        print(line)
        sys.stdout.flush()
        time.sleep(0.08)

    print(title)
    print(colorize("    숨겨진 성능 비교 모드가 열렸습니다.", ANSI_MAGENTA))
    print()


# 숨겨진 4번 모드 진입 시 더 화려한 연출을 출력한다.
def print_secret_benchmark_banner():
    parade = [
        colorize(" .  *   .   *   .  RAINBOW BENCH  .   *  . ", ANSI_RED, ANSI_BOLD),
        colorize("   +   *   1 to 7 MAC SPEED SHOWDOWN   *   +", ANSI_GOLD, ANSI_BOLD),
        colorize(" *   .   ZIP! FLAT! SPARSE!   .   *   .    ", ANSI_CYAN, ANSI_BOLD),
        colorize("   *   .   CONFETTI! FIREWORKS!   .   *    ", ANSI_MAGENTA, ANSI_BOLD),
    ]
    title = colorize(">>> FULL MAC OPTIMIZATION BENCHMARK UNLOCKED <<<", ANSI_GREEN, ANSI_BOLD)

    print()
    for line in parade:
        print(line)
        sys.stdout.flush()
        time.sleep(0.08)

    print(title)
    print(colorize("    1번부터 7번까지 전부 비교합니다.", ANSI_BLUE, ANSI_BOLD))
    print()


# 3번 모드 전용 컬러 프롬프트로 양의 정수를 입력받는다.
def read_secret_positive_int(prompt, color):
    return read_positive_int(colorize(prompt, color, ANSI_BOLD))


# 공통 처리 영역
# 입력 라벨을 표준 라벨로 정규화한다.
def normalize_label(value):
    text = str(value).strip().lower()

    if text == "+" or text == "cross":
        return "Cross"
    if text == "x":
        return "X"

    return str(value).strip()


# 한 줄 입력을 숫자 행렬 한 줄로 변환한다.
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


# 콘솔에서 정사각 행렬을 입력받는다.
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


# 양의 정수를 입력받는다.
def read_positive_int(prompt):
    while True:
        raw = input(prompt).strip()

        try:
            value = int(raw)
        except ValueError:
            print("정수만 입력하세요.")
            continue

        if value <= 0:
            print("1 이상의 정수를 입력하세요.")
            continue

        return value


# 행렬 크기와 구조가 올바른지 검사한다.
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


# 연산 영역
# 패턴과 필터의 MAC 점수를 계산한다.
def mac(pattern, filt):
    size = len(pattern)
    total = 0.0

    for i in range(size):
        for j in range(size):
            
            total += pattern[i][j] * filt[i][j]

    return total


# 2차원 행렬을 1차원 리스트로 펼친다.
def flatten_matrix(matrix):
    flat = []

    for row in matrix:
        flat.extend(row)

    return flat


# 1차원 리스트 두 개를 N x N 행렬처럼 해석해 MAC를 계산한다.
def mac_flat(pattern_flat, filt_flat, size):
    total = 0.0

    for row in range(size):
        row_start = row * size
        for col in range(size):
            index = row_start + col  # i * N + j
            total += pattern_flat[index] * filt_flat[index]

    return total


def mac_zip(pattern, filt):
    total = 0.0

    for pattern_row, filt_row in zip(pattern, filt):
        for pattern_value, filt_value in zip(pattern_row, filt_row):
            total += pattern_value * filt_value

    return total


def mac_generator_zip(pattern, filt):
    return sum(
        pattern_value * filt_value
        for pattern_row, filt_row in zip(pattern, filt)
        for pattern_value, filt_value in zip(pattern_row, filt_row)
    )


def mac_flat_zip(pattern_flat, filt_flat):
    total = 0.0

    for pattern_value, filt_value in zip(pattern_flat, filt_flat):
        total += pattern_value * filt_value

    return total


def compile_sparse_filter(filt):
    active = []

    for row_index, row in enumerate(filt):
        for col_index, value in enumerate(row):
            if value != 0:
                active.append((row_index, col_index, value))

    return active


def compile_sparse_rows(filt):
    compiled = []

    for row_index, row in enumerate(filt):
        active_cols = []

        for col_index, value in enumerate(row):
            if value != 0:
                active_cols.append((col_index, value))

        if active_cols:
            compiled.append((row_index, active_cols))

    return compiled


def mac_sparse_coords(pattern, active_filter):
    total = 0.0

    for row_index, col_index, value in active_filter:
        total += pattern[row_index][col_index] * value

    return total


def mac_sparse_rows(pattern, compiled_rows):
    total = 0.0

    for row_index, active_cols in compiled_rows:
        pattern_row = pattern[row_index]

        for col_index, value in active_cols:
            total += pattern_row[col_index] * value

    return total


# 두 점수를 비교해 최종 라벨을 결정한다.
def judge_scores(score_cross, score_x, epsilon=EPSILON):
    if abs(score_cross - score_x) < epsilon:
        return "UNDECIDED"

    if score_cross > score_x:
        return "Cross"

    return "X"


# 함수 실행 시간을 여러 번 측정해 평균 ms를 계산한다.
def measure_average_ms(func, *args, repeat=MEASURE_REPEAT):
    total = 0.0

    for _ in range(repeat):
        start = time.perf_counter()
        func(*args)
        end = time.perf_counter()
        total += (end - start) * 1000.0

    return total / repeat


# 성능 비교용 NxN 예제 행렬 두 개를 만든다.
def build_benchmark_matrices(size):
    pattern = []
    filt = []

    for row in range(size):
        pattern_row = []
        filt_row = []

        for col in range(size):
            pattern_row.append(float(((row * size) + col) % 7))
            filt_row.append(float(((row + 1) * (col + 3)) % 5))

        pattern.append(pattern_row)
        filt.append(filt_row)

    return pattern, filt


def build_sparse_benchmark_matrices(size):
    pattern = [[0.0 for _ in range(size)] for _ in range(size)]
    filt = [[0.0 for _ in range(size)] for _ in range(size)]
    center = size // 2

    for row in range(size):
        for col in range(size):
            if row == center or col == center:
                pattern[row][col] = 1.0
                filt[row][col] = 1.0

    return pattern, filt


# JSON 처리 영역
# JSON 파일을 읽어 파이썬 객체로 변환한다.
def load_json_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


# 패턴 키에서 정사각 행렬 크기를 추출한다.
def extract_size_from_pattern_key(pattern_key):
    parts = pattern_key.split("_")

    if len(parts) < 3 or parts[0] != "size":
        raise ValueError(f"패턴 키 형식 오류: {pattern_key}")

    try:
        return int(parts[1])
    except ValueError as exc:
        raise ValueError(f"패턴 크기 파싱 실패: {pattern_key}") from exc


# JSON의 필터 정보를 크기별 표준 라벨 구조로 정리한다.
def load_filters_from_json(data):
    filters = data.get("filters", {}) #예: "size_5": {"Cross": [[...]], "X": [[...]]}
    filters_by_size = {} 

    for size_key, filter_info in filters.items():
        '''
        size_key = "size_5"
        filter_info = {"cross": [...], "x": [...]}
        ''' 
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


# 패턴 1개를 분석해 점수와 PASS/FAIL 결과를 만든다.
def analyze_single_pattern(pattern_key, pattern_info, filters_by_size):
    size = extract_size_from_pattern_key(pattern_key) # 예: "size_5_pattern_1" -> 5
    pattern = pattern_info.get("input") #예: [[0,1,0], [1,1,1], [0,1,0]]
    expected = normalize_label(pattern_info.get("expected")) #예: "Cross" -> "Cross"

    if size not in filters_by_size:
        raise ValueError(f"해당 크기의 필터가 없습니다: size_{size}")

    validate_square_matrix(pattern, size) 

    cross_filter = filters_by_size[size]["Cross"] #예: size_5 필터의 Cross 행렬
    x_filter = filters_by_size[size]["X"] #예: size_5 필터의 X 행렬

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


# 성능 분석 영역
# 기본 예제로 3x3 MAC 성능 표를 출력한다.
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


# 모드 실행 영역
# 사용자 입력 모드에서 3x3 필터와 패턴을 비교한다.
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


# JSON 분석 모드에서 전체 패턴을 일괄 판정한다.
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


# 2차원 접근과 1차원 flatten 접근의 성능을 비교한다.
def run_flatten_benchmark_mode():
    print_secret_mode_banner()
    print()
    print(colorize("#---------------------------------------", ANSI_CYAN))
    print(colorize("# [3] 2D vs 1D flatten 성능 비교", ANSI_CYAN, ANSI_BOLD))
    print(colorize("#---------------------------------------", ANSI_CYAN))

    size = read_secret_positive_int("행렬 크기 N 입력: ", ANSI_MAGENTA)
    repeat = read_secret_positive_int("반복 측정 횟수 입력: ", ANSI_GOLD)

    pattern, filt = build_benchmark_matrices(size)
    pattern_flat = flatten_matrix(pattern)
    filt_flat = flatten_matrix(filt)

    score_2d = mac(pattern, filt)
    score_1d = mac_flat(pattern_flat, filt_flat, size)
    avg_2d_ms = measure_average_ms(mac, pattern, filt, repeat=repeat)
    avg_1d_ms = measure_average_ms(mac_flat, pattern_flat, filt_flat, size, repeat=repeat)

    if abs(score_2d - score_1d) < EPSILON:
        same_result = "YES"
    else:
        same_result = "NO"

    print()
    print(colorize("#---------------------------------------", ANSI_MAGENTA))
    print(colorize("# [비교 결과]", ANSI_MAGENTA, ANSI_BOLD))
    print(colorize("#---------------------------------------", ANSI_MAGENTA))
    print(colorize("입력 크기:", ANSI_BLUE, ANSI_BOLD), colorize(f"{size}x{size}", ANSI_GOLD, ANSI_BOLD))
    print(colorize("동일 반복 횟수:", ANSI_BLUE, ANSI_BOLD), colorize(repeat, ANSI_GOLD, ANSI_BOLD))
    print(colorize("2D 결과:", ANSI_CYAN, ANSI_BOLD), colorize(f"{score_2d:.6f}", ANSI_CYAN, ANSI_BOLD))
    print(colorize("1D 결과:", ANSI_GREEN, ANSI_BOLD), colorize(f"{score_1d:.6f}", ANSI_GREEN, ANSI_BOLD))
    if same_result == "YES":
        same_result_text = colorize("YES", ANSI_GREEN, ANSI_BOLD)
    else:
        same_result_text = colorize("NO", ANSI_RED, ANSI_BOLD)
    print(colorize("결과 일치 여부:", ANSI_MAGENTA, ANSI_BOLD), same_result_text)
    print()
    print(colorize(f"{'방식':<18}{'평균 시간(ms)':<20}{'접근 수(N^2)':<15}", ANSI_BOLD))
    print(colorize("-" * 53, ANSI_GOLD))
    print(f"{colorize('2차원 배열', ANSI_CYAN):<27}{avg_2d_ms:<20.6f}{size * size:<15}")
    print(f"{colorize('1차원 flatten', ANSI_GREEN):<27}{avg_1d_ms:<20.6f}{size * size:<15}")

    delta_ms = avg_1d_ms - avg_2d_ms
    if abs(delta_ms) < EPSILON:
        summary = "체감 차이가 거의 없습니다."
        summary_style = (ANSI_GOLD, ANSI_BOLD)
    elif delta_ms < 0:
        summary = f"flatten 방식이 {-delta_ms:.6f} ms 더 빨랐습니다."
        summary_style = (ANSI_GREEN, ANSI_BOLD)
    else:
        summary = f"2차원 방식이 {delta_ms:.6f} ms 더 빨랐습니다."
        summary_style = (ANSI_CYAN, ANSI_BOLD)

    print()
    print(colorize("요약:", ANSI_MAGENTA, ANSI_BOLD), colorize(summary, *summary_style))


def collect_full_benchmark_results(case, repeat, size):
    entries = [
        ("1. dense index", mac, (case["pattern"], case["filter"])),
        ("2. zip rows", mac_zip, (case["pattern"], case["filter"])),
        ("3. generator zip", mac_generator_zip, (case["pattern"], case["filter"])),
        ("4. flat index", mac_flat, (case["pattern_flat"], case["filter_flat"], size)),
        ("5. flat zip", mac_flat_zip, (case["pattern_flat"], case["filter_flat"])),
        ("6. sparse coords", mac_sparse_coords, (case["pattern"], case["sparse_coords"])),
        ("7. sparse rows", mac_sparse_rows, (case["pattern"], case["sparse_rows"])),
    ]
    results = []

    for name, func, args in entries:
        avg_ms = measure_average_ms(func, *args, repeat=repeat)
        result = func(*args)
        results.append({
            "name": name,
            "avg_ms": avg_ms,
            "result": result,
        })

    return results


def print_full_benchmark_table(title, results):
    baseline_result = None

    print()
    print(colorize(title, ANSI_MAGENTA, ANSI_BOLD))
    print(colorize(f"{'방식':<20}{'평균 시간(ms)':<20}{'결과':<16}{'검증'}", ANSI_BOLD))
    print(colorize("-" * 68, ANSI_GOLD))

    for item in results:
        if baseline_result is None:
            baseline_result = item["result"]

        if abs(item["result"] - baseline_result) < EPSILON:
            verdict = colorize("OK", ANSI_GREEN, ANSI_BOLD)
        else:
            verdict = colorize("DIFF", ANSI_RED, ANSI_BOLD)

        print(f"{item['name']:<20}{item['avg_ms']:<20.6f}{item['result']:<16.6f}{verdict}")


def print_full_benchmark_rankings(title, results):
    ranked = sorted(results, key=lambda item: item["avg_ms"])

    print()
    print(colorize(title, ANSI_GREEN, ANSI_BOLD))
    print(colorize(f"{'순위':<8}{'방식':<20}{'평균 시간(ms)':<20}", ANSI_BOLD))
    print(colorize("-" * 48, ANSI_GOLD))

    for index, item in enumerate(ranked, start=1):
        print(f"{index:<8}{item['name']:<20}{item['avg_ms']:<20.6f}")


def run_full_benchmark_mode():
    print_secret_benchmark_banner()
    print(colorize("#---------------------------------------", ANSI_CYAN))
    print(colorize("# [4] 전체 MAC 최적화 벤치", ANSI_CYAN, ANSI_BOLD))
    print(colorize("#---------------------------------------", ANSI_CYAN))

    size = read_secret_positive_int("행렬 크기 N 입력: ", ANSI_MAGENTA)
    repeat = read_secret_positive_int("반복 측정 횟수 입력: ", ANSI_GOLD)

    dense_pattern, dense_filter = build_benchmark_matrices(size)
    sparse_pattern, sparse_filter = build_sparse_benchmark_matrices(size)

    dense_case = {
        "pattern": dense_pattern,
        "filter": dense_filter,
        "pattern_flat": flatten_matrix(dense_pattern),
        "filter_flat": flatten_matrix(dense_filter),
        "sparse_coords": compile_sparse_filter(dense_filter),
        "sparse_rows": compile_sparse_rows(dense_filter),
    }
    sparse_case = {
        "pattern": sparse_pattern,
        "filter": sparse_filter,
        "pattern_flat": flatten_matrix(sparse_pattern),
        "filter_flat": flatten_matrix(sparse_filter),
        "sparse_coords": compile_sparse_filter(sparse_filter),
        "sparse_rows": compile_sparse_rows(sparse_filter),
    }

    print()
    print(colorize("입력 크기:", ANSI_BLUE, ANSI_BOLD), colorize(f"{size}x{size}", ANSI_GOLD, ANSI_BOLD))
    print(colorize("반복 횟수:", ANSI_BLUE, ANSI_BOLD), colorize(repeat, ANSI_GOLD, ANSI_BOLD))
    print(colorize("dense 활성 원소 수:", ANSI_BLUE, ANSI_BOLD), colorize(sum(1 for value in dense_case["filter_flat"] if value != 0), ANSI_GREEN, ANSI_BOLD))
    print(colorize("sparse 활성 원소 수:", ANSI_BLUE, ANSI_BOLD), colorize(len(sparse_case["sparse_coords"]), ANSI_GREEN, ANSI_BOLD))
    print()
    print(colorize("[방식 설명]", ANSI_MAGENTA, ANSI_BOLD))
    print(colorize("1. dense index", ANSI_CYAN, ANSI_BOLD), ": 원본 방식, 2차원 인덱스 접근")
    print("   -> 기준선입니다. 현재 구현이 얼마나 느린지/빠른지 비교하는 출발점입니다.")
    print(colorize("2. zip rows", ANSI_CYAN, ANSI_BOLD), ": zip으로 행/원소 순회")
    print("   -> 인덱스 접근을 줄이면 Python 루프 비용이 얼마나 줄어드는지 보기 위한 후보입니다.")
    print(colorize("3. generator zip", ANSI_CYAN, ANSI_BOLD), ": sum(generator) + zip")
    print("   -> for 루프를 generator 표현으로 바꾸면 내장 sum 활용이 도움이 되는지 보기 위한 후보입니다.")
    print(colorize("4. flat index", ANSI_CYAN, ANSI_BOLD), ": 1차원 flatten 후 index 계산")
    print("   -> 2차원 대신 1차원 인덱스 계산이 유리한지 확인하려고 넣은 후보입니다.")
    print(colorize("5. flat zip", ANSI_CYAN, ANSI_BOLD), ": 1차원 flatten 후 zip 순회")
    print("   -> flatten 이점은 살리고 index 계산은 줄이면 더 나아지는지 보기 위한 후보입니다.")
    print(colorize("6. sparse coords", ANSI_CYAN, ANSI_BOLD), ": 0이 아닌 좌표만 전처리")
    print("   -> 희소 필터에서는 0인 위치 계산을 아예 빼는 것이 핵심이라 넣은 후보입니다.")
    print(colorize("7. sparse rows", ANSI_CYAN, ANSI_BOLD), ": 행별 활성 열만 전처리")
    print("   -> 희소 좌표 접근에 행 캐시까지 더하면 더 빨라지는지 보기 위한 후보입니다.")

    dense_results = collect_full_benchmark_results(dense_case, repeat, size)
    sparse_results = collect_full_benchmark_results(sparse_case, repeat, size)

    print_full_benchmark_table("[Dense Case] 값이 전역에 퍼진 일반 행렬", dense_results)
    print_full_benchmark_rankings("[Dense Ranking] 빠른 순위", dense_results)
    print_full_benchmark_table("[Sparse Case] + 모양처럼 0이 많은 희소 필터", sparse_results)
    print_full_benchmark_rankings("[Sparse Ranking] 빠른 순위", sparse_results)


# 프로그램 시작 영역
# 모드를 선택해 알맞은 실행 흐름으로 보낸다.
def main():
    print_title()
    choice = input("선택: ").strip()

    if choice == "1":
        run_user_mode()
    elif choice == "2":
        run_json_mode()
    elif choice == "3":
        run_flatten_benchmark_mode()
    elif choice == "4":
        run_full_benchmark_mode()
    else:
        print("잘못된 입력입니다. 1 또는 2를 입력하세요.")


if __name__ == "__main__":
    main()
