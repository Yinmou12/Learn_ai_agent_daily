from typing import Any

data_aug_result = {
    "Baseline": [0.7070, 0.6180, 0.4560, 0.5003, 0.9011, 0.7132],
    "AST": [0.7630, 0.7249, 0.7632, 0.7426, 0.7631, 0.8551],
}


def calculate_boost_ratio(
    result: dict[str, list[float]],
    cal_method_name: list[str] = None,
) -> dict[str, list[float] | None]:
    if result is None:
        return None

    final_metric_result = result.get("AST")
    if (
        final_metric_result is None
        or (isinstance(final_metric_result, list) is False)
        or (len(final_metric_result) != 6)
    ):
        return None

    if cal_method_name is None:
        cal_method_name = ["Baseline"]

    final_metric_result = result.get("AST")
    boost_ratio: dict[str, list[float]] = {}
    for method_name in cal_method_name:
        current_metric_result = result.get(method_name)
        if current_metric_result is None:
            print(f"{method_name} 指标缺失")
            continue

        if len(current_metric_result) != 6:
            print(f"{method_name} 指标长度错误")
            continue

        ratio_list = []
        for i in range(6):
            ratio_list.append(
                (
                    (final_metric_result[i] - current_metric_result[i])
                    / current_metric_result[i]
                )
                * 100
            )

        boost_ratio[f"AST--{method_name}"] = ratio_list

    return boost_ratio


def main():
    result = calculate_boost_ratio(data_aug_result)
    print(result)


if __name__ == "__main__":
    # main()
    temp_list = [0.6721, 0.7049, 0.7377]
    result = [(0.7705 - value) / value * 100 for value in temp_list]
    print(result)
    pass
