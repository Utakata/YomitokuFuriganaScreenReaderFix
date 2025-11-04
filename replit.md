# Yomitoku Searchable PDF Improvement - Furigana Filtering

## プロジェクトの目的

yomitokuの`searchable_pdf.py`を改善し、日本語のフリガナ（ルビ）をスクリーンリーダーから除外する機能を実装しました。

## 問題点と解決策

### 元の問題
yomitokuの元の実装では、OCRで検出されたすべてのテキスト（フリガナと基本テキスト）が透明テキストレイヤーに配置されるため、スクリーンリーダーがフリガナと基本テキストの**両方**を読み上げてしまいます。

例：「完璧」→「かんぺき」→「完璧」のように二重に読まれる

### 実装した解決策
フリガナを自動検出し、透明テキストレイヤーから除外：
- **視覚レイヤー**：元の画像にフリガナと基本テキストが表示される
- **音声レイヤー**（スクリーンリーダー用）：基本テキストのみが含まれる
- 結果：スクリーンリーダーは「完璧」を「かんぺき」と一度だけ読み上げる

## 実装の詳細

### 変更されたファイル
`yomitoku_repo/src/yomitoku/utils/searchable_pdf.py`

### 追加された機能

1. **`_is_kana_only(text)`**: ひらがな・カタカナのみで構成されているかチェック
2. **`_is_furigana(text, font_size, bbox_height, bbox_width)`**: 複数の基準でフリガナを判定
   - フォントサイズ < 8pt
   - かな文字のみ
   - バウンディングボックス < 12px
3. **`create_searchable_pdf()`の修正**: フリガナを検出した場合、透明テキストレイヤーから除外

## アーキテクチャレビュー結果

Architect Agent による評価：**Pass** ✅

### 主要な発見
- フリガナ検出ロジックが正しく動作
- 既存コードとの統合が適切
- 視覚レイヤーを保持しながらスクリーンリーダーレイヤーからフリガナを除外
- 基本テキストが誤って除外されることはない

### 将来の改善提案
1. 閾値を設定可能にする
2. 回帰テストを追加
3. 位置ベースのチェックで精度向上

## 技術的背景

### PDFの構造
1. **視覚レイヤー（画像）**: 元の画像が描画され、フリガナと基本テキストが両方表示される
2. **音声レイヤー（透明テキスト）**: 基本テキストのみが透明で配置され、スクリーンリーダーが読み上げる

### フリガナ検出アルゴリズム
| 特徴 | フリガナ | 基本テキスト |
|------|---------|------------|
| フォントサイズ | < 8pt | ≥ 8pt |
| 文字種別 | かな文字のみ | 漢字を含む |
| バウンディングボックス | 小さい (< 12px) | 大きい (≥ 12px) |

## ファイル構成

```
/
├── yomitoku_repo/
│   └── src/yomitoku/utils/
│       └── searchable_pdf.py  # 改善版（フリガナフィルタリング機能付き）
├── YOMITOKU_IMPROVEMENT.md    # 詳細ドキュメント（日英）
└── replit.md                  # このファイル
```

## 使用方法

改善版は既存のyomitoku APIと完全に互換性があります：

```python
from yomitoku import DocumentAnalyzer
from yomitoku.utils.searchable_pdf import create_searchable_pdf
import cv2

analyzer = DocumentAnalyzer(configs={}, device="cpu")
results, ocr_vis = analyzer("path/to/image.jpg")

image = cv2.imread("path/to/image.jpg")
create_searchable_pdf(
    images=[image],
    ocr_results=[results],
    output_path="output.pdf"
)
```

または、CLIから：

```bash
yomitoku path/to/image.jpg --format pdf --output output.pdf
```

## テスト方法

1. yomitokuを使用して日本語文書（フリガナ付き）からPDFを生成
2. スクリーンリーダー（NVDA、JAWS、VoiceOverなど）で開いて確認
3. 期待される動作：
   - ✅ スクリーンリーダーが基本テキスト（漢字など）のみを読み上げる
   - ✅ フリガナは視覚的に表示されるが、読み上げられない
   - ✅ 「完璧」は「かんぺき」と一度だけ読まれる

## 対応状況
- ✅ 縦書きテキスト対応
- ✅ 横書きテキスト対応
- ✅ 既存のyomitoku API完全互換
- ✅ CLIツール対応

## 最新の変更履歴
- 2025-11-04: yomitoku searchable_pdf.pyにフリガナフィルタリング機能を実装
- 2025-11-04: フリガナ検出アルゴリズム（`_is_kana_only`, `_is_furigana`）を追加
- 2025-11-04: Architect Agentによるコードレビュー完了（Pass）
- 2025-11-04: 詳細ドキュメント（YOMITOKU_IMPROVEMENT.md）を作成

## ライセンス
この改善は、yomitokuの元のライセンス（CC BY-NC-SA 4.0）に従います。

## 参考資料
- [yomitoku GitHub](https://github.com/Utakata/yomitoku)
- [YOMITOKU_IMPROVEMENT.md](./YOMITOKU_IMPROVEMENT.md) - 詳細ドキュメント
