# Yomitoku Searchable PDF Improvement - Furigana Filtering for Screen Readers

## 概要 (Overview)

このプロジェクトでは、yomitokuの`searchable_pdf.py`を改善し、日本語のフリガナ（ルビ）をスクリーンリーダーから除外する機能を実装しました。

### 問題点 (Problem)

yomitokuの元の実装では、OCRで検出されたすべてのテキスト（フリガナと基本テキスト）が透明テキストレイヤーに配置されます。その結果：

- スクリーンリーダーがフリガナと基本テキストの**両方**を読み上げる
- 例：「完璧」→「かんぺき」→「完璧」のように二重に読まれる
- 視覚障害者にとって非常に聞き取りにくい

### 解決策 (Solution)

改善版では、フリガナを自動検出し、透明テキストレイヤーから除外します：

- **視覚レイヤー**：元の画像にフリガナと基本テキストが表示される
- **音声レイヤー**（スクリーンリーダー用）：基本テキストのみが含まれる
- 結果：スクリーンリーダーは「完璧」を「かんぺき」と一度だけ読み上げる

## 実装の詳細 (Implementation Details)

### 追加された機能

#### 1. `_is_kana_only(text)` 関数

文字列がひらがな、カタカナ、日本語句読点のみで構成されているかチェックします。

```python
def _is_kana_only(text):
    """
    Check if text contains only hiragana, katakana, and Japanese punctuation.
    Returns True if the text is likely furigana.
    """
    kana_pattern = re.compile(r'^[\u3040-\u309F\u30A0-\u30FF\u3001-\u303F\s]+$')
    return bool(kana_pattern.match(text))
```

#### 2. `_is_furigana(text, font_size, bbox_height, bbox_width)` 関数

複数の基準でフリガナを判定します：

1. **フォントサイズ**：8pt未満
2. **文字種別**：かな文字のみ
3. **バウンディングボックス**：高さまたは幅が12px未満

```python
def _is_furigana(text, font_size, bbox_height, bbox_width):
    """
    Determine if a text element is furigana based on multiple criteria.
    """
    if font_size >= 8:
        return False
    
    if not _is_kana_only(text):
        return False
    
    if bbox_height < 12 or bbox_width < 12:
        return True
    
    return False
```

#### 3. `create_searchable_pdf()` 関数の修正

フリガナを検出した場合、透明テキストレイヤーに追加せずにスキップします：

```python
# Skip furigana from the accessible text layer
# Furigana will remain visible in the image layer but won't be read by screen readers
if _is_furigana(text, font_size, bbox_height, bbox_width):
    continue
```

### 変更されたファイル

- **`yomitoku_repo/src/yomitoku/utils/searchable_pdf.py`**
  - `import re` を追加
  - `_is_kana_only()` 関数を追加
  - `_is_furigana()` 関数を追加
  - `create_searchable_pdf()` 内でフリガナをスキップする処理を追加

## 使用方法 (Usage)

### 通常のyomitoku使用方法

改善版は既存のyomitoku APIと完全に互換性があります：

```python
from yomitoku import DocumentAnalyzer

analyzer = DocumentAnalyzer(configs={}, device="cpu")
results, ocr_vis = analyzer("path/to/image.jpg")

# Generate searchable PDF with furigana filtering
from yomitoku.utils.searchable_pdf import create_searchable_pdf
import cv2

image = cv2.imread("path/to/image.jpg")
create_searchable_pdf(
    images=[image],
    ocr_results=[results],
    output_path="output.pdf"
)
```

### CLIからの使用

```bash
yomitoku path/to/image.jpg --format pdf --output output.pdf
```

生成されたPDFは自動的にフリガナフィルタリングが適用されます。

## テスト方法 (Testing)

### 1. PDFを生成

yomitokuを使用して日本語文書（フリガナ付き）からPDFを生成します。

### 2. スクリーンリーダーでテスト

生成されたPDFをスクリーンリーダーで開いて確認：

- **Windows**: NVDA、JAWS
- **macOS**: VoiceOver
- **Linux**: Orca

### 3. 期待される動作

- ✅ スクリーンリーダーが基本テキスト（漢字など）のみを読み上げる
- ✅ フリガナは視覚的に表示されるが、読み上げられない
- ✅ 「完璧」は「かんぺき」と一度だけ読まれる（「かんぺき」→「完璧」ではない）

## 技術的背景 (Technical Background)

### PDFの構造

改善版のPDFには2つのレイヤーがあります：

1. **視覚レイヤー（画像）**
   - 元の画像が描画される
   - フリガナと基本テキストが両方表示される
   - ユーザーが目で見る内容

2. **音声レイヤー（透明テキスト）**
   - 基本テキストのみが透明で配置される
   - スクリーンリーダーが読み上げる内容
   - フリガナは含まれない

### フリガナ検出アルゴリズム

フリガナの特徴を利用して自動検出：

| 特徴 | フリガナ | 基本テキスト |
|------|---------|------------|
| フォントサイズ | < 8pt | ≥ 8pt |
| 文字種別 | かな文字のみ | 漢字を含む |
| バウンディングボックス | 小さい (< 12px) | 大きい (≥ 12px) |

## 対応状況 (Compatibility)

- ✅ 縦書きテキスト対応
- ✅ 横書きテキスト対応
- ✅ 既存のyomitoku API完全互換
- ✅ CLIツール対応

## 今後の改善案 (Future Improvements)

1. **機械学習ベースの検出**：フォントサイズとバウンディングボックスだけでなく、位置関係も考慮
2. **設定可能な閾値**：フォントサイズやバウンディングボックスの閾値をユーザーが調整可能に
3. **ルビタグサポート**：HTMLやEPUBでの正式なルビタグ生成

## ライセンス (License)

この改善は、yomitokuの元のライセンス（CC BY-NC-SA 4.0）に従います。

## 貢献者 (Contributors)

- Original yomitoku: Kotaro Kinoshita
- Furigana filtering improvement: Replit Agent

## 参考資料 (References)

- [yomitoku GitHub](https://github.com/Utakata/yomitoku)
- [ReportLab Documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [PDF Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/)
