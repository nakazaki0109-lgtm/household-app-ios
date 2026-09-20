# 決まった処理はスクリプトに任せる

## 原則

同じ決定的な処理を、スキルが発火するたびにモデルへプローズの手順として毎回考え直させると、トークンを無駄に使ううえに再現性も落ちる。ファイル生成、番号採番、集計、フォーマット変換、検証など「入力が同じなら出力も同じ」になる処理は、SKILL.md に手順を書くのではなく `scripts/` にスクリプトとして入れ、SKILL.md からはその実行コマンドだけを示す。

判断の目安:

- **スクリプトに任せる**: 手順が毎回同じ、入出力が機械的に決まる、人間の主観的判断が要らない（例: ディレクトリの雛形作成、ADRの連番採番、JSONの集計、フォーマットのバリデーション）
- **モデルに任せる**: ユーザーの自然文の意図を読む、主観的な良し悪しを判断する、一度きりで二度と起きない作業

## 置き場所と言語

`scripts/` をスキル直下に置く。

- **Bash**: ファイル操作やコマンドの組み合わせなど、シェルで完結する軽い処理
- **Python**: JSONやデータ構造を扱う処理、パース、計算など。かつ単体テストの書きやすさの面でも基本はPythonを優先する

SKILL.md からは実行コマンドを示すだけにし、スクリプトの中身の説明はSKILL.mdに書かない。スクリプト自体とそのテストが実装のドキュメントを兼ねる。

```markdown
## 雛形を作る

`python scripts/scaffold_skill.py <parent_dir> <name> --with-scripts` を実行する。
```

## 単体テストを書く

`scripts/` に入れたスクリプトには、`scripts/tests/` に pytest のユニットテストを書く。

- テスト対象は「純粋なロジック」を優先する。ファイルI/Oが絡む部分は `tmp_path` フィクスチャなどで隔離し、実際のファイルシステムやネットワークに依存しない形にする
- CLIのエントリポイント（`main()` / `argparse`）と、テストしたいロジック本体（`scaffold_skill()` のような関数）を分離する。CLI関数は薄いラッパーにし、ロジック本体を直接importしてテストできるようにする
- 異常系（不正な入力、既に存在するファイルなど）も最低1ケースはテストする

ディレクトリ構成:

```
skill-name/
└── scripts/
    ├── __init__.py
    ├── my_script.py
    └── tests/
        ├── __init__.py
        └── test_my_script.py
```

`__init__.py` を置くことで、テストファイル側から `from scripts.my_script import ...` の形でパッケージとしてimportできる。テストはスキルのルートディレクトリから実行する:

```bash
cd skill-name
python -m pytest scripts/tests
```

pytestが未導入の環境では `pip install pytest`（または `pip3 install --user pytest`）が必要になる旨をユーザーに伝える。

## 具体例

このスキル自身の `scripts/scaffold_skill.py` と `scripts/tests/test_scaffold_skill.py` が実例になっている。新しいスキルの雛形作成という決定的な処理をスクリプトに任せ、ロジック本体 (`scaffold_skill()`, `validate_name()`, `slug_to_title()`) を関数として切り出してテストしている。
