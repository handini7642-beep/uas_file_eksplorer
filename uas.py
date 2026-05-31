import streamlit as st
import requests

# ====================================================================
# 1. KONFIGURASI HALAMAN & STYLE CSS
# ====================================================================
st.set_page_config(page_title="File Explorer Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    div[data-testid="stCard"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
    }
    .file-content {
        background-color: #1e1e1e;
        color: #d4d4d4;
        padding: 20px;
        border-radius: 8px;
        font-family: 'Courier New', Courier, monospace;
        white-space: pre-wrap;
        border-left: 5px solid #4F46E5;
    }
    </style>
""", unsafe_allow_html=True)

# ====================================================================
# 2. STRUKTUR DATA: NODE UNTUK GENERAL TREE
# ====================================================================
class TreeNode:
    def __init__(self, data, is_folder=True, ukuran_mb=0, url_asli_github=""):
        self.data = data
        self.is_folder = is_folder  
        self.ukuran_mb = ukuran_mb if not is_folder else 0 
        self.url_asli_github = url_asli_github if not is_folder else "" 
        self.children = []          
        self.parent = None          

    def add_child(self, child_node):
        child_node.parent = self    
        self.children.append(child_node)

    def remove_child(self, child_node):
        if child_node in self.children:
            self.children.remove(child_node)


class GeneralTree:
    def __init__(self, root_data):
        self.root = TreeNode(root_data, is_folder=True)

    def display_streamlit(self, node=None, level=0):
        if node is None: node = self.root
        ikon = "📁 " if node.is_folder else dapatkan_ikon_file(node.data)
        st.code("   " * level + f"└── {ikon}{node.data}", language="")
        for child in node.children:
            self.display_streamlit(child, level + 1)

    def cari_global(self, keyword, node=None, hasil=None):
        if node is None:
            node = self.root
            hasil = []
        if keyword.lower() in node.data.lower() and node != self.root:
            hasil.append(node)
        for child in node.children:
            self.cari_global(keyword, child, hasil)
        return hasil

    def hitung_statistik(self, node=None, stats=None):
        if node is None:
            node = self.root
            stats = {"folder": 0, "file": 0, "total_ukuran": 0}
        if node != self.root:
            if node.is_folder: stats["folder"] += 1
            else:
                stats["file"] += 1
                stats["total_ukuran"] += node.ukuran_mb
        for child in node.children:
            self.hitung_statistik(child, stats)
        return stats


# ====================================================================
# 3. FUNGSI PEMBANTU (UTILITIES)
# ====================================================================
def dapatkan_ikon_file(nama_file):
    if "." in nama_file:
        ekstensi = nama_file.split(".")[-1].lower()
        if ekstensi in ["pdf"]: return "📕 "
        if ekstensi in ["txt", "docx", "doc"]: return "📄 "
        if ekstensi in ["jpg", "jpeg", "png"]: return "🖼️ "
    return "📝 "

def dapatkan_path_list(node):
    path = []
    sementara = node
    while sementara is not None:
        path.insert(0, sementara)
        sementara = sementara.parent
    return path


# ====================================================================
# 4. INISIALISASI SESSION STATE (SINKRON DENGAN USERNAME KAMU)
# ====================================================================
if "sistem_file" not in st.session_state:
    sistem_file = GeneralTree("🖥️ Home")
    
    local_disk_c = TreeNode("🖴 Local Disk (C:)", is_folder=True)
    sistem_file.root.add_child(local_disk_c)

    dokumen = TreeNode("Dokumen", is_folder=True)
    download = TreeNode("Download", is_folder=True)
    local_disk_c.add_child(dokumen)
    local_disk_c.add_child(download)

    # Username asli kamu sudah terpasang rapi di sini
    username_github = "handini7642-beep" 

    # Jalur tembak ke PDF Asli milikmu
    dokumen.add_child(TreeNode(
        "Tugas_Struktur_Data.pdf", 
        is_folder=False, 
        ukuran_mb=12,
        url_asli_github=f"https://raw.githubusercontent.com/{username_github}/uas_file_eksplorer/main/Dokumen/Tugas_Struktur_Data.pdf"
    ))
    
    # Jalur tembak ke Catatan Teks Asli milikmu
    dokumen.add_child(TreeNode(
        "Catatan_Algoritma.txt", 
        is_folder=False, 
        ukuran_mb=2,
        url_asli_github=f"https://raw.githubusercontent.com/{username_github}/uas_file_eksplorer/main/Dokumen/Catatan_Algoritma.txt"
    ))
    
    # Jalur tembak ke Foto Asli milikmu
    download.add_child(TreeNode(
        "foto.jpg", 
        is_folder=False, 
        ukuran_mb=8,
        url_asli_github=f"https://raw.githubusercontent.com/{username_github}/uas_file_eksplorer/main/Download/foto.jpg"
    ))
    
    st.session_state.sistem_file = sistem_file
    st.session_state.current_node = sistem_file.root
    st.session_state.opened_file = None


# ====================================================================
# 5. ANTARMUKA UTAMA (STREAMLIT UI)
# ====================================================================

st.markdown("""
    <div style="background: linear-gradient(135deg, #4F46E5, #06B6D4); padding: 25px; border-radius: 15px; margin-bottom: 25px; color: white;">
        <h1 style='margin:0; font-weight: 700;'>🗃️ Smart File Explorer Kelompok</h1>
        <p style='margin:5px 0 0 0; opacity: 0.9;'>Aplikasi UAS Terintegrasi File Asli Cloud GitHub</p>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 📊 Status Penyimpanan")
    stats = st.session_state.sistem_file.hitung_statistik()
    
    maks_kapasitas = 100
    persen_terpakai = min(stats['total_ukuran'] / maks_kapasitas, 1.0)
    st.progress(persen_terpakai)
    st.caption(f"**{stats['total_ukuran']} MB** terpakai dari **{maks_kapasitas} MB**")
    
    col_stat1, col_stat2 = st.columns(2)
    col_stat1.metric("Folder", f"{stats['folder']}")
    col_stat2.metric("File", f"{stats['file']}")
    
    st.markdown("---")
    st.markdown("### 🔍 Pencarian Berkas")
    kata_kunci = st.text_input("Cari nama file/folder...", placeholder="Ketik nama berkas...")
    
    if kata_kunci:
        hasil_cari = st.session_state.sistem_file.cari_global(kata_kunci)
        if hasil_cari:
            for item in hasil_cari:
                tipe_str = "Folder" if item.is_folder else "File"
                if st.button(f"📍 Buka: {item.data} ({tipe_str})", key=f"search_{id(item)}", use_container_width=True):
                    if item.is_folder:
                        st.session_node = item
                        st.session_state.opened_file = None
                    else:
                        st.session_state.current_node = item.parent
                        st.session_state.opened_file = item
                    st.rerun()

# AREA NAVIGATION BREADCRUMBS
b_nodes = dapatkan_path_list(st.session_state.current_node)
cols_b = st.columns(len(b_nodes) * 2 - 1)

idx_col = 0
for i, node in enumerate(b_nodes):
    if cols_b[idx_col].button(node.data, key=f"breadcrumb_{id(node)}"):
        st.session_state.current_node = node
        st.session_state.opened_file = None
        st.rerun()
    idx_col += 1
    if idx_col < len(cols_b):
        cols_b[idx_col].write(" / ")
        idx_col += 1

st.markdown(" ")

# LAYOUT UTAMA PROGRAM
kolom_files, kolom_aksi = st.columns([2, 1])

with kolom_files:
    st.subheader(f"📂 Folder: {st.session_state.current_node.data}")
    
    if st.session_state.current_node.parent is not None:
        if st.button("🔙 Kembali", use_container_width=True):
            st.session_state.current_node = st.session_state.current_node.parent
            st.session_state.opened_file = None
            st.rerun()
            
    children_nodes = st.session_state.current_node.children
    if len(children_nodes) == 0:
        st.info("ℹ️ Folder ini kosong.")
    else:
        for child in children_nodes:
            ikon = "📁 " if child.is_folder else dapatkan_ikon_file(child.data)
            label_ukuran = "" if child.is_folder else f"({child.ukuran_mb} MB)"
            
            with st.container(border=True):
                if child.is_folder:
                    c1, c2 = st.columns([5, 1])
                    c1.markdown(f"#### {ikon} {child.data}", unsafe_allow_html=True)
                    with c2:
                        if st.button("Buka 📂", key=f"buka_{id(child)}", use_container_width=True):
                            st.session_state.current_node = child
                            st.session_state.opened_file = None
                            st.rerun()
                else:
                    c1, c2, c3 = st.columns([4, 1, 1])
                    c1.markdown(f"#### {ikon} {child.data} <span style='font-size:12px; color:gray;'>{label_ukuran}</span>", unsafe_allow_html=True)
                    
                    with c2:
                        if st.button("Buka 👁️", key=f"buka_file_{id(child)}", use_container_width=True):
                            st.session_state.opened_file = child
                            st.rerun()
                            
                    with c3:
                        st.markdown(f'<a href="{child.url_asli_github}" target="_blank"><button style="width:100%; background-color:#4F46E5; color:white; border:none; padding:6px; border-radius:5px; cursor:pointer;">Unduh 📥</button></a>', unsafe_allow_html=True)

    # AREA SCREEN VIEWER OUTPUT (PREVIEW)
    if st.session_state.opened_file is not None:
        st.markdown("---")
        st.markdown(f"### 🖥️ Preview File: `{st.session_state.opened_file.data}`")
        
        if st.session_state.opened_file.data.endswith(".txt"):
            try:
                respon = requests.get(st.session_state.opened_file.url_asli_github)
                konten_txt = respon.text
            except:
                konten_txt = "Gagal memuat isi catatan dari GitHub."
            st.markdown(f'<div class="file-content">{konten_txt}</div>', unsafe_allow_html=True)
            
        elif st.session_state.opened_file.data.endswith((".jpg", ".jpeg", ".png")):
            st.image(st.session_state.opened_file.url_asli_github, caption="Preview Foto dari GitHub", use_container_width=True)
            
        elif st.session_state.opened_file.data.endswith(".pdf"):
            st.success("📄 Dokumen ini adalah file PDF Asli.")
            st.markdown(f'Link baca langsung: [Buka PDF di Tab Baru]({st.session_state.opened_file.url_asli_github})')
            
        if st.button("Tutup Preview ❌"):
            st.session_state.opened_file = None
            st.rerun()

with kolom_aksi:
    st.subheader("⚙️ Pengelola")
    tab_tambah, tab_ubah, tab_hapus, tab_pohon = st.tabs(["📥 Tambah", "📝 Rename", "🗑️ Hapus", "🗂️ Structure"])
    
    with tab_tambah:
        nama_baru = st.text_input("Nama Baru:", key="add_name").strip()
        tipe = st.radio("Jenis:", ("Folder", "File"), horizontal=True)
        ukuran_input = st.number_input("Ukuran (MB):", min_value=1, value=2) if tipe == "File" else 0
        if st.button("Simpan", type="primary", use_container_width=True):
            if nama_baru:
                st.session_state.current_node.add_child(TreeNode(nama_baru, is_folder=(tipe == "Folder"), ukuran_mb=ukuran_input))
                st.rerun()
    with tab_ubah:
        if len(st.session_state.current_node.children) == 0: st.caption("Kosong.")
        else:
            opsi_ubah = [c.data for c in st.session_state.current_node.children]
            target_ubah = st.selectbox("Pilih Target:", opsi_ubah, key="select_rename")
            nama_ganti = st.text_input("Nama Ganti:", key="input_rename").strip()
            if st.button("Ubah Nama", use_container_width=True):
                if nama_ganti:
                    for child in st.session_state.current_node.children:
                        if child.data == target_ubah: child.data = nama_ganti; st.rerun()
    with tab_hapus:
        if len(st.session_state.current_node.children) == 0: st.caption("Kosong.")
        else:
            opsi_hapus = [c.data for c in st.session_state.current_node.children]
            target_hapus = st.selectbox("Pilih Hapus:", opsi_hapus, key="select_delete")
            if st.button("Hapus", type="primary", use_container_width=True):
                for child in st.session_state.current_node.children:
                    if child.data == target_hapus:
                        if st.session_state.opened_file == child: st.session_state.opened_file = None
                        st.session_state.current_node.remove_child(child)
                        st.rerun()
    with tab_pohon:
        st.session_state.sistem_file.display_streamlit()
