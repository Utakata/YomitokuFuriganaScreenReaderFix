"""
Streamlit app for converting image-based EPUB to searchable EPUB.
"""

import streamlit as st
import tempfile
from pathlib import Path
from src.epub_searchable.main import convert_epub_to_searchable

st.set_page_config(
    page_title="サーチャブルEPUB変換ツール",
    page_icon="📚",
    layout="centered"
)

st.title("📚 サーチャブルEPUB変換ツール")

st.markdown("""
画像ベースのEPUB（固定レイアウト）を、検索とコピー&ペーストが可能な  
**サーチャブルEPUB**に変換します。

### 特徴
- ✅ 元のレイアウトを完全に保持
- ✅ 透明なテキストレイヤーを追加
- ✅ 縦書き・横書き対応
- ✅ 高精度OCR（yomitoku使用）
- ✅ フリガナフィルタリング対応
""")

st.divider()

# File uploader
uploaded_file = st.file_uploader(
    "EPUBファイルをアップロード",
    type=['epub'],
    help="画像ベースのEPUBファイルを選択してください"
)

if uploaded_file is not None:
    st.success(f"アップロード完了: {uploaded_file.name}")
    
    # Convert button
    if st.button("🔄 変換開始", type="primary", use_container_width=True):
        with st.spinner("変換中... この処理には数分かかる場合があります。"):
            try:
                # Create temporary files
                with tempfile.NamedTemporaryFile(delete=False, suffix='.epub') as input_temp:
                    input_temp.write(uploaded_file.read())
                    input_path = input_temp.name
                
                output_path = tempfile.mktemp(suffix='_searchable.epub')
                
                # Progress display
                progress_text = st.empty()
                progress_bar = st.progress(0)
                
                progress_text.text("EPUB展開中...")
                progress_bar.progress(10)
                
                # Get font path from yomitoku
                try:
                    from yomitoku.constants import ROOT_DIR
                    font_path = str(Path(ROOT_DIR) / "resource" / "MPLUS1p-Medium.ttf")
                except:
                    font_path = None
                
                progress_text.text("OCR処理中...")
                progress_bar.progress(30)
                
                # Convert
                result_path = convert_epub_to_searchable(
                    input_path,
                    output_path,
                    font_path=font_path
                )
                
                progress_text.text("EPUB再圧縮中...")
                progress_bar.progress(90)
                
                # Read result file
                with open(result_path, 'rb') as f:
                    result_data = f.read()
                
                progress_bar.progress(100)
                progress_text.text("変換完了！")
                
                st.success("✅ 変換が完了しました！")
                
                # Download button
                output_filename = uploaded_file.name.replace('.epub', '_searchable.epub')
                st.download_button(
                    label="📥 サーチャブルEPUBをダウンロード",
                    data=result_data,
                    file_name=output_filename,
                    mime="application/epub+zip",
                    use_container_width=True
                )
                
                # Cleanup
                Path(input_path).unlink(missing_ok=True)
                Path(output_path).unlink(missing_ok=True)
                
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
                st.exception(e)

st.divider()

with st.expander("📖 使い方"):
    st.markdown("""
    1. **EPUBファイルをアップロード**
       - 画像ベースのEPUBファイル（固定レイアウト）を選択
    
    2. **変換開始ボタンをクリック**
       - OCR処理が実行されます（数分かかる場合があります）
    
    3. **ダウンロード**
       - 変換完了後、サーチャブルEPUBをダウンロード
    
    ### 仕組み
    - yomitokuで画像からテキストを抽出
    - 透明なテキストレイヤーを元の画像に重ねる
    - 検索・コピー可能なEPUBを生成
    - フリガナは視覚的に表示されるが、スクリーンリーダーでは読み上げられない
    """)

with st.expander("⚙️ 技術詳細"):
    st.markdown("""
    **使用技術:**
    - OCRエンジン: yomitoku (DocumentAnalyzer)
    - フォント計算: reportlab
    - EPUB処理: lxml, zipfile
    - 画像処理: Pillow
    
    **処理フロー:**
    1. EPUB展開（ZIP解凍）
    2. HTMLファイルから画像参照を取得
    3. yomitokuでOCR処理
    4. 透明テキストレイヤー生成
    5. EPUB再圧縮
    
    **フリガナフィルタリング:**
    - フォントサイズ < 8pt
    - かな文字のみ
    - 小さいバウンディングボックス
    → これらの条件でフリガナを検出し、スクリーンリーダーから除外
    """)

st.markdown("---")
st.caption("Powered by yomitoku | CC BY-NC-SA 4.0")
