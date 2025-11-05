# サーチャブルEPUB変換ツール

画像ベースのEPUB（固定レイアウト）を、検索とコピー＆ペーストが可能なサーチャブルEPUBに変換するPythonツールです。

## 特徴

- ✅ **元のレイアウトを完全に保持**: 画像の見た目はそのまま維持
- ✅ **透明テキストレイヤー**: OCRで取得したテキストを透明で正確に配置
- ✅ **縦書き・横書き対応**: 日本語の縦書きテキストにも対応
- ✅ **yomitoku統合**: 高精度なOCRエンジンを使用
- ✅ **固定レイアウト**: リフロー型に変換せず、元のEPUB構造を維持

## 技術仕様

### アーキテクチャ

```
入力EPUB (画像のみ) → OCR処理 → 透明テキストレイヤー追加 → 出力EPUB (検索可能)
```

### 使用技術

- **OCRエンジン**: yomitoku (DocumentAnalyzer)
- **テキスト処理**: reportlab (フォントサイズ計算)
- **EPUB処理**: lxml (HTML/XML解析), zipfile
- **画像処理**: Pillow

### yomitoku searchable_pdf.py からの応用

このツールは、yomitokuの既存機能 `src/yomitoku/utils/searchable_pdf.py` のロジックを応用しています：

- `_poly2rect()`: 座標の矩形化
- `to_full_width()`: 縦書き用の全角変換
- `_calc_font_size()`: bbox に収まるフォントサイズ計算
- 透明化処理: PDFの `alpha=0` → HTMLの `color: transparent`

## インストール

```bash
pip install -r requirements.txt
```

## 使い方

### コマンドライン

```bash
python src/epub_searchable/main.py input.epub output.epub
```

### Streamlitアプリ

```bash
streamlit run app.py
```

ブラウザでEPUBファイルをアップロードして変換できます。

## プロジェクト構造

```
.
├── src/
│   └── epub_searchable/
│       ├── __init__.py
│       ├── utils.py           # 共通ユーティリティ関数
│       ├── epub_handler.py    # EPUB展開・再圧縮
│       ├── ocr_processor.py   # yomitoku OCR処理
│       ├── html_processor.py  # HTMLテキストレイヤー生成
│       └── main.py            # メインスクリプト
├── app.py                     # Streamlitアプリ
├── requirements.txt
└── README.md
```

## 処理フロー

1. **EPUB展開**: 入力EPUBをZIPとして展開
2. **HTMLファイル走査**: `.html` / `.xhtml` ファイルを検出
3. **画像参照取得**: `<img>` や `<svg><image>` から画像パスを取得
4. **OCR処理**: yomitokuで画像を解析し、`results.words` を取得
5. **テキストレイヤー生成**: 
   - 元の画像を背景レイヤーとして配置
   - OCR結果を透明な `<span>` タグで絶対座標に配置
   - 縦書き対応 (`writing-mode: vertical-rl`)
6. **EPUB再圧縮**: 処理済HTMLをEPUBとして再圧縮

## 出力HTML構造

```html
<body>
  <!-- 背景レイヤー: 元の画像 -->
  <img src="../images/00002.jpeg" style="position: absolute; top: 0; left: 0;">
  
  <!-- テキストレイヤー: 透明なOCRテキスト -->
  <div style="position: relative; color: transparent;">
    <span style="position: absolute; left: 100px; top: 200px; font-size: 16px;">
      完璧
    </span>
    <!-- ... 他のテキスト要素 ... -->
  </div>
</body>
```

## ライセンス

CC BY-NC-SA 4.0 (yomitokuのライセンスに準拠)

## 関連プロジェクト

- [yomitoku](https://github.com/Utakata/yomitoku) - 日本語OCRエンジン
