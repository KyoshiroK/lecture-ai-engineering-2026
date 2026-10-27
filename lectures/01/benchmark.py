"""第1回 発展課題:
複数の質問について、LLMの応答時間とトークン数を計測する。

使い方:
    uv run python -m app.benchmark
"""

import csv
import time
from pathlib import Path

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key


# ==============================
# 実験条件
# ==============================

QUESTIONS = [
    "LoRAとは何ですか？一文で説明してください。",
    "LoRAとは何ですか？初心者向けに説明してください。",
    "LoRAの仕組み、メリット、デメリット、利用例を詳しく説明してください。",
]

TRIALS = 3

OUTPUT_FILE = Path(f"benchmark_results_{MODEL}.csv")


# ==============================
# 1回のAPI呼び出しを計測
# ==============================

def measure(client, question: str, trial: int) -> dict:
    """1回質問し、応答時間とトークン数を返す。"""

    start = time.perf_counter()

    response = client.models.generate_content(
        model=MODEL,
        contents=question,
    )

    elapsed = time.perf_counter() - start

    usage = response.usage_metadata

    input_tokens = getattr(
        usage,
        "prompt_token_count",
        None,
    )

    output_tokens = getattr(
        usage,
        "candidates_token_count",
        None,
    )

    total_tokens = getattr(
        usage,
        "total_token_count",
        None,
    )

    return {
        "model": MODEL,
        "question": question,
        "trial": trial,
        "response_time_sec": round(elapsed, 3),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "status": "OK",
    }


# ==============================
# 結果をCSVに保存
# ==============================

def save_results(results: list[dict]) -> None:
    """測定結果をCSVファイルに保存する。"""

    fieldnames = [
        "model",
        "question",
        "trial",
        "response_time_sec",
        "input_tokens",
        "output_tokens",
        "total_tokens",
        "status",
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)


# ==============================
# メイン処理
# ==============================

def main() -> None:

    print("=" * 60)
    print("AIE2026 第1回 発展課題")
    print("LLM Benchmark")
    print("=" * 60)

    print(f"\n[model] {MODEL}")
    print(f"[questions] {len(QUESTIONS)}")
    print(f"[trials] {TRIALS}")

    client = genai.Client(
        api_key=get_api_key()
    )

    results = []

    for question_no, question in enumerate(
        QUESTIONS,
        start=1,
    ):

        print("\n" + "-" * 60)
        print(f"[Question {question_no}]")
        print(question)
        print("-" * 60)

        for trial in range(1, TRIALS + 1):

            print(
                f"Trial {trial}/{TRIALS} ... ",
                end="",
                flush=True,
            )

            try:

                result = measure(
                    client,
                    question,
                    trial,
                )

                results.append(result)

                print(
                    f"{result['response_time_sec']:.3f} sec"
                    f" | input={result['input_tokens']}"
                    f" | output={result['output_tokens']}"
                    f" | total={result['total_tokens']}"
                )

            except errors.APIError as e:

                print("API ERROR")

                print(
                    api_error_message(
                        e.code,
                        e.message,
                    )
                )

                results.append(
                    {
                        "model": MODEL,
                        "question": question,
                        "trial": trial,
                        "response_time_sec": None,
                        "input_tokens": None,
                        "output_tokens": None,
                        "total_tokens": None,
                        "status": f"API_ERROR_{e.code}",
                    }
                )

            # APIを短時間に連続して呼びすぎないための間隔
            time.sleep(2)

    # ==============================
    # CSV保存
    # ==============================

    save_results(results)

    print("\n" + "=" * 60)
    print("Benchmark completed")
    print("=" * 60)

    print(
        f"\nResults saved to: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()