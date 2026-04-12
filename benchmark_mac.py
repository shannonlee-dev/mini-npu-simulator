import argparse
import time


def build_dense_matrices(size):
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


def build_sparse_shape_matrices(size, shape):
    pattern = [[0.0 for _ in range(size)] for _ in range(size)]
    filt = [[0.0 for _ in range(size)] for _ in range(size)]
    center = size // 2

    for row in range(size):
        for col in range(size):
            if shape == "cross":
                active = row == center or col == center
            else:
                active = row == col or row + col == size - 1

            if active:
                pattern[row][col] = 1.0
                filt[row][col] = 1.0

    return pattern, filt


def flatten_matrix(matrix):
    flat = []

    for row in matrix:
        flat.extend(row)

    return flat


def compile_sparse_filter(filt):
    active = []

    for row_index, row in enumerate(filt):
        for col_index, value in enumerate(row):
            if value != 0:
                active.append((row_index, col_index, value))

    return active


def mac_1_dense_index(pattern, filt):
    size = len(pattern)
    total = 0.0

    for i in range(size):
        for j in range(size):
            total += pattern[i][j] * filt[i][j]

    return total


def mac_2_zip_rows(pattern, filt):
    total = 0.0

    for pattern_row, filt_row in zip(pattern, filt):
        for pattern_value, filt_value in zip(pattern_row, filt_row):
            total += pattern_value * filt_value

    return total


def mac_3_generator_zip(pattern, filt):
    return sum(
        pattern_value * filt_value
        for pattern_row, filt_row in zip(pattern, filt)
        for pattern_value, filt_value in zip(pattern_row, filt_row)
    )


def mac_4_flat_index(pattern_flat, filt_flat):
    total = 0.0

    for index in range(len(pattern_flat)):
        total += pattern_flat[index] * filt_flat[index]

    return total


def mac_5_flat_zip(pattern_flat, filt_flat):
    total = 0.0

    for pattern_value, filt_value in zip(pattern_flat, filt_flat):
        total += pattern_value * filt_value

    return total


def mac_6_sparse_coords(pattern, active_filter):
    total = 0.0

    for row_index, col_index, value in active_filter:
        total += pattern[row_index][col_index] * value

    return total


def measure_average_ms(func, *args, repeat):
    total_ms = 0.0
    last_result = None

    for _ in range(repeat):
        start = time.perf_counter()
        last_result = func(*args)
        end = time.perf_counter()
        total_ms += (end - start) * 1000.0

    return total_ms / repeat, last_result


def build_benchmark_cases(size):
    dense_pattern, dense_filter = build_dense_matrices(size)
    sparse_pattern, sparse_filter = build_sparse_shape_matrices(size, "cross")

    dense_pattern_flat = flatten_matrix(dense_pattern)
    dense_filter_flat = flatten_matrix(dense_filter)
    sparse_pattern_flat = flatten_matrix(sparse_pattern)
    sparse_filter_flat = flatten_matrix(sparse_filter)

    sparse_coords = compile_sparse_filter(sparse_filter)
    return {
        "dense": {
            "pattern": dense_pattern,
            "filter": dense_filter,
            "pattern_flat": dense_pattern_flat,
            "filter_flat": dense_filter_flat,
            "sparse_coords": compile_sparse_filter(dense_filter),
            "active_count": sum(1 for value in dense_filter_flat if value != 0),
        },
        "sparse": {
            "pattern": sparse_pattern,
            "filter": sparse_filter,
            "pattern_flat": sparse_pattern_flat,
            "filter_flat": sparse_filter_flat,
            "sparse_coords": compile_sparse_filter(sparse_filter),
            "active_count": len(sparse_coords),
        },
    }


def run_suite(title, case, repeat):
    entries = [
        ("1. dense index", mac_1_dense_index, (case["pattern"], case["filter"])),
        ("2. zip rows", mac_2_zip_rows, (case["pattern"], case["filter"])),
        ("3. generator zip", mac_3_generator_zip, (case["pattern"], case["filter"])),
        ("4. flat index", mac_4_flat_index, (case["pattern_flat"], case["filter_flat"])),
        ("5. flat zip", mac_5_flat_zip, (case["pattern_flat"], case["filter_flat"])),
        ("6. sparse coords", mac_6_sparse_coords, (case["pattern"], case["sparse_coords"])),
    ]

    baseline_result = None
    print()
    print(title)
    print(f"{'방식':<20}{'평균 시간(ms)':<18}{'결과':<14}{'비고'}")
    print("-" * 68)

    for name, func, args in entries:
        avg_ms, result = measure_average_ms(func, *args, repeat=repeat)

        if baseline_result is None:
            baseline_result = result

        note = "OK" if abs(result - baseline_result) < 1e-9 else "DIFF"
        print(f"{name:<20}{avg_ms:<18.6f}{result:<14.6f}{note}")


def print_optimization_notes():
    print("최적화 방식 번호")
    print("1. dense index: 원본 방식, 2차원 인덱스 접근")
    print("2. zip rows: zip으로 행/원소 순회")
    print("3. generator zip: sum(generator) + zip")
    print("4. flat index: 1차원 flatten 후 인덱스 순회")
    print("5. flat zip: 1차원 flatten 후 zip 순회")
    print("6. sparse coords: 필터의 0이 아닌 좌표만 전처리")


def main():
    parser = argparse.ArgumentParser(description="순수 파이썬 MAC 최적화 벤치마크")
    parser.add_argument("--size", type=int, default=25, help="행렬 크기")
    parser.add_argument("--repeat", type=int, default=5000, help="반복 측정 횟수")
    args = parser.parse_args()

    cases = build_benchmark_cases(args.size)

    print_optimization_notes()
    print()
    print(f"입력 크기: {args.size}x{args.size}")
    print(f"반복 횟수: {args.repeat}")
    print(f"dense 활성 원소 수: {cases['dense']['active_count']}")
    print(f"sparse 활성 원소 수: {cases['sparse']['active_count']}")

    run_suite("[Dense Case] 값이 전역에 퍼진 일반 행렬", cases["dense"], args.repeat)
    run_suite("[Sparse Case] + 모양처럼 0이 많은 희소 필터", cases["sparse"], args.repeat)


if __name__ == "__main__":
    main()
