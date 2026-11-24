# 第6回 解答

## 演習
- STEP 1 のツールの名前：glossary_search_glossary
- STEP 2 の [tool call]：[tool call] glossary_search_glossary({'query': '3レベル'})
- STEP 3 の [tool call]：[tool call] fetch_fetch({'url': 'https://modelcontextprotocol.io/'})
- STEP 4 の [tool call]：[tool call] aws_aws___search_documentation({'search_phrase': 'Amazon S3 versioning overview'})
- 気づき・疑問：

    - STEP 1では、通常のエージェントではsearch_materialsが1個表示されたのに対し、MCPエージェントではglossary_search_glossaryが1個表示され、MCPサーバーを介してモデルに見えるツールが変わることを確認できた。
    - STEP 2では、glossary_search_glossaryが実際に呼び出され、「3レベル」を検索した結果をもとに回答が生成された。traceを確認することで、最終回答だけでなく、モデルがどのツールをどの引数で呼び出したかを確認できた。
    - STEP 3では、fetch MCPサーバーを追加すると、モデルに見えるツールが2個になり、fetch_fetchを使ってhttps://modelcontextprotocol.io/の情報を取得できた。ローカルで作成したMCPサーバーだけでなく、公開されているMCPサーバーも同じ設定ファイルから利用できることが分かった。
    - STEP 4では、https://knowledge-mcp.global.api.awsにURLで接続し、aws_aws___search_documentationを使ってAmazon S3のバージョニングに関するドキュメントを検索できた。STEP 3のようにコマンドでMCPサーバーを起動する方法と、STEP 4のようにURLで外部のMCPサーバーへ接続する方法があることが分かった。
    - また、MCPサーバーを追加するとモデルが利用可能なツールが増え、質問内容に応じてモデル自身が適切なツールを選択して呼び出せることが印象的だった。一方で、複数のMCPサーバーに似た機能のツールが存在する場合、モデルがどのような基準で使用するツールを選択するのかが気になった。

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：発展
- やったこと：
    - 自分が利用しているソフトウェアとしてVS Codeを選び、VS CodeでMCPサーバーを設定する方法を公式ドキュメントから調査した。
    - MCPの設定場所、コマンドによるMCPサーバーの起動方法、URLによるリモートMCPサーバーへの接続方法、設定が有効になる範囲を確認した。
    - 調査結果を、演習で使用した`app/mcp_servers.json`の設定方法と比較した。
    - 調査日：2026年11月24日
    - 公式ドキュメント：[VS Code MCP configuration reference](https://code.visualstudio.com/docs/agents/reference/mcp-configuration)
    - 関連する公式ドキュメント：https://code.visualstudio.com/docs/agents/run/manage-mcp-servers
- 結果：
    - VS CodeのCopilot harness向けMCP設定では、複数のワークスペースで個人的に利用する場合は`$COPILOT_HOME/mcp-config.json`、または`~/.copilot/mcp-config.json`を使用する。
    - ワークスペースやチームで設定を共有する場合は、ワークスペース直下の`.mcp.json`を使用する。
    - いずれの設定ファイルも、トップレベルに`mcpServers`を置くportable形式を使用する。
    - コマンドでローカルMCPサーバーを起動する場合は、`type`に`stdio`を指定し、`command`と`args`を設定する。
    - URLでリモートMCPサーバーに接続する場合は、`type`に`http`を指定し、`url`を設定する。
    - 今回の演習で使用した`app/mcp_servers.json`も、トップレベルに`mcpServers`を置き、その下へサーバー名と`command`、`args`、または`url`を記載するため、VS Codeのportable形式と基本構造がよく似ていた。
    - 一方、VS Codeの推奨形式では、`type: "stdio"`または`type: "http"`によって接続方式を明示する点が演習の設定と異なっていた。また、VS Codeでは`tools`、`env`、`headers`なども設定できる。
    - 演習の設定は講義用Pythonエージェントから参照されるのに対し、VS Codeでは設定ファイルの場所によって、ユーザー全体または特定のワークスペースに適用範囲を分けられることが分かった。

- 気づき・疑問：
    - MCPの設定ファイルはソフトウェアによって保存場所や一部の項目が異なるが、サーバー名の下に起動コマンドや接続先URLを記述する基本的な考え方は共通していると分かった。
    - 演習では`command`または`url`だけで接続方式を判断していたが、VS Codeでは`type`によって`stdio`と`http`を明示しており、設定の意図がより分かりやすいと感じた。
    - ワークスペース直下の`.mcp.json`はチームで共有できる一方、コマンドを実行するためのランタイムや認証情報は各実行環境に別途必要であり、設定ファイルを共有するだけでは同じ環境を完全には再現できないことが分かった。
    - CodespacesやDev Containerなどのリモート環境では、ローカルPCではなく、MCPサーバーを実際に実行するリモート側にコマンドや依存パッケージを用意する必要がある点に注意したい。
    - 今後、同じMCPサーバーをユーザー設定とワークスペース設定の両方に登録した場合、どちらが優先されるのか、またツール名が重複した場合にモデルがどのように選択するのかを確認したい。
