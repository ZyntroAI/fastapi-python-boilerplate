import streamlit as st
from utils.search_engine import search_all_documents
from auth.permission_check import require_permission

require_permission("doc_view")
st.set_page_config(page_title="Search Documents", layout="centered")

st.title("🔍 Document Search")
st.caption("Search by filename, content text, and text extracted from scanned images")

# ===== Search Input =====
query = st.text_input("Enter search keyword", placeholder="e.g., receipt, travel expense, document number...",
                     label_visibility="collapsed")

search_type = st.selectbox("Search Scope", ["All", "Document Titles", "Content", "Text from Scanned Images"])

if query and len(query.strip()) >= 2:
    with st.spinner("Searching..."):
        results = search_all_documents(query.strip(), search_type)
    
    if results:
        st.subheader(f"✅ Found {len(results)} results")
        st.divider()
        
        for idx, item in enumerate(results):
            with st.expander(f"📄 {item['title']} — {item['type']}", expanded=idx < 3):
                st.write(f"📂 Source: {item['source']}")
                st.write(f"📅 Date: {item['date']}")
                if item.get("preview"):
                    st.markdown(f"...{item['preview']}...")
                st.page_link(f"pages/📄_my_documents.py?id={item['id']}", label="👉 Open Document")
    else:
        st.info("❌ No documents found matching your search")
        st.caption("💡 Try different keywords or check your spelling")
elif query:
    st.warning("⚠️ Please enter at least 2 characters")
else:
    st.info("💡 Type a keyword to start searching")
