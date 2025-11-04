# 最も簡単なプルリクエスト作成方法

## ステップ1: GitHubでyomitokuをフォーク

1. https://github.com/Utakata/yomitoku にアクセス
2. 右上の「Fork」ボタンをクリック
3. 自分のアカウントにフォークを作成

## ステップ2: GitHub上で直接ファイルを編集

### オプションA: GitHub Web Editorを使用（最も簡単）

1. フォークしたリポジトリ（`https://github.com/YOUR_USERNAME/yomitoku`）にアクセス
2. `src/yomitoku/utils/searchable_pdf.py` を開く
3. 鉛筆アイコン（Edit this file）をクリック
4. Replitからコピーした改善版のコードをペースト
5. 下部の「Commit changes」をクリック
   - Commit message: `feat: Add furigana filtering for screen reader accessibility`
   - Description: （任意）
6. 「Commit changes」ボタンをクリック
7. リポジトリのトップページに戻り、「Contribute」→「Open pull request」をクリック

### オプションB: github.devを使用（VS Code風エディタ）

1. フォークしたリポジトリで `.` キー（ドット）を押す
   - または、URLを `github.com` → `github.dev` に変更
2. VS Code風のエディタが開く
3. `src/yomitoku/utils/searchable_pdf.py` を開いて編集
4. 左サイドバーの「Source Control」（Git アイコン）を開く
5. 変更をステージング → コミット → プッシュ
6. GitHubのリポジトリページでプルリクエストを作成

## ステップ3: 改善版のコードを取得

Replitから以下のファイルの内容をコピーします：

### 📄 searchable_pdf.py の改善版

以下の変更箇所をコピーして、GitHubで該当箇所に貼り付けてください。

#### 1. import文に追加（1-2行目）
```python
import os
import re  # ← この行を追加
```

#### 2. 関数を追加（68行目以降に追加）

to_full_width関数の後に以下を追加：

```python
def _is_kana_only(text):
    """
    Check if text contains only hiragana, katakana, and Japanese punctuation.
    Returns True if the text is likely furigana.
    """
    # Pattern: hiragana, katakana, small kana, Japanese punctuation, whitespace
    kana_pattern = re.compile(r'^[\u3040-\u309F\u30A0-\u30FF\u3001-\u303F\s]+$')
    return bool(kana_pattern.match(text))


def _is_furigana(text, font_size, bbox_height, bbox_width):
    """
    Determine if a text element is furigana based on multiple criteria:
    1. Font size is small (< 8pt)
    2. Text contains only kana characters
    3. Bounding box is small relative to typical text
    
    Args:
        text: The text content
        font_size: Calculated font size
        bbox_height: Height of bounding box
        bbox_width: Width of bounding box
    
    Returns:
        bool: True if the text is likely furigana
    """
    # Criterion 1: Small font size (typical furigana is < 8pt)
    if font_size >= 8:
        return False
    
    # Criterion 2: Must be kana-only
    if not _is_kana_only(text):
        return False
    
    # Criterion 3: Small bounding box (furigana is typically small)
    # For horizontal text, height < 12px; for vertical, width < 12px
    if bbox_height < 12 or bbox_width < 12:
        return True
    
    return False
```

#### 3. create_searchable_pdf関数内に追加（142-149行目あたり）

以下の部分を探して：
```python
            if direction == "horizontal":
                font_size = _calc_font_size(text, bbox_height, bbox_width)
            else:
                font_size = _calc_font_size(text, bbox_width, bbox_height)

            c.setFont("MPLUS1p-Medium", font_size)
```

この後に以下を追加：
```python
            # Skip furigana from the accessible text layer
            # Furigana will remain visible in the image layer but won't be read by screen readers
            if _is_furigana(text, font_size, bbox_height, bbox_width):
                continue
```

完成形：
```python
            if direction == "horizontal":
                font_size = _calc_font_size(text, bbox_height, bbox_width)
            else:
                font_size = _calc_font_size(text, bbox_width, bbox_height)

            # Skip furigana from the accessible text layer
            # Furigana will remain visible in the image layer but won't be read by screen readers
            if _is_furigana(text, font_size, bbox_height, bbox_width):
                continue

            c.setFont("MPLUS1p-Medium", font_size)
```

## ステップ4: プルリクエストを作成

1. GitHubのフォークしたリポジトリに戻る
2. 「Contribute」ボタンをクリック
3. 「Open pull request」をクリック
4. タイトル: `[Feature] Add furigana filtering for screen reader accessibility in searchable PDF`
5. 説明文: `PULL_REQUEST_TEMPLATE.md` の内容をコピー&ペースト
6. 「Create pull request」をクリック

## トラブルシューティング

### Q: GitHubで編集できない
A: フォークしたリポジトリ（`YOUR_USERNAME/yomitoku`）で編集していることを確認してください。元のリポジトリ（`Utakata/yomitoku`）は編集できません。

### Q: コミットメッセージは何を書けばいい？
A: 
```
feat: Add furigana filtering for screen reader accessibility

- Add _is_kana_only() and _is_furigana() functions
- Skip furigana in accessible text layer
- Support horizontal and vertical Japanese text
```

### Q: 変更がうまく適用されない
A: 完全版のファイルをReplitからダウンロードして、GitHubの「Upload files」機能で直接アップロードすることもできます。

---

**このガイドで問題が解決しない場合は、具体的なエラーメッセージを教えてください！**
