# サーチャブルEPUB変換ツール

## プロジェクトの目的

画像ベースのEPUBを、検索とコピー&ペーストが可能な**サーチャブルEPUB（固定レイアウト）**に変換するPythonツールです。yomitokuの`searchable_pdf.py`のロジックを活用し、透明なテキストレイヤーをEPUBに追加します。

### 関連プロジェクト

このプロジェクトは、yomitokuの`searchable_pdf.py`改善（フリガナフィルタリング機能）の成果を活用しています。

## 特徴

### 主要機能
- ✅ **元のレイアウトを完全に保持**: 画像の見た目はそのまま維持
- ✅ **透明テキストレイヤー**: OCRで取得したテキストを透明で正確に配置
- ✅ **縦書き・横書き対応**: 日本語の縦書きテキストにも対応
- ✅ **高精度OCR**: yomitoku DocumentAnalyzerを使用
- ✅ **フリガナフィルタリング**: スクリーンリーダーがフリガナを読まない

### EPUBの構造
- **背景レイヤー**: 元の画像が表示される
- **テキストレイヤー**: OCRテキストが透明（`color: transparent`）で絶対座標に配置される
- **固定レイアウト**: リフロー型に変換せず、元のレイアウトを維持

## 実装の詳細

### プロジェクト構造

```
.
├── src/
│   └── epub_searchable/
│       ├── __init__.py
│       ├── utils.py           # 共通ユーティリティ（yomitoku searchable_pdf.pyから移植）
│       ├── epub_handler.py    # EPUB展開・再圧縮（ZIP処理）
│       ├── ocr_processor.py   # yomitoku DocumentAnalyzer統合
│       ├── html_processor.py  # HTMLテキストレイヤー生成
│       └── main.py            # メインスクリプト
├── app.py                     # Streamlitアプリ
├── requirements.txt
└── README.md
```

### 主要モジュール

1. **`utils.py`**: yomitokuの`searchable_pdf.py`から移植
   - `_poly2rect()`: 座標の矩形化
   - `to_full_width()`: 縦書き用の全角変換
   - `_calc_font_size()`: フォントサイズ計算
   - `_is_furigana()`: フリガナ判定

2. **`epub_handler.py`**: EPUB処理
   - EPUB展開（ZIPファイルとして）
   - HTMLファイル検出
   - EPUB再圧縮（mimetypeを最初に非圧縮で追加）

3. **`ocr_processor.py`**: OCR処理
   - yomitoku DocumentAnalyzerでOCR実行
   - `results.words`（テキスト、座標、方向）を取得

4. **`html_processor.py`**: HTML生成
   - 元のHTMLから画像参照を抽出
   - 背景レイヤー（元の画像）を配置
   - テキストレイヤー（透明な`<span>`）を絶対座標に配置
   - 縦書き対応（`writing-mode: vertical-rl`）

## 処理フロー

1. **EPUB展開**: 入力EPUBをZIPとして展開
2. **HTMLファイル走査**: `.html` / `.xhtml` ファイルを検出
3. **画像参照取得**: `<img>` や `<svg><image>` から画像パスを取得
4. **OCR処理**: yomitokuで画像を解析し、`results.words` を取得
5. **テキストレイヤー生成**:
   - 元の画像を背景レイヤーとして配置
   - OCR結果を透明な `<span>` タグで絶対座標に配置
   - 縦書き対応 (`writing-mode: vertical-rl`)
   - フリガナフィルタリング適用
6. **EPUB再圧縮**: 処理済HTMLをEPUBとして再圧縮

## 技術的背景

### 生成されるHTML構造

```html
<body>
  <!-- 背景レイヤー: 元の画像 -->
  <div class="background-layer">
    <img src="../images/00002.jpeg" width="1395" height="2048" alt="Page image"/>
  </div>
  
  <!-- テキストレイヤー: 透明なOCRテキスト -->
  <div class="text-layer" style="width: 1395px; height: 2048px; color: transparent;">
    <span style="position: absolute; left: 100px; top: 200px; font-size: 16px;">
      完璧
    </span>
    <span style="position: absolute; left: 120px; top: 180px; font-size: 6px; writing-mode: vertical-rl;">
      かんぺき
    </span>
    <!-- フリガナは検出されて除外される -->
  </div>
</body>
```

### フリガナフィルタリング

yomitokuの改善版searchable_pdf.pyのロジックを使用：

| 特徴 | フリガナ | 基本テキスト |
|------|---------|------------|
| フォントサイズ | < 8pt | ≥ 8pt |
| 文字種別 | かな文字のみ | 漢字を含む |
| バウンディングボックス | 小さい (< 12px) | 大きい (≥ 12px) |

→ フリガナを検出し、HTMLテキストレイヤーから除外

## ファイル構成

```
/
├── src/
│   └── epub_searchable/       # メインモジュール
├── yomitoku_repo/
│   └── src/yomitoku/utils/
│       └── searchable_pdf.py  # 改善版（フリガナフィルタリング機能付き）
├── app.py                     # Streamlitアプリ
├── requirements.txt
├── README.md
├── YOMITOKU_IMPROVEMENT.md    # yomitoku改善の詳細ドキュメント
└── replit.md                  # このファイル
```

## 使用方法

### Streamlitアプリ（推奨）

```bash
streamlit run app.py
```

1. EPUBファイルをアップロード
2. 「変換開始」ボタンをクリック
3. サーチャブルEPUBをダウンロード

### コマンドライン

```bash
python -m src.epub_searchable.main input.epub output.epub [font.ttf]
```

### Pythonスクリプト

```python
from src.epub_searchable.main import convert_epub_to_searchable

convert_epub_to_searchable(
    input_epub="input.epub",
    output_epub="output_searchable.epub",
    font_path=None  # Optional: path to .ttf font
)
```

## テスト方法

### 入力EPUB要件
- 画像ベースのEPUB（固定レイアウト）
- HTMLファイルが`<img>`または`<svg><image>`で画像を参照
- 画像ファイルが`images/`フォルダに存在

### 検証方法
1. 画像ベースのEPUBを変換
2. 出力EPUBをEPUBリーダーで開く
3. テキスト検索が機能することを確認
4. テキストをコピー&ペーストできることを確認
5. スクリーンリーダーで開いて音声読み上げを確認

## 対応状況
- ✅ 縦書きテキスト対応
- ✅ 横書きテキスト対応
- ✅ フリガナフィルタリング
- ✅ EPUB固定レイアウト維持
- ✅ Streamlit Webアプリ
- ✅ CLIツール対応

## 最新の変更履歴
- 2025-11-05: サーチャブルEPUB変換ツールを実装
- 2025-11-05: yomitokuのsearchable_pdf.pyロジックをEPUBに応用
- 2025-11-05: Streamlit Webアプリを作成
- 2025-11-05: フリガナフィルタリング機能を統合
- 2025-11-04: yomitoku searchable_pdf.pyにフリガナフィルタリング機能を実装（完了）

## 依存関係

- yomitoku (OCRエンジン)
- pillow (画像処理)
- reportlab (フォントサイズ計算)
- numpy (数値計算)
- jaconv (全角変換)
- lxml (HTML/XML解析)
- streamlit (Webアプリ)

## ライセンス
CC BY-NC-SA 4.0（yomitokuのライセンスに準拠）

## 参考資料
- [yomitoku GitHub](https://github.com/Utakata/yomitoku)
- [YOMITOKU_IMPROVEMENT.md](./YOMITOKU_IMPROVEMENT.md) - yomitoku改善の詳細ドキュメント
- [README.md](./README.md) - サーチャブルEPUB変換ツールの詳細
