import streamlit as st
import os
from datetime import datetime
from PIL import Image
import json
from src.furigana_analyzer import FuriganaAnalyzer
from src.pdf_generator import ScreenReaderPDFGenerator


st.set_page_config(
    page_title="Yomitoku スクリーンリーダー最適化ツール",
    page_icon="📖",
    layout="wide"
)

st.title("📖 日本語フリガナ スクリーンリーダー最適化ツール")

st.markdown("""
### システムの目的

日本語の縦書き・横書き文書画像から、スクリーンリーダーで正しく読み上げられるサーチャブルPDFを生成します。

**現在の問題点:**
- フリガナが基本テキストより先に読み上げられる（例: 「かんぺき」→「完璧」）

**最適化後:**
- 基本テキストのみを読み上げ（例: 「完璧」を「かんぺき」と読む）
- フリガナは視覚的には表示されるが、音声では読まない

---
""")

if 'demo_pdf_generated' not in st.session_state:
    st.session_state.demo_pdf_generated = False

col1, col2 = st.columns(2)

with col1:
    st.header("🧪 デモPDF生成")
    st.markdown("""
    スクリーンリーダー最適化アルゴリズムのデモPDFを生成します。
    
    **含まれる内容:**
    - フリガナ付きテキスト（完璧、素晴らしい）
    - 通常のテキスト
    """)
    
    if st.button("デモPDFを生成", type="primary"):
        with st.spinner("PDF生成中..."):
            try:
                os.makedirs("output", exist_ok=True)
                
                pdf_gen = ScreenReaderPDFGenerator()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"output/demo_screader_optimized_{timestamp}.pdf"
                
                result_path = pdf_gen.create_test_pdf_with_demo(output_path)
                
                st.session_state.demo_pdf_generated = True
                st.session_state.demo_pdf_path = result_path
                
                st.success(f"✅ PDF生成完了: {result_path}")
                
            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
    
    if st.session_state.demo_pdf_generated:
        st.markdown("---")
        st.subheader("📥 生成されたPDFダウンロード")
        
        with open(st.session_state.demo_pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            st.download_button(
                label="PDFをダウンロード",
                data=pdf_bytes,
                file_name=os.path.basename(st.session_state.demo_pdf_path),
                mime="application/pdf"
            )
        
        st.markdown("""
        **テスト方法:**
        1. ダウンロードしたPDFを開く
        2. スクリーンリーダー（NVDA, JAWS, VoiceOver）で読み上げテスト
        3. フリガナではなく、基本テキストが読み上げられることを確認
        """)

with col2:
    st.header("📷 画像アップロード（将来実装）")
    st.markdown("""
    将来的には、画像をアップロードして自動的にOCR処理とフリガナ検出を行います。
    
    **予定機能:**
    - yomitokuを使った日本語OCR
    - 縦書き・横書きレイアウト解析
    - フリガナと基本テキストの自動分離
    - スクリーンリーダー最適化PDF生成
    """)
    
    uploaded_file = st.file_uploader(
        "画像をアップロード（PNG, JPG）",
        type=['png', 'jpg', 'jpeg'],
        disabled=True,
        help="OCR機能は将来実装予定です"
    )

st.markdown("---")

with st.expander("🛠️ システム設定"):
    st.markdown("""
    ### 現在の設定
    
    **フリガナ検出アルゴリズム:**
    - フォントサイズが8px未満
    - ひらがな・カタカナのみで構成
    - 基本テキストとの位置関係（縦書き・横書き対応）
    
    **PDFテキストレイヤー設定:**
    - 描画モード: 3 (非表示テキスト)
    - 透明度: 0% (完全透明)
    - 読み上げ対象: 基本テキストのみ
    """)

with st.expander("📊 アルゴリズムの詳細"):
    st.markdown("""
    ### フリガナ検出アルゴリズム
    
    1. **候補検出**
       - テキストブロックのフォントサイズを分析
       - 8px未満の小さなテキストを検出
       - 文字種類（ひらがな・カタカナのみ）を確認
    
    2. **基本テキストとの紐付け**
       - 縦書き: 水平距離50px以内、垂直方向のオーバーラップ50%以上
       - 横書き: 垂直距離20px以内、水平方向のオーバーラップ50%以上
    
    3. **PDF生成最適化**
       - 基本テキスト: 透明テキストレイヤーに配置
       - フリガナ: 視覚的には表示、音声読み上げでは非表示
       - スクリーンリーダー: 基本テキストのみを読み上げ
    
    ### W3C Ruby T2S Requirements準拠
    
    このツールは、W3C（World Wide Web Consortium）のRuby Text to Speech要件に基づいて設計されています:
    
    - `aria-hidden="true"` による フリガナの音声非表示化
    - 基本テキスト優先の読み上げ順序
    - アクセシビリティツリーへの適切な情報提供
    """)

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Powered by PyMuPDF & Streamlit | 日本語スクリーンリーダー最適化プロジェクト</p>
</div>
""", unsafe_allow_html=True)
