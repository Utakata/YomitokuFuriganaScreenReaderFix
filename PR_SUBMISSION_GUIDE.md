# yomitoku プルリクエスト作成ガイド

## 変更内容の概要

以下のファイルを変更しました：

### 変更されたファイル
- `yomitoku_repo/src/yomitoku/utils/searchable_pdf.py`

### 追加された機能
1. `_is_kana_only(text)` - かな文字のみチェック関数
2. `_is_furigana(text, font_size, bbox_height, bbox_width)` - フリガナ判定関数
3. `create_searchable_pdf()` 内でフリガナを除外する処理

## プルリクエストの作成手順

### ステップ 1: yomitokuリポジトリをフォーク

1. https://github.com/Utakata/yomitoku にアクセス
2. 右上の「Fork」ボタンをクリック
3. 自分のGitHubアカウントにフォークを作成

### ステップ 2: ローカルで変更を適用

#### オプションA: Replitから直接コピー

現在のReplit環境で変更済みのファイルをダウンロード：

```bash
# Replitのファイルブラウザから以下をダウンロード
yomitoku_repo/src/yomitoku/utils/searchable_pdf.py
```

#### オプションB: ローカル環境で作業

```bash
# 1. フォークしたリポジトリをクローン
git clone https://github.com/YOUR_USERNAME/yomitoku.git
cd yomitoku

# 2. 新しいブランチを作成
git checkout -b feature/furigana-screen-reader-filter

# 3. Replitからダウンロードしたファイルで上書き
# または、以下の変更を手動で適用
```

### ステップ 3: 変更をコミット

```bash
# 変更を確認
git diff src/yomitoku/utils/searchable_pdf.py

# ステージング
git add src/yomitoku/utils/searchable_pdf.py

# コミット
git commit -m "feat: Add furigana filtering for screen reader accessibility

- Add _is_kana_only() function to detect kana-only text
- Add _is_furigana() function with multi-criteria detection (font size, character type, bounding box)
- Modify create_searchable_pdf() to skip furigana in accessible text layer
- Preserve visual appearance while improving screen reader experience
- Support both horizontal and vertical Japanese text layouts

Fixes screen readers reading both furigana and base text (e.g., 'かんぺき' → '完璧' becomes just '完璧' read as 'かんぺき')
"
```

### ステップ 4: GitHubにプッシュ

```bash
# フォークしたリポジトリにプッシュ
git push origin feature/furigana-screen-reader-filter
```

### ステップ 5: プルリクエストを作成

1. GitHubのフォークしたリポジトリ（`https://github.com/YOUR_USERNAME/yomitoku`）にアクセス
2. 「Compare & pull request」ボタンをクリック
3. プルリクエストのタイトルと説明を入力：
   - **タイトル**: `[Feature] Add furigana filtering for screen reader accessibility in searchable PDF`
   - **説明**: `PULL_REQUEST_TEMPLATE.md` の内容をコピー
4. 「Create pull request」をクリック

## プルリクエストの説明文（テンプレート）

`PULL_REQUEST_TEMPLATE.md` に詳細な説明を用意しました。このファイルの内容をGitHubのプルリクエスト説明欄にコピー&ペーストしてください。

## 変更内容の詳細

### 追加されたコード

#### 1. import文の追加
```python
import re
```

#### 2. _is_kana_only 関数
```python
def _is_kana_only(text):
    """
    Check if text contains only hiragana, katakana, and Japanese punctuation.
    Returns True if the text is likely furigana.
    """
    kana_pattern = re.compile(r'^[\u3040-\u309F\u30A0-\u30FF\u3001-\u303F\s]+$')
    return bool(kana_pattern.match(text))
```

#### 3. _is_furigana 関数
```python
def _is_furigana(text, font_size, bbox_height, bbox_width):
    """
    Determine if a text element is furigana based on multiple criteria:
    1. Font size is small (< 8pt)
    2. Text contains only kana characters
    3. Bounding box is small relative to typical text
    """
    if font_size >= 8:
        return False
    
    if not _is_kana_only(text):
        return False
    
    if bbox_height < 12 or bbox_width < 12:
        return True
    
    return False
```

#### 4. create_searchable_pdf 関数内の変更
```python
# フリガナをスキップする処理を追加（146-149行目あたり）
# Skip furigana from the accessible text layer
# Furigana will remain visible in the image layer but won't be read by screen readers
if _is_furigana(text, font_size, bbox_height, bbox_width):
    continue
```

## テスト方法

### 1. 単体テスト（推奨）

```python
# テストスクリプト例
from yomitoku.utils.searchable_pdf import _is_kana_only, _is_furigana

# かな文字のみ
assert _is_kana_only("かんぺき") == True
assert _is_kana_only("ほんぶん") == True

# 漢字を含む
assert _is_kana_only("完璧") == False
assert _is_kana_only("本文テキスト") == False

# フリガナ判定（小さいフォント、かな文字のみ、小さいバウンディングボックス）
assert _is_furigana("かんぺき", font_size=6, bbox_height=10, bbox_width=50) == True
assert _is_furigana("完璧", font_size=12, bbox_height=20, bbox_width=40) == False
```

### 2. 統合テスト

```python
from yomitoku import DocumentAnalyzer
from yomitoku.utils.searchable_pdf import create_searchable_pdf
import cv2

# OCR実行
analyzer = DocumentAnalyzer(configs={}, device="cpu")
results, _ = analyzer("test_image_with_furigana.jpg")

# PDF生成
image = cv2.imread("test_image_with_furigana.jpg")
create_searchable_pdf(
    images=[image],
    ocr_results=[results],
    output_path="output_test.pdf"
)

# スクリーンリーダーでテスト（手動）
```

## 注意事項

1. **ライセンス**: yomitokuのライセンス（CC BY-NC-SA 4.0）を遵守
2. **コーディング規約**: yomitokuの既存のコーディングスタイルに従う
3. **後方互換性**: 既存のAPIを変更しない
4. **テスト**: できれば単体テスト/統合テストを追加（今回は未追加）

## トラブルシューティング

### git操作でエラーが出る場合

```bash
# ユーザー情報を設定
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### プルリクエストがマージされるまで

- yomitokuのメンテナー（Kotaro Kinoshita氏）がレビュー
- 必要に応じて修正を依頼される場合がある
- レビュー後、マージされる

## 参考資料

- [yomitoku GitHub](https://github.com/Utakata/yomitoku)
- [yomitoku Documentation](https://kotaro-kinoshita.github.io/yomitoku/)
- [YOMITOKU_IMPROVEMENT.md](./YOMITOKU_IMPROVEMENT.md) - 詳細ドキュメント

---

**Good luck with your pull request! 🎉**
