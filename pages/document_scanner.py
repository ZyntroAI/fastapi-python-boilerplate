# ===== 📑 Multi-Page Mode =====
st.subheader("📑 Multi-Page Scanning")

if "multi_pages" not in st.session_state:
    st.session_state["multi_pages"] = []

col_add, col_clear, col_list = st.columns([2, 1, 3])

with col_add:
    multi_image = st.camera_input("📸 Add New Page", key="multi_cam", label_visibility="collapsed")
    if multi_image:
        img = Image.open(multi_image)
        st.session_state["multi_pages"].append(img)
        st.success(f"✅ Added page {len(st.session_state['multi_pages'])}")
        st.rerun()

with col_clear:
    if st.button("🗑️ Clear All"):
        st.session_state["multi_pages"] = []
        st.rerun()

# Display page list
pages = st.session_state["multi_pages"]
if pages:
    st.write(f"📋 Total pages: {len(pages)}")
    
    # Show preview thumbnails
    cols = st.columns(min(4, len(pages)))
    for idx, img in enumerate(pages):
        with cols[idx % 4]:
            st.image(img, caption=f"Page {idx+1}", use_container_width=True)
            if st.button(f"❌ Remove", key=f"del_{idx}"):
                pages.pop(idx)
                st.rerun()
    
    # Generate PDF
    st.divider()
    pdf_name = st.text_input("📄 PDF Filename", value=f"scanned_document_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf")
    
    if st.button("📥 Generate & Download PDF", type="primary", use_container_width=True):
        from utils.pdf_builder import images_to_pdf
        pdf_bytes = images_to_pdf(pages)
        st.download_button(
            label="📅 Download PDF File",
            data=pdf_bytes,
            file_name=pdf_name.strip(),
            mime="application/pdf"
        )
        log_action("Created multi-page PDF", ActionCategory.DOCUMENT, ActionStatus.SUCCESS,
                  description=f"{len(pages)} pages")
else:
    st.info("📌 Take photos to add document pages")
