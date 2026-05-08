"""
SmartSplit Bill AI
Main Streamlit Application - Complete Implementation
"""

import streamlit as st
from PIL import Image
import sys
from pathlib import Path
import pandas as pd

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from utils.receipt_processor import ReceiptProcessor
from models.model_manager import ModelType


# Page configuration
st.set_page_config(
    page_title="SmartSplit Bill AI",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables"""
    if 'processor' not in st.session_state:
        st.session_state.processor = ReceiptProcessor()
    
    if 'step' not in st.session_state:
        st.session_state.step = 1
    
    if 'receipt_data' not in st.session_state:
        st.session_state.receipt_data = None
    
    if 'people_names' not in st.session_state:
        st.session_state.people_names = []
    
    if 'item_assignments' not in st.session_state:
        st.session_state.item_assignments = {}
    
    if 'split_result' not in st.session_state:
        st.session_state.split_result = None
    
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None


def reset_app():
    """Reset application state"""
    st.session_state.step = 1
    st.session_state.receipt_data = None
    st.session_state.people_names = []
    st.session_state.item_assignments = {}
    st.session_state.split_result = None
    st.session_state.uploaded_image = None
    st.session_state.processor.reset()


def render_sidebar():
    """Render sidebar with navigation and info"""
    with st.sidebar:
        st.header("📋 Panduan Penggunaan")
        
        # Progress indicator
        steps = [
            "1️⃣ Upload Struk",
            "2️⃣ Verifikasi Data",
            "3️⃣ Input Peserta",
            "4️⃣ Assign Items",
            "5️⃣ Lihat Hasil"
        ]
        
        current_step = st.session_state.step
        for i, step_text in enumerate(steps, 1):
            if i < current_step:
                st.success(f"✓ {step_text}")
            elif i == current_step:
                st.info(f"➤ {step_text}")
            else:
                st.text(f"  {step_text}")
        
        st.divider()
        
        # Model info
        st.subheader("🤖 Model AI")
        default_model = st.session_state.processor.model_manager.get_default_model_type()
        st.write(f"**Model**: {default_model.value}")
        
        # Available models
        with st.expander("Model yang Tersedia"):
            models = st.session_state.processor.model_manager.get_available_models()
            for model_id, info in models.items():
                status = "✓" if info["available"] else "✗"
                st.write(f"{status} **{info['name']}**")
                st.caption(info['description'])
        
        st.divider()
        
        # Reset button
        if st.button("🔄 Reset Aplikasi", use_container_width=True):
            reset_app()
            st.rerun()
        
        st.divider()
        st.caption("💡 **Tips**: Pastikan foto struk jelas dan tidak blur untuk hasil terbaik!")


def render_step1_upload():
    """Step 1: Upload receipt image"""
    st.header("1️⃣ Upload Struk Belanja")
    
    st.markdown("""
    Upload foto struk belanja Anda. AI akan membaca dan mengekstrak data secara otomatis.
    """)
    
    uploaded_file = st.file_uploader(
        "Pilih gambar struk (JPG, JPEG, PNG)",
        type=["jpg", "jpeg", "png"],
        help="Upload foto struk belanja yang ingin diproses"
    )
    
    if uploaded_file is not None:
        # Display uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Preview Struk")
            image = Image.open(uploaded_file)
            st.image(image, use_column_width=True)
            st.session_state.uploaded_image = image
        
        with col2:
            st.subheader("Informasi File")
            st.write(f"**Nama File:** {uploaded_file.name}")
            st.write(f"**Ukuran:** {uploaded_file.size / 1024:.2f} KB")
            st.write(f"**Dimensi:** {image.size[0]} x {image.size[1]} px")
            
            st.divider()
            
            # Process button
            if st.button("🚀 Proses Struk dengan AI", type="primary", use_container_width=True):
                with st.spinner("🤖 AI sedang membaca struk..."):
                    success, message, receipt_data = st.session_state.processor.process_receipt_image(
                        image,
                        use_mock_on_failure=False  # Disable mock fallback - show real errors
                    )
                    
                    if success:
                        st.session_state.receipt_data = receipt_data
                        st.session_state.step = 2
                        st.success(f"✓ {message}")
                        st.rerun()
                    else:
                        st.error(f"✗ {message}")
                        st.info("💡 Tips: Pastikan foto struk jelas, tidak blur, dan pencahayaan baik")
                        
                        # Show debug info
                        with st.expander("🔍 Debug Info"):
                            st.write("Model yang digunakan:", st.session_state.processor.model_manager.get_default_model_type().value)
                            if receipt_data:
                                st.json(receipt_data)
    else:
        st.info("👆 Silakan upload foto struk untuk memulai")


def render_step2_verify():
    """Step 2: Verify extracted data"""
    st.header("2️⃣ Verifikasi Data Struk")
    
    st.markdown("""
    Periksa data yang diekstrak oleh AI. Anda bisa mengedit jika ada yang salah.
    """)
    
    receipt_data = st.session_state.receipt_data
    
    if receipt_data is None:
        st.warning("Tidak ada data struk. Silakan upload struk terlebih dahulu.")
        if st.button("← Kembali ke Upload"):
            st.session_state.step = 1
            st.rerun()
        return
    
    # Display extracted items
    st.subheader("🛒 Items yang Terdeteksi")
    
    items = receipt_data.get("items", [])
    
    if items:
        # Create editable dataframe
        df = pd.DataFrame(items)
        df.index = df.index + 1  # Start from 1
        
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="dynamic",
            column_config={
                "name": st.column_config.TextColumn("Nama Item", required=True),
                "quantity": st.column_config.NumberColumn("Jumlah", min_value=1, required=True),
                "price": st.column_config.NumberColumn("Harga Satuan", format="$%.2f", required=True),
                "total": st.column_config.NumberColumn("Total", format="$%.2f", required=True)
            }
        )
        
        # Update items if edited
        receipt_data["items"] = edited_df.to_dict('records')
    else:
        st.warning("Tidak ada items yang terdeteksi!")
    
    # Display summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Subtotal", f"Rp {receipt_data.get('subtotal', 0):,.0f}")
    
    with col2:
        charges = receipt_data.get('additional_charges', [])
        total_charges = sum(c.get('amount', 0) for c in charges)
        st.metric("Biaya Tambahan", f"Rp {total_charges:,.0f}")
    
    with col3:
        st.metric("Total", f"Rp {receipt_data.get('total', 0):,.0f}")
    
    # Additional charges
    if charges:
        with st.expander("📝 Biaya Tambahan"):
            for charge in charges:
                st.write(f"- {charge.get('name', 'Unknown')}: Rp {charge.get('amount', 0):,.0f}")
    
    # Processing info
    with st.expander("ℹ️ Informasi Processing"):
        st.write(f"**Model**: {receipt_data.get('model_used', 'Unknown')}")
        st.write(f"**Waktu Processing**: {receipt_data.get('processing_time', 0):.2f} detik")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Kembali", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    
    with col2:
        if st.button("Lanjut ke Input Peserta →", type="primary", use_container_width=True):
            if len(items) > 0:
                st.session_state.step = 3
                st.rerun()
            else:
                st.error("Tidak ada items untuk dibagi!")


def render_step3_people():
    """Step 3: Input people names"""
    st.header("3️⃣ Input Nama Peserta")
    
    st.markdown("""
    Masukkan nama orang-orang yang akan berbagi tagihan ini.
    """)
    
    # Number of people
    num_people = st.number_input(
        "Jumlah Orang",
        min_value=2,
        max_value=20,
        value=len(st.session_state.people_names) if st.session_state.people_names else 2,
        help="Minimal 2 orang untuk split bill"
    )
    
    # Input names
    st.subheader("👥 Nama Peserta")
    
    people_names = []
    cols = st.columns(2)
    
    for i in range(num_people):
        col = cols[i % 2]
        with col:
            default_name = ""
            if i < len(st.session_state.people_names):
                default_name = st.session_state.people_names[i]
            
            name = st.text_input(
                f"Orang {i+1}",
                value=default_name,
                key=f"person_{i}",
                placeholder=f"Nama orang ke-{i+1}"
            )
            if name.strip():
                people_names.append(name.strip())
    
    # Validation
    if people_names:
        # Check duplicates
        if len(people_names) != len(set(people_names)):
            st.warning("⚠️ Ada nama yang duplikat!")
        
        # Check minimum
        if len(people_names) < 2:
            st.warning("⚠️ Minimal 2 orang untuk split bill!")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Kembali", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    
    with col2:
        can_proceed = (
            len(people_names) >= 2 and 
            len(people_names) == len(set(people_names))
        )
        
        if st.button("Lanjut ke Assign Items →", type="primary", use_container_width=True, disabled=not can_proceed):
            st.session_state.people_names = people_names
            
            # Setup bill split
            success, message = st.session_state.processor.setup_bill_split(people_names)
            
            if success:
                st.session_state.step = 4
                st.rerun()
            else:
                st.error(f"✗ {message}")


def render_step4_assign():
    """Step 4: Assign items to people"""
    st.header("4️⃣ Assign Items ke Orang")
    
    st.markdown("""
    Tentukan siapa yang membayar item mana. Satu item bisa dibagi ke beberapa orang.
    """)
    
    receipt_data = st.session_state.receipt_data
    people_names = st.session_state.people_names
    items = receipt_data.get("items", [])
    
    if not items or not people_names:
        st.error("Data tidak lengkap!")
        return
    
    # Assignment interface
    st.subheader("🎯 Assignment")
    
    assignments = {}
    
    for idx, item in enumerate(items):
        with st.container():
            col1, col2 = st.columns([2, 3])
            
            with col1:
                st.write(f"**{item['name']}**")
                st.caption(f"Rp {item['total']:,.0f} ({item['quantity']} x Rp {item['price']:,.0f})")
            
            with col2:
                # Get previous assignment if exists
                default_selection = st.session_state.item_assignments.get(idx, [])
                
                selected_people = st.multiselect(
                    f"Dibayar oleh:",
                    options=people_names,
                    default=default_selection,
                    key=f"assign_{idx}",
                    label_visibility="collapsed"
                )
                
                if selected_people:
                    assignments[idx] = selected_people
                    # Show split info
                    split_amount = item['total'] / len(selected_people)
                    st.caption(f"→ Rp {split_amount:,.0f} per orang")
        
        st.divider()
    
    # Update assignments
    st.session_state.item_assignments = assignments
    
    # Check if all items assigned
    all_assigned = len(assignments) == len(items)
    
    if not all_assigned:
        st.warning(f"⚠️ {len(items) - len(assignments)} item belum di-assign!")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Kembali", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
    
    with col2:
        if st.button("Hitung Split →", type="primary", use_container_width=True, disabled=not all_assigned):
            # Assign all items
            for item_idx, assigned_people in assignments.items():
                st.session_state.processor.assign_item_to_people(item_idx, assigned_people)
            
            # Calculate split
            with st.spinner("Menghitung split..."):
                success, message, split_data = st.session_state.processor.calculate_split()
                
                if success:
                    st.session_state.split_result = split_data
                    st.session_state.step = 5
                    st.rerun()
                else:
                    st.error(f"✗ {message}")


def render_step5_result():
    """Step 5: Display split result"""
    st.header("5️⃣ Hasil Split Bill")
    
    st.markdown("""
    Berikut adalah rincian pembagian tagihan untuk setiap orang.
    """)
    
    split_result = st.session_state.split_result
    
    if split_result is None:
        st.error("Tidak ada hasil split!")
        return
    
    split_data = split_result.get("split", {})
    summary = split_result.get("summary", {})
    
    # Summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Bill", f"Rp {summary.get('bill_total', 0):,.0f}")
    
    with col2:
        st.metric("Jumlah Orang", summary.get('num_people', 0))
    
    with col3:
        st.metric("Jumlah Items", summary.get('num_items', 0))
    
    with col4:
        is_valid = summary.get('is_valid', False)
        status = "✓ Valid" if is_valid else "✗ Invalid"
        st.metric("Status", status)
    
    st.divider()
    
    # Per-person breakdown
    st.subheader("💰 Rincian Per Orang")
    
    for person, data in split_data.items():
        with st.expander(f"**{person}** - Total: Rp {data['total']:,.0f}", expanded=True):
            # Items
            if data['items']:
                st.write("**Items:**")
                for item in data['items']:
                    st.write(f"- {item['name']}: Rp {item['amount']:,.0f}")
            
            # Summary
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Subtotal Items", f"Rp {data['subtotal']:,.0f}")
            
            with col2:
                st.metric("Biaya Tambahan", f"Rp {data['additional_charges']:,.0f}")
            
            with col3:
                st.metric("**TOTAL**", f"**Rp {data['total']:,.0f}**")
    
    # Validation info
    if not summary.get('is_valid', False):
        st.warning(f"⚠️ Perhatian: Total yang dihitung (Rp {summary.get('calculated_total', 0):,.0f}) berbeda dengan total bill (Rp {summary.get('bill_total', 0):,.0f})")
        st.info("💡 Ini mungkin karena AI salah membaca total dari struk. Anda bisa kembali ke Step 2 untuk mengoreksi total, atau lanjutkan dengan total yang dihitung dari items.")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Kembali ke Assignment", use_container_width=True):
            st.session_state.step = 4
            st.rerun()
    
    with col2:
        if st.button("🔄 Split Bill Baru", type="primary", use_container_width=True):
            reset_app()
            st.rerun()


def main():
    """Main application entry point"""
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.title("🧾 SmartSplit Bill AI")
    st.markdown("### Aplikasi Pintar untuk Membagi Tagihan")
    
    # Render sidebar
    render_sidebar()
    
    # Render current step
    current_step = st.session_state.step
    
    if current_step == 1:
        render_step1_upload()
    elif current_step == 2:
        render_step2_verify()
    elif current_step == 3:
        render_step3_people()
    elif current_step == 4:
        render_step4_assign()
    elif current_step == 5:
        render_step5_result()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <small>SmartSplit Bill AI - Dibuat dengan ❤️ menggunakan Streamlit & AI</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
