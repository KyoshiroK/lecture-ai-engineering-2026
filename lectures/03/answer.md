# 第3回 解答

## 演習

# 1. 第1回のLLMと第3回のエージェントの回答の違い

    質問：
    「AIE2026の講座の宿題にある『3レベル』とは何ですか？」

    第3回のエージェントでは、以下の回答が得られた。
    - 基礎：講義内容の確認（知識の定着）
    - 実装：自分でコードを書く（実践力の向上）
    - 発展：調査や試行（応用力の養成）
    また、3つのうちどれか1つに取り組めば宿題が完了することや、関係する回が第1回であることも回答された。
    第1回の `app.ask` はLLM単体で回答する構成だったのに対し、第3回の `app.agent` は用語集検索などの外部ツールを利用できる構成になっている。
    このため、第3回のエージェントでは、講座固有の情報を外部データから取得して回答できる点が異なる。

# 2. --trace で確認したツール呼び出し

    質問：
    「LoRA とQLoRAの違いは？」

    実行コマンド：
    `uv run python -m app.agent --trace "LoRA とQLoRAの違いは？"`

    確認されたツール呼び出し：
    ```text
    [tool call] search_glossary({'query': 'LoRA'})
    [tool call] search_glossary({'query': 'QLoRA'})
    ```
    
    実行結果：
    - LLM呼び出し回数（requests）：2回
    - ツール呼び出し回数（tool_calls）：2回
    - 使用モデル：gemini-3.5-flash-lite

    LoRAとQLoRAについて、それぞれ別の引数で `search_glossary` が呼び出された。
    検索結果を使って、LoRAは低ランク行列を学習する手法、QLoRAはベースモデルを量子化してメモリ使用量を削減しながらLoRAで学習する手法であると説明された。
    この結果から、LLMがツールの説明文に従って必要な検索を選択し、検索結果を利用して回答する仕組みを確認できた。

# 3. 追加したツール make_quiz

    `app/tools.py` に以下の関数を追加した。
    `make_quiz(lecture: int) -> str`

    目的：
    指定した講義回の用語集から1つの用語を選び、その意味を問う確認問題と答えをJSON形式で返す。
    docstringには、次の内容を記載した。

    - 指定した回の用語から1つを選び、確認問題と答えを返す。
    - 「第2回の確認問題を出して」のように、指定した講義回の復習問題を求められたときに使用する。
    - 引数 `lecture` は講義回の番号を指定する整数。
    - 戻り値は確認問題と答えを含むJSON文字列。

    さらに、`app/agent.py` で `agent.tool_plain` を使って登録した。

# 4. make_quiz の動作確認と修正

    最初の実装では、`make_quiz` は正常に呼び出されたものの、指定した講義回の用語を取得できなかった。
    原因は、用語集のデータ構造と用語抽出条件が一致していなかったことだった。
    抽出条件を修正し、再実行したところ、以下の結果が得られた。

    **実行コマンド**
    `uv run python -m app.agent --trace "第2回の内容から確認問題を1問出して"`

    **ツール呼び出し**
    ```text
    [tool call] make_quiz({'lecture': 2})
    ```

    **ツールの戻り値**
    - 問題：「ファインチューニング」の意味は？
    - 解答：事前学習済みモデルを、特定のタスクや形式に合ったデータで追加学習させること。

    **実行結果の比較**

    | 項目 | 修正前 | 修正後 |
    |---|---|---|
    | 用語取得 | 失敗 | 成功 |
    | LLM呼び出し回数 | 3回 | 2回 |
    | ツール呼び出し回数 | 2回 | 1回 |
    | 確認問題の生成 | 講義要約から生成 | 用語集から生成 |

    修正後は `make_quiz` だけで必要な情報を取得でき、追加の `get_lecture_summary` 呼び出しが不要になった。


# 5. テスト結果

    実行コマンド：
    `uv run pytest -q`

    結果：
    ........... [100%]
    11 passed in 3.92s

    すべてのテストが成功した。

# 6. 気づき・考察

    今回の演習から、エージェントはLLM単体ではなく、モデル・ツール・実行ループを組み合わせて動作することを理解した。

    特に以下の点が重要だと感じた。
    1. ツールのdocstringは、LLMがどのツールを選択するかを判断するための情報になる。
    2. `--trace` を利用することで、実際に呼び出されたツール名、引数、呼び出し回数を確認できる。
    3. ツールの登録成功やテスト成功だけでは、期待した機能が正しく実現されているとは限らない。
    4. 今回の `make_quiz` では用語を取得できなかったため、データ構造と抽出条件を確認する必要がある。

    今後は、ツールの実行可否だけでなく、戻り値の正確性やエージェントの回答への反映も検証することが重要だと考えた。
    今回の演習では、ツールの登録と実行が成功していても、戻り値が期待どおりとは限らないことを学んだ。
    --trace によってツールの呼び出しだけでなく、戻り値も確認できたため、データ構造の不一致に気づいて修正できた。
    修正後は、LLMの呼び出し回数とツールの呼び出し回数が減少した。ツールの正確な実装が、エージェントの動作効率にも関係することを確認できた。

## 宿題

# 1. 取り組んだレベル
    **発展（a）：Google ADKによるエージェントの再構築**

# 2. 目的
    第3回演習で作成したPydantic AIベースの学習支援エージェントをGoogle ADKで再構築し、エージェントの実装方法および回答の違いを比較する。

# 3. 実施内容
    既存の `app/agent.py` に定義された `INSTRUCTIONS` と、`app/tools.py` に実装された以下の3つのツールを再利用した。
    - `search_glossary`：講座の用語を検索する。
    - `get_lecture_summary`：指定した講義回の要点を取得する。
    - `make_quiz`：指定した講義回の用語から確認問題を作成する。

    `adk_agent/glossary_agent/agent.py` および `__init__.py` を新規作成し、Google ADKの `Agent` を使用してエージェントを構築した。

    起動には以下のコマンドを使用した。
    ```
    bash
    PYTHONPATH=. uv run --with google-adk \
    adk run adk_agent/glossary_agent
    ```
    ADKの初回起動時にテレメトリーの確認が表示されたため、`n` を選択した。
    その後、`Running agent glossary_agent` と表示され、対話形式で質問できることを確認した。

# 4. Pydantic AI版とGoogle ADK版の比較
    両方のエージェントに同じ質問を入力して比較した。

    | 質問 | Pydantic AI版 | Google ADK版 |
    |---|---|---|
    | LoRAとQLoRAの違いは？ | LoRAは低ランク行列を学習し、QLoRAはベースモデルを量子化する手法と説明 | 同様の内容を説明 |
    | 第2回の内容から確認問題を1問出して | 「ファインチューニング」の意味を問う問題を生成 | 「QLoRA」の特徴を問う問題を生成 |
    | 宿題の「3レベル」とは？ | 基礎・実装・発展の3レベルを説明 | 同じ3レベルを説明 |

    いずれのエージェントも、3つの質問に対して適切な回答を生成できた。
    確認問題の内容は異なったが、用語をランダムに選択する実装のため、フレームワークの違いが直接の原因とは断定できない。

# 5. 実装方法の比較
    **Pydantic AI**
    - `Agent` でエージェントを構築する。
    - `agent.tool_plain` によってツールを登録する。
    - `INSTRUCTIONS` にエージェントの動作指示を定義する。
    - `--trace` により、ツール呼び出しと戻り値を確認できた。

    **Google ADK**
    - `google.adk.agents.Agent` でエージェントを構築する。
    - `Agent` の `tools` 引数に関数のリストを渡して登録する。
    - `instruction` 引数に既存の `INSTRUCTIONS` を渡す。
    - `adk run` により対話形式でエージェントを実行できた。

    今回の実験では、既存のツール関数や指示文を変更することなく、エージェントの構築部分を別のフレームワークに置き換えることができた。

# 6. 実験結果と考察
    Pydantic AI版とGoogle ADK版の両方で、講座固有の用語の説明、複数用語の比較、確認問題の生成を実行できた。
    両者の主な違いは、エージェントの構築方法とツールの登録方法にある。
    特に、Pydantic AIではツール登録メソッドを使用するのに対し、Google ADKではエージェント作成時にツールをリストで渡す点が異なっていた。
    一方、どちらも既存のPython関数をツールとして利用できるため、機能を再利用しやすいと感じた。
    なお、Google ADK版の今回のCLI出力では個々のツール呼び出しを直接確認していないため、ツール選択の詳細については追加検証が必要である。

# 7. 気づき・疑問
    今回の発展課題を通じて、エージェントの機能とフレームワーク固有の実装を分離する重要性を理解した。
    同じ指示文とツールを使用しても、LLMの回答表現や出題内容には違いが生じることが分かった。
    今後は、同じ質問を複数回実行し、ツール呼び出し回数、トークン使用量、回答の再現性などを比較することで、各フレームワークの特徴をより定量的に評価したい。

# 8. 実際のターミナルのLog
    @KyoshiroK ➜ /workspaces/lecture-ai-engineering-2026 (lec03) $ mkdir -p adk_agent/glossary_agent
    @KyoshiroK ➜ /workspaces/lecture-ai-engineering-2026 (lec03) $ touch adk_agent/glossary_agent/__init__.py
    @KyoshiroK ➜ /workspaces/lecture-ai-engineering-2026 (lec03) $ touch adk_agent/glossary_agent/agent.py
    @KyoshiroK ➜ /workspaces/lecture-ai-engineering-2026 (lec03) $ PYTHONPATH=. uv run --with google-adk \
    adk run adk_agent/glossary_agent
    Installed 48 packages in 5.18s
    Help improve the ADK (CLI and Web UI) by allowing Google to collect pseudonymized usage data?

    What is collected: Names of subcommands and flags (no user-provided values or arguments), execution metrics (duration, exit state), environment specs (OS, Python version), and aggregated Web UI feature interactions. No personally identifiable information (PII) is collected.

    This is OFF by default. You can opt out at any time using the 'adk telemetry disable' command or Web UI user settings.

    Enable telemetry? [Y/n]: n
    Log setup complete: /tmp/agents_log/agent.20261103_112938.log
    To access latest log: tail -F /tmp/agents_log/agent.latest.log
    /home/vscode/.cache/uv/archive-v0/1Zhb-_Be0oYStebI/lib/python3.12/site-packages/google/adk/cli/cli.py:351: UserWarning: [EXPERIMENTAL] InMemoryCredentialService: This feature is experimental and may change or be removed in future versions without notice. It may introduce breaking changes at any time.
    credential_service = InMemoryCredentialService()
    /home/vscode/.cache/uv/archive-v0/1Zhb-_Be0oYStebI/lib/python3.12/site-packages/google/adk/auth/credential_service/in_memory_credential_service.py:33: UserWarning: [EXPERIMENTAL] BaseCredentialService: This feature is experimental and may change or be removed in future versions without notice. It may introduce breaking changes at any time.
    super().__init__()
    Running agent glossary_agent, type exit to exit.
    [user]: LoRAとQLoRAの違いは？
    [glossary_agent]: LoRAとQLoRAの違いは、ベースモデルの重みをそのまま扱うか、量子化して扱うかにあります。

    * **LoRA**: 事前学習済みの重みを固定したまま、重みの更新分を小さな低ランク行列（2つの小さな行列の積）で表し、その部分だけを効率的に学習するPEFT（Parameter-Efficient Fine-Tuning）手法です。学習パラメータや保存ファイルを大幅に削減できます。
    * **QLoRA**: LoRAの仕組みをベースにしつつ、**ベースモデルの重みを4ビットなどに量子化してメモリを大幅に節約した状態**で学習を行う手法です。これにより、より大きなモデルを比較的小さなGPUでも扱えるようになります。

    関係する回：第2回
    [user]: 第2回の内容から確認問題を1問出して
    [glossary_agent]: それでは、第2回の内容から確認問題を出します。

    **【確認問題】**
    「QLoRA」とは、どのような特徴を持つ手法ですか？（LoRAとの違いに触れて説明してください）

    関係する回：第2回
    [user]: AIE2026の講座の宿題にある「3レベル」とは何ですか？
    [glossary_agent]: 用語集を確認したところ、「宿題の3レベル」は以下のように定義されています。

    AIE2026の宿題は、以下の3段階（レベル）で構成されています。

    1. **基礎**：講義内容の確認
    2. **実装**：自分でコードを書く
    3. **発展**：調査や試行を行う

    どれか1つのレベルに取り組めば、その回の宿題は完了となります（原則として採点は行われません）。

    関係する回：第1回
    [user]: exit
