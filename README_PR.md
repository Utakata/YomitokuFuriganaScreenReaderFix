# Yomitoku Furigana Filtering - Pull Request Package

このディレクトリには、yomitokuへのプルリクエストに必要なすべてのファイルが含まれています。

## 📋 プルリクエストの内容

### 主な変更
**フリガナフィルタリング機能をsearchable_pdf.pyに追加**

スクリーンリーダーがフリガナを読み上げないよう、自動検出・除外機能を実装しました。これにより、視覚障害者にとって聞き取りやすいPDFが生成されます。

## 📂 ファイル構成

```
.
├── yomitoku_repo/
│   └── src/yomitoku/utils/
│       └── searchable_pdf.py          # ⭐ 改善版（これをPRする）
├── YOMITOKU_IMPROVEMENT.md             # 詳細ドキュメント（日英）
├── PULL_REQUEST_TEMPLATE.md            # PRの説明文テンプレート
├── PR_SUBMISSION_GUIDE.md              # PR作成手順
└── README_PR.md                        # このファイル
```

## 🚀 次のステップ

### 1. 変更内容を確認

**変更されたファイル:**
- `yomitoku_repo/src/yomitoku/utils/searchable_pdf.py`

**追加された機能:**
- `_is_kana_only()` - かな文字のみチェック
- `_is_furigana()` - フリガナ判定（フォントサイズ、文字種別、サイズで判定）
- `create_searchable_pdf()` 内でフリガナ除外処理

### 2. プルリクエストを作成

詳細な手順は **`PR_SUBMISSION_GUIDE.md`** を参照してください。

#### 簡単な手順:

1. **yomitokuをフォーク**
   - https://github.com/Utakata/yomitoku
   - 右上の「Fork」ボタンをクリック

2. **変更を適用**
   ```bash
   git clone https://github.com/YOUR_USERNAME/yomitoku.git
   cd yomitoku
   git checkout -b feature/furigana-screen-reader-filter
   
   # Replitからダウンロードした searchable_pdf.py で上書き
   cp /path/to/searchable_pdf.py src/yomitoku/utils/searchable_pdf.py
   
   git add src/yomitoku/utils/searchable_pdf.py
   git commit -m "feat: Add furigana filtering for screen reader accessibility"
   git push origin feature/furigana-screen-reader-filter
   ```

3. **GitHubでPR作成**
   - フォークしたリポジトリで「Compare & pull request」をクリック
   - `PULL_REQUEST_TEMPLATE.md` の内容を説明欄にコピー
   - 「Create pull request」をクリック

### 3. Replitから直接ファイルをダウンロード

Replitのファイルブラウザから以下のファイルをダウンロード：

**必須:**
- `yomitoku_repo/src/yomitoku/utils/searchable_pdf.py`

**参考資料（任意）:**
- `YOMITOKU_IMPROVEMENT.md`
- `PULL_REQUEST_TEMPLATE.md`

## 📖 ドキュメント

### 1. YOMITOKU_IMPROVEMENT.md
改善内容の詳細説明（日本語・英語）
- 問題点と解決策
- 実装の詳細
- 使用方法
- 技術的背景

### 2. PULL_REQUEST_TEMPLATE.md
プルリクエストの説明文テンプレート
- 概要
- 変更内容
- テスト方法
- チェックリスト

### 3. PR_SUBMISSION_GUIDE.md
プルリクエスト作成の詳細手順
- GitHubでの操作方法
- git コマンド例
- トラブルシューティング

## ✅ 変更内容のサマリー

### Before (元の実装)
```python
# すべてのOCRテキストを透明レイヤーに配置
c.setFillColorRGB(1, 1, 1, alpha=0)
c.drawString(x1, base_y, text)
```
→ スクリーンリーダーがフリガナも基本テキストも両方読む

### After (改善版)
```python
# フリガナを検出してスキップ
if _is_furigana(text, font_size, bbox_height, bbox_width):
    continue  # スクリーンリーダーレイヤーから除外

c.setFillColorRGB(1, 1, 1, alpha=0)
c.drawString(x1, base_y, text)
```
→ スクリーンリーダーが基本テキストのみを読む

## 🎯 期待される効果

- ✅ スクリーンリーダーが基本テキストのみを読み上げる
- ✅ フリガナは視覚的に表示されるが、読み上げられない
- ✅ 「完璧」は「かんぺき」と一度だけ読まれる
- ✅ 視覚障害者にとって聞き取りやすいPDFが生成される

## 📞 連絡先

プルリクエストに関する質問は、GitHubのPRページでコメントしてください。

yomitokuのメンテナー: Kotaro Kinoshita
- Website: https://www.mlism.com/
- GitHub: https://github.com/Utakata/yomitoku

## 📄 ライセンス

CC BY-NC-SA 4.0（yomitokuのライセンスに準拠）

---

**Good luck with your pull request! 🎉**
