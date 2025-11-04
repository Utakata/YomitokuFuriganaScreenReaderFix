# Yomitoku スクリーンリーダー最適化プロジェクト

## 概要
日本語の縦書き・横書き文書画像から、スクリーンリーダーで正しく読み上げられるサーチャブルPDFを生成するツールです。

## プロジェクトの目的
- 日本語フリガナ付き文書をOCR処理
- フリガナと基本テキストを分離
- スクリーンリーダーが基本テキストのみを読み上げるPDFを生成
- 縦書き・横書き両方に対応

## 技術スタック
- **OCRエンジン**: yomitoku (日本語特化Document AI)
- **PDF生成**: PyMuPDF, reportlab
- **UI**: Streamlit
- **画像処理**: Pillow, OpenCV
- **言語**: Python 3.11

## プロジェクト構造
```
/
├── app.py                      # Streamlit メインアプリ
├── src/
│   ├── ocr_processor.py        # yomitoku OCR処理
│   ├── furigana_analyzer.py    # フリガナ検出・分離アルゴリズム
│   └── pdf_generator.py        # スクリーンリーダー対応PDF生成
├── requirements.txt
├── output/                     # 生成されたPDF保存先
└── uploaded_images/            # アップロード画像保存先
```

## 最新の変更
- 2025-11-04: プロジェクト初期設定完了

## アーキテクチャの決定
- yomitokuを使用して日本語OCRとレイアウト解析を実行
- フリガナ検出: テキストサイズと配置からルビテキストを判定
- PDFテキストレイヤー: 基本テキストのみを音声読み上げ対象に設定

## 使用方法
```bash
streamlit run app.py
```
