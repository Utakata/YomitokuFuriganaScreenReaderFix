# [Feature] Add furigana filtering for screen reader accessibility in searchable PDF

## 概要 (Summary)

スクリーンリーダーがフリガナ（ルビ）を読み上げないよう、`searchable_pdf.py`にフリガナ検出・除外機能を追加しました。

This PR adds furigana (ruby) detection and filtering functionality to `searchable_pdf.py`, improving screen reader accessibility for Japanese documents.

## 問題 (Problem)

元の実装では、OCRで検出されたすべてのテキスト（フリガナと基本テキスト）が透明テキストレイヤーに配置されるため：

- スクリーンリーダーがフリガナと基本テキストの**両方**を読み上げる
- 例：「完璧」→「かんぺき」→「完璧」のように二重に読まれる
- 視覚障害者にとって非常に聞き取りにくい

In the original implementation, all OCR-detected text (both furigana and base text) is placed in the transparent text layer, causing screen readers to read both furigana and base text, resulting in a poor user experience for visually impaired users.

## 解決策 (Solution)

フリガナを自動検出し、透明テキストレイヤーから除外：

- **視覚レイヤー**：元の画像にフリガナと基本テキストが表示される
- **音声レイヤー**（スクリーンリーダー用）：基本テキストのみが含まれる
- 結果：スクリーンリーダーは「完璧」を「かんぺき」と一度だけ読み上げる

Automatically detect furigana and exclude it from the transparent text layer while preserving visual appearance, so screen readers only read base text once.

## 変更内容 (Changes)

### 追加された関数 (Added Functions)

1. **`_is_kana_only(text: str) -> bool`**
   - ひらがな・カタカナのみで構成されているかチェック
   - Check if text contains only hiragana, katakana, and Japanese punctuation

2. **`_is_furigana(text: str, font_size: float, bbox_height: int, bbox_width: int) -> bool`**
   - 複数の基準でフリガナを判定：
     - フォントサイズ < 8pt
     - かな文字のみ
     - バウンディングボックス < 12px
   - Determine if text is furigana based on font size, character type, and bounding box size

### 修正された関数 (Modified Functions)

**`create_searchable_pdf()`**
- フリガナを検出した場合、透明テキストレイヤーに追加せずにスキップ
- Skip furigana when building the transparent text layer for screen readers

## テスト (Testing)

### 動作確認 (Verification)

フリガナ検出ロジックの正確性：
- ✅ フォントサイズベースの検出が正しく動作
- ✅ かな文字のみのテキストを正しく識別
- ✅ 基本テキストが誤って除外されない

### 互換性 (Compatibility)

- ✅ 既存のyomitoku API完全互換
- ✅ 縦書き・横書き両方に対応
- ✅ 既存の機能に影響なし

### 期待される動作 (Expected Behavior)

生成されたPDFをスクリーンリーダー（NVDA、JAWS、VoiceOverなど）で開いた場合：
- ✅ スクリーンリーダーが基本テキスト（漢字など）のみを読み上げる
- ✅ フリガナは視覚的に表示されるが、読み上げられない
- ✅ 「完璧」は「かんぺき」と一度だけ読まれる（「かんぺき」→「完璧」ではない）

## 技術的詳細 (Technical Details)

### フリガナ検出アルゴリズム

| 特徴 | フリガナ | 基本テキスト |
|------|---------|------------|
| フォントサイズ | < 8pt | ≥ 8pt |
| 文字種別 | かな文字のみ | 漢字を含む |
| バウンディングボックス | 小さい (< 12px) | 大きい (≥ 12px) |

### PDFの構造

1. **視覚レイヤー（画像）**: 元の画像が描画され、フリガナと基本テキストが両方表示される
2. **音声レイヤー（透明テキスト）**: 基本テキストのみが透明で配置され、スクリーンリーダーが読み上げる

## Breaking Changes

なし (None) - 既存のAPIは完全に互換性があります

## チェックリスト (Checklist)

- [x] コードが正しく動作する
- [x] 既存のテストが通る
- [x] ドキュメントを更新
- [x] 後方互換性を保持
- [x] コードレビュー準備完了

## 関連情報 (Related Information)

- W3C Accessibility Guidelines: [PDF Techniques](https://www.w3.org/WAI/WCAG21/Techniques/pdf/)
- Japanese Ruby Annotation: [W3C Ruby Annotation](https://www.w3.org/TR/ruby/)

## 今後の改善案 (Future Improvements)

1. 閾値を設定可能にする (Configurable thresholds)
2. 回帰テストを追加 (Add regression tests)
3. 位置ベースのチェックで精度向上 (Position-based checks for better accuracy)

## スクリーンショット / デモ (Screenshots / Demo)

### Before (元の実装)
```
Screen reader reads: "かんぺき" → "完璧"
(furigana + base text, confusing)
```

### After (改善版)
```
Screen reader reads: "完璧" (as "かんぺき")
(base text only, natural reading)
```

---

**ライセンス (License)**: CC BY-NC-SA 4.0（yomitokuのライセンスに準拠）
