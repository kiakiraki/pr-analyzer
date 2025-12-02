# PR Analyzer

GitHub プルリクエストの統計情報と生産性指標を分析し、チームパフォーマンスを可視化するツールです。

## 機能

- 📊 `gh` CLI を使用して GitHub リポジトリから PR データを取得
- 🏷️ ラベルによる PR のフィルタリング（複数ラベルの除外も可能、dependencies はデフォルトで除外）
- 📈 月次統計を計算（マージされた PR 数、マージまでの時間、1人あたりの PR 数）
- 📉 生産性トレンドの可視化
- 🔍 PR サイズの分析と可視化（変更行数、変更ファイル数の推移と分布）
- 🎯 完全な分析パイプラインをワンコマンドで実行

## 必要要件

- Python 3.12+
- uv（Python パッケージマネージャー）
- GitHub CLI (`gh`) のインストールと認証
- 必要な Python パッケージ（自動インストール）:
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - click
  - scipy

### uv のインストール

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Homebrew:**
```bash
brew install uv
```

その他のインストール方法については、[uv 公式ドキュメント](https://docs.astral.sh/uv/getting-started/installation/)を参照してください。

### GitHub CLI のインストール

**macOS:**
```bash
brew install gh
```

**Ubuntu/Debian:**
```bash
sudo apt install gh
```

**Windows:**
```bash
winget install --id GitHub.cli
```

**GitHub で認証:**
```bash
gh auth login
```

その他のプラットフォームについては、[GitHub CLI インストールガイド](https://github.com/cli/cli#installation)を参照してください。


## 使い方

### クイックスタート（GitHub URLから直接実行）

インストール不要で、GitHubから直接実行できます:

```bash
# 完全なパイプラインを実行: 取得 + 分析 + 可視化
uvx --from git+https://github.com/kiakiraki/pr-analyzer pr-analyze run \
  --repo owner/repo \
  --output-dir ./results

# ラベルを指定する場合
uvx --from git+https://github.com/kiakiraki/pr-analyzer pr-analyze run \
  --repo owner/repo \
  --label bug \
  --output-dir ./results

# 特定のラベルを除外する場合
uvx --from git+https://github.com/kiakiraki/pr-analyzer pr-analyze run \
  --repo owner/repo \
  --exclude-label "auto-generated" \
  --exclude-label "dependencies" \
  --output-dir ./results

# 期間を指定する場合（2023年1月1日から2024年12月31日まで）
uvx --from git+https://github.com/kiakiraki/pr-analyzer pr-analyze run \
  --repo owner/repo \
  --cutoff-date 2023-01-01 \
  --end-date 2024-12-31 \
  --output-dir ./results
```

### ローカルでの実行

リポジトリをクローンして実行する場合:

```bash
# リポジトリをクローン
git clone https://github.com/kiakiraki/pr-analyzer.git
cd pr-analyzer

# 実行
uv run pr-analyze run \
  --repo owner/repo \
  --output-dir ./results
```

実行内容:
1. GitHub から PR データを取得
2. データを処理・分析
3. 統計情報を生成（CSV/JSON）
4. 可視化チャートを作成

**オプション:**
- `--repo`: GitHub リポジトリ（"owner/repo" 形式、必須）
- `--label`: PR をフィルタするラベル（オプション）
- `--exclude-label`: 除外するラベル（複数回指定可能、デフォルト: dependencies）
- `--output-dir`, `-o`: 出力ディレクトリ（デフォルト: カレントディレクトリ）
- `--cutoff-date`: この日付以降に作成された PR のみ分析（YYYY-MM-DD 形式、オプション）
- `--end-date`: この日付以前に作成された PR のみ分析（YYYY-MM-DD 形式、オプション）
- `--limit`: 取得する PR の最大数（デフォルト: 10000）
- `--state`: 取得する PR の状態 - all, merged, open, closed（デフォルト: merged）
- `--timeout`: コマンドタイムアウト秒数（デフォルト: 600）

### ステップごとのコマンド

ステップごとに実行する場合も、GitHub URLから直接実行できます。

#### 1. PR データを取得

**GitHub URLから直接実行:**
```bash
# ラベルを指定して取得
uvx --from git+https://github.com/kiakiraki/pr-analyzer pr-analyze fetch \
  --repo owner/repo \
  --label bug \
  --output pr_data_with_diff.json

# すべての PR を取得（ラベル指定なし）
uvx --from git+https://github.com/kiakiraki/pr-analyzer pr-analyze fetch \
  --repo owner/repo \
  --output pr_data_with_diff.json
```

**ローカルで実行:**
```bash
# ラベルを指定して取得
uv run pr-analyze fetch \
  --repo owner/repo \
  --label bug \
  --output pr_data_with_diff.json

# すべての PR を取得（ラベル指定なし）
uv run pr-analyze fetch \
  --repo owner/repo \
  --output pr_data_with_diff.json
```

**オプション:**
- `--repo`: GitHub リポジトリ（"owner/repo" 形式、必須）
- `--label`: PR をフィルタするラベル（オプション、指定しない場合はすべての PR を取得）
- `--exclude-label`: 除外するラベル（複数回指定可能、デフォルト: dependencies）
- `--output`, `-o`: 出力 JSON ファイル（デフォルト: `pr_data_with_diff.json`）
- `--no-diff`: 差分統計（追加/削除行数）をスキップ
- `--limit`: 取得する PR の最大数（デフォルト: 10000）
- `--state`: 取得する PR の状態 - all, merged, open, closed（デフォルト: merged）
- `--timeout`: コマンドタイムアウト秒数（デフォルト: 600）

#### 2. データを分析

**GitHub URLから直接実行:**
```bash
uvx --from git+https://github.com/kiakiraki/pr-analyzer pr-analyze analyze \
  --input pr_data_with_diff.json \
  --output-dir ./results
```

**ローカルで実行:**
```bash
uv run pr-analyze analyze \
  --input pr_data_with_diff.json \
  --output-dir ./results
```

**オプション:**
- `--input`, `-i`: PR データの入力 JSON ファイル（必須）
- `--output-dir`, `-o`: 出力ファイル用ディレクトリ（デフォルト: カレントディレクトリ）
- `--cutoff-date`: この日付以降に作成された PR のみ分析（YYYY-MM-DD 形式、オプション）
- `--end-date`: この日付以前に作成された PR のみ分析（YYYY-MM-DD 形式、オプション）

#### 3. 可視化を生成

**GitHub URLから直接実行:**
```bash
uvx --from git+https://github.com/kiakiraki/pr-analyzer pr-analyze visualize \
  --input results/monthly_statistics.json \
  --output-dir ./results
```

**ローカルで実行:**
```bash
uv run pr-analyze visualize \
  --input results/monthly_statistics.json \
  --output-dir ./results
```

**オプション:**
- `--input`, `-i`: 月次統計 JSON ファイル（必須）
- `--output-dir`, `-o`: チャート出力ディレクトリ（デフォルト: カレントディレクトリ）
- `--repo`: グラフタイトルに表示するリポジトリ名（オプション）

## 出力ファイル

このツールは以下のファイルを生成します:

### データファイル
- `pr_data_with_diff.json` - GitHub からの生 PR データ
- `monthly_statistics.csv` - 月次集計統計
- `monthly_statistics.json` - 月次統計の JSON 形式
- `pr_details.csv` - PR の詳細情報
- `pr_details.json` - PR 詳細データの JSON 形式

**`monthly_statistics.csv` の例:**
```csv
month,merged_pr_count,avg_time_to_merge_days,unique_authors,prs_per_person
2024-01,12,1.5,4,3.0
2024-02,15,1.2,5,3.0
2024-03,18,0.9,6,3.0
...
```

**`pr_details.csv` の例（一部カラム）:**
```csv
number,title,author,created_at,merged_at,time_to_merge_days,additions,deletions,commits
1234,Add feature X,user1,2024-01-15,2024-01-16,1.2,120,45,3
1235,Fix bug Y,user2,2024-01-16,2024-01-17,0.8,25,10,1
...
```

### 可視化ファイル
- `pr_analysis_overview.png` - 6つの主要指標を含む概要ダッシュボード
  - マージされた PR 数（トレンドライン付き月次推移）
  - 平均マージ時間（日数）
  - 月次の中央値総変更行数（追加+削除）
  - ユニークな著者数
  - 1人あたりの PR 数（生産性指標）
  - 月次の中央値変更ファイル数

## 主要指標

- **マージされた PR 数** - 月ごとのマージされた PR の数
- **マージまでの時間** - PR 作成からマージまでの平均日数
- **1人あたりの PR 数** - ユニークな著者あたりの平均 PR 数（生産性指標）
- **ユニークな著者数** - 月ごとの貢献者数
- **中央値変更行数** - 月次の中央値総変更行数（追加+削除）
- **中央値変更ファイル数** - 月次の中央値変更ファイル数

## プロジェクト構造

```
pr-analyzer/
├── src/
│   └── pr_analyzer/
│       ├── __init__.py
│       ├── cli.py          # コマンドラインインターフェース
│       ├── fetcher.py      # GitHub からの PR データ取得とフィルタリング
│       ├── analyzer.py     # 統計分析
│       └── visualizer.py   # グラフ生成
├── pyproject.toml          # パッケージ設定
└── README.md
```

## トラブルシューティング

### タイムアウトエラー

大量の PR を取得する際にタイムアウトが発生する場合の対策:

**GitHub URLから直接実行:**
```bash
# 1. タイムアウト時間を延長（秒単位、デフォルト: 600）
uvx --from git+https://github.com/kiakiraki/pr-analyzer pr-analyze run \
  --repo owner/repo \
  --timeout 1200 \
  --output-dir ./results

# 2. limit を調整（デフォルト: 10000）
uvx --from git+https://github.com/kiakiraki/pr-analyzer pr-analyze run \
  --repo owner/repo \
  --limit 20000 \
  --timeout 1200 \
  --output-dir ./results
```

**ローカルで実行:**
```bash
# タイムアウト時間を延長
uv run pr-analyze run \
  --repo owner/repo \
  --timeout 1200 \
  --output-dir ./results

# limit を調整
uv run pr-analyze run \
  --repo owner/repo \
  --limit 20000 \
  --timeout 1200 \
  --output-dir ./results
```

### GitHub CLI 認証

データ取得時に認証エラーが発生した場合:

```bash
# 認証ステータスを確認
gh auth status

# 必要に応じてログイン
gh auth login
```

### リポジトリアクセスの確認

リポジトリとラベルにアクセスできることをテスト:

```bash
# リポジトリの PR 一覧を取得できるか確認
gh pr list --repo owner/repo --limit 5

# 特定のラベルで絞り込めるか確認
gh pr list --repo owner/repo --label bug --limit 5
```

### uvx のキャッシュ削除

GitHub URLから実行する際に古いバージョンがキャッシュされている場合、キャッシュをクリアする:

```bash
# キャッシュを削除
uv cache clean

# 再度実行（新しいバージョンが読み込まれる）
uvx --from git+https://github.com/kiakiraki/pr-analyzer pr-analyze run \
  --repo owner/repo \
  --output-dir ./results
```

## ライセンス

MIT License
