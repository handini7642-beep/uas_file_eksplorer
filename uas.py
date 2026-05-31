import streamlit as st
import io

# ====================================================================
# 1. KONFIGURASI HALAMAN & STYLE CSS
# ====================================================================
st.set_page_config(page_title="File Explorer Pro", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #f8f9fa;
    }
    div[data-testid="stCard"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e9ecef;
        transition: transform 0.2s;
    }
    div[data-testid="stCard"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
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
    def __init__(self, data, is_folder=True, ukuran_mb=0, konten_simulasi=""):
        self.data = data
        self.is_folder = is_folder  
        self.ukuran_mb = ukuran_mb if not is_folder else 0 
        self.konten_simulasi = konten_simulasi if not is_folder else "" 
        self.is_favorite = False    
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
        if node is None:
            node = self.root
        ikon = "📁 " if node.is_folder else dapatkan_ikon_file(node.data)
        fav = " ⭐" if node.is_favorite else ""
        st.code("   " * level + f"└── {ikon}{node.data}{fav}", language="")
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

    def dapatkan_semua_favorit(self, node=None, hasil=None):
        if node is None:
            node = self.root
            hasil = []
        if node.is_favorite:
            hasil.append(node)
        for child in node.children:
            self.dapatkan_semua_favorit(child, hasil)
        return hasil

    def hitung_statistik(self, node=None, stats=None):
        if node is None:
            node = self.root
            stats = {"folder": 0, "file": 0, "total_ukuran": 0}
        if node != self.root:
            if node.is_folder:
                stats["folder"] += 1
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
        if ekstensi in ["jpg", "jpeg", "png", "gif"]: return "🖼️ "
        if ekstensi in ["mp4", "mkv"]: return "🎬 "
        if ekstensi in ["mp3"]: return "🎵 "
        if ekstensi in ["zip", "rar"]: return "📦 "
    return "📝 "

def dapatkan_path_list(node):
    path = []
    sementara = node
    while sementara is not None:
        path.insert(0, sementara)
        sementara = sementara.parent
    return path

def tentukan_mime_type(nama_file):
    ekstensi = nama_file.split(".")[-1].lower() if "." in nama_file else ""
    if ekstensi == "pdf": return "application/pdf"
    if ekstensi in ["jpg", "jpeg"]: return "image/jpeg"
    if ekstensi == "png": return "image/png"
    return "text/plain"


# ====================================================================
# 4. INISIALISASI SESSION STATE (MENGGUNAKAN STRUKTUR SINKRON GITHUB)
# ====================================================================
if "sistem_file" not in st.session_state:
    sistem_file = GeneralTree("🖥️ Home")
    
    local_disk_c = TreeNode("🖴 Local Disk (C:)", is_folder=True)
    sistem_file.root.add_child(local_disk_c)

    dokumen = TreeNode("Dokumen", is_folder=True)
    download = TreeNode("Download", is_folder=True)
    local_disk_c.add_child(dokumen)
    local_disk_c.add_child(download)

    # Inisialisasi file Dokumen sesuai milikmu di GitHub
    dokumen.add_child(TreeNode(
        "Tugas_Struktur_Data.pdf", 
        is_folder=False, 
        ukuran_mb=12,
        konten_simulasi="=== [DOKUMEN PDF DIGITAL] ===\nTugas Kuliah Kelompok: Implementasi Non-Linear Data Structure (Tree)\nStatus File: Sukses diverifikasi secara online di internet."
    ))
    dokumen.add_child(TreeNode(
        "Catatan_Algoritma.txt", 
        is_folder=False, 
        ukuran_mb=2,
        konten_simulasi="Catatan Kelompok Belajar Algoritma:\n- Representasi silsilah folder menggunakan tipe General Tree.\n- Setiap folder bertindak sebagai Parent, dan isinya bertindak sebagai Children."
    ))
    
    # Sinkronisasi penuh dengan nama file foto.jpg barumu di GitHub
    download.add_child(TreeNode(
        "foto.jpg", 
        is_folder=False, 
        ukuran_mb=8,
        konten_simulasi="=== [IMAGE PREVIEW] ===\n[ Berkas: foto.jpg ]\nFormat berkas berhasil dibaca dari direktori online GitHub Kelompok."
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
        <p style='margin:5px 0 0 0; opacity: 0.9;'>Aplikasi UAS Struktur Data Terintegrasi Cloud</p>
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
                        st.session_state.current_node = item
                        st.session_state.opened_file = None
                    else:
                        st.session_state.current_node = item.parent
                        st.session_state.opened_file = item
                    st.rerun()
        else:
            st.error("Item tidak ditemukan.")
            
    st.markdown("---")
    st.markdown("### ⭐ Koleksi Favorit")
    list_fav = st.session_state.sistem_file.dapatkan_semua_favorit()
    if not list_fav:
        st.caption("Belum ada berkas favorit.")
    else:
        for fav_node in list_fav:
            ikon_fav = "📁 " if fav_node.is_folder else dapatkan_ikon_file(fav_node.data)
            if st.button(f"{ikon_fav} {fav_node.data}", key=f"fav_{id(fav_node)}", use_container_width=True):
                if fav_node.is_folder:
                    st.session_state.current_node = fav_node
                    st.session_state.opened_file = None
                else:
                    st.session_state.current_node = fav_node.parent
                    st.session_state.opened_file = fav_node
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
    st.subheader(f"📂 Direktori Aktif: {st.session_state.current_node.data}")
    
    if st.session_state.current_node.parent is not None:
        if st.button("🔙 Kembali ke Folder Sebelumnya", use_container_width=True):
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
            fav_status = "⭐" if child.is_favorite else "☆"
            
            with st.container(border=True):
                if child.is_folder:
                    c1, c2, c3 = st.columns([4, 1, 1])
                    c1.markdown(f"#### {ikon} {child.data}", unsafe_allow_html=True)
                    
                    with c2:
                        if st.button(f"{fav_status} Favorit", key=f"fav_btn_{id(child)}", use_container_width=True):
                            child.is_favorite = not child.is_favorite
                            st.rerun()
                    with c3:
                        if st.button("Buka 📂", key=f"buka_{id(child)}", use_container_width=True):
                            st.session_state.current_node = child
                            st.session_state.opened_file = None
                            st.rerun()
                else:
                    c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
                    c1.markdown(f"#### {ikon} {child.data} <span style='font-size:12px; color:gray;'>{label_ukuran}</span>", unsafe_allow_html=True)
                    
                    with c2:
                        if st.button(f"{fav_status} Favorit", key=f"fav_btn_{id(child)}", use_container_width=True):
                            child.is_favorite = not child.is_favorite
                            st.rerun()
                    with c3:
                        if st.button("Lihat 👁️", key=f"buka_file_{id(child)}", use_container_width=True):
                            st.session_state.opened_file = child
                            st.rerun()
                    with c4:
                        # PROSES DOWNLOAD ASLI FILE
                        file_buffer = io.BytesIO(child.konten_simulasi.encode('utf-8'))
                        st.download_button(
                            label="Unduh 📥",
                            data=file_buffer,
                            file_name=child.data,
                            mime=tentukan_mime_type(child.data),
                            key=f"dl_real_{id(child)}",
                            use_container_width=True
                        )

    # AREA SCREEN VIEWER OUTPUT (PREVIEW FILE)
    if st.session_state.opened_file is not None:
        st.markdown("---")
        st.markdown(f"### 🖥️ Viewer Output File: `{st.session_state.opened_file.data}`")
        st.markdown(f"""
        <div class="file-content">{st.session_state.opened_file.konten_simulasi}</div>
        """, unsafe_allow_html=True)
        if st.button("Tutup File Preview ❌"):
            st.session_state.opened_file = None
            st.rerun()

with kolom_aksi:
    st.subheader("⚙️ Pengelola Berkas")
    
    tab_tambah, tab_ubah, tab_hapus, tab_pohon = st.tabs(["📥 Tambah Berkas", "📝 Rename", "🗑️ Hapus", "🗂️ File Structure"])
    
    with tab_tambah:
        nama_baru = st.text_input("Nama Berkas/Folder Baru:", key="add_name").strip()
        tipe = st.radio("Jenis Objek:", ("Folder", "File"), horizontal=True)
        
        ukuran_input = 0
        if tipe == "File":
            ukuran_input = st.number_input("Ukuran Berkas (MB):", min_value=1, max_value=50, value=2)
            
        if st.button("Simpan Data Baru", type="primary", use_container_width=True):
            if not nama_baru:
                st.error("Nama tidak boleh kosong!")
            elif any(c.data.lower() == nama_baru.lower() for c in st.session_state.current_node.children):
                st.error("Nama sudah terpakai!")
            elif tipe == "File" and (stats['total_ukuran'] + ukuran_input > maks_kapasitas):
                st.error("❌ Gagal! Penyimpanan penuh, tidak muat.")
            else:
                is_folder_bool = (tipe == "Folder")
                konten_def = f"=== OUTPUT FILE BARU ===\nNama Dokumen: {nama_baru}\nStatus Berkas: Berhasil dibuat secara dinamis di memori." if not is_folder_bool else ""
                st.session_state.current_node.add_child(TreeNode(
                    nama_baru, 
                    is_folder=is_folder_bool, 
                    ukuran_mb=ukuran_input, 
                    konten_simulasi=konten_def
                ))
                st.success(f"Berhasil membuat {tipe.lower()} '{nama_baru}'")
                st.rerun()

    with tab_ubah:
        if len(st.session_state.current_node.children) == 0:
            st.caption("Kosong.")
        else:
            opsi_ubah = [c.data for c in st.session_state.current_node.children]
            target_ubah = st.selectbox("Pilih Objek:", opsi_ubah, key="select_rename")
            nama_ganti = st.text_input("Ketik Nama Baru:", key="input_rename").strip()
            
            if st.button("Ubah Nama Sekarang", use_container_width=True):
                if nama_ganti and not any(c.data.lower() == nama_ganti.lower() for c in st.session_state.current_node.children):
                    for child in st.session_state.current_node.children:
                        if child.data == target_ubah:
                            child.data = nama_ganti
                            st.rerun()

    with tab_hapus:
        if len(st.session_state.current_node.children) == 0:
            st.caption("Kosong.")
        else:
            opsi_hapus = [c.data for c in st.session_state.current_node.children]
            target_hapus = st.selectbox("Pilih Objek:", opsi_hapus, key="select_delete")
            
            if st.button("Hapus Permanen", type="primary", use_container_width=True):
                for child in st.session_state.current_node.children:
                    if child.data == target_hapus:
                        if st.session_state.opened_file == child:
                            st.session_state.opened_file = None
                        st.session_state.current_node.remove_child(child)
                        st.rerun()
                        
    with tab_pohon:
        st.write("Visualisasi Logika Rekursif General Tree:")
        st.session_state.sistem_file.display_streamlit()
