#"Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Konfigurasi halaman
st.set_page_config(page_title="Statistika | Analisis Distribusi", 
                   page_icon=':bar_chart:',
                   layout="wide")

st.title("📊 Statistika: Analisis Distribusi Frekuensi")
st.markdown("Unggah file Excel Anda untuk melihat datanya dalam tabel interaktif.")
st.write("Format : ")
st.image('format-data.png',width=500)

@st.cache_data
def load_data(file):
    data = pd.read_excel(file)
    return data

def header():
    # Komponen untuk mengunggah file
    uploaded_file = st.file_uploader("Pilih file Excel", type=['xlsx', 'xls'])

    if uploaded_file is None:
        st.info("Silakan unggah file untuk memulai.")
    else :
        try:
            # Membaca data Excel menggunakan Pandas
            df = load_data(uploaded_file)
            
            # Menampilkan informasi dasar
            st.success("File berhasil diunggah!")
            Body(df)
                
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

def Body(df):
    #-------DATA TABEL-------
    # Menampilkan tabel interaktif (bisa di-sort dan di-search)
    st.write('')
    st.subheader("Data Tabel")
    with st.expander("Data Preview") :
        df = st.data_editor(df, width='stretch')
    
    #-------TABEL DISTRIBUSI-------
    st.write('')
    st.subheader("Tabel Distribusi")
    # Ambil daftar semua nama kolom
    numbertype_columns = df.select_dtypes(include=['number']).columns.tolist()
    selected_columns = st.selectbox(
        "Pilih kolom yang ingin dihitung : (Hanya dapat memilih tipe data angka saja)",
        options=[None] + numbertype_columns,
        format_func=lambda x: "--- Pilih Kolom ---" if x is None else x,
        key="col2"
    )
    # Filter dataframe berdasarkan pilihan user
    if selected_columns != None:
        data = df[selected_columns].dropna()
        st.info(f"Total data : {len(data)}")

        kiri, tengah, kanan = st.columns(3)
        with kiri :
            min_val, max_val = data.min(), data.max()
            range_value = max_val - min_val
            st.metric("Jangkauan (R)", f"{range_value:,.2f}")
            st.markdown("**Langkah-langkah:**")
            col1, col2 = st.columns([1, 1]) # Membagi layar jadi 2 bagian
            with col1:
                st.latex(fr'''
                \begin{{aligned}}
                    R &= X_{{max}} - X_{{min}} \\
                    R &= {max_val} - {min_val} \\
                    R &= \mathbf{{{range_value}}}
                \end{{aligned}}
                ''')

        with tengah:
            n = len(data)
            k_raw = 1 + 3.322 * np.log10(n)
            k_final = int(np.ceil(k_raw))
            st.metric("Banyak Kelas (k)", k_final)
            st.markdown("**Langkah-langkah:**")
            col1, col2 = st.columns([1, 1]) # Membagi layar jadi 2 bagian
            with col1:
                st.latex(fr'''
                \begin{{aligned}}
                    k &= 1 + 3.3 \log_{{10}}({n}) \\
                    k &= {k_raw:.2f} \\
                    k &\approx \mathbf{{{k_final}}}
                \end{{aligned}}
                ''')

        with kanan:
            p_raw = range_value / k_final
            p_final = int(np.ceil(p_raw))
            st.metric("Panjang Kelas (p)", p_final)
            st.markdown("**Langkah-langkah:**")
            col1, col2 = st.columns([1, 1]) # Membagi layar jadi 2 bagian
            with col1:
                st.latex(fr'''
                \begin{{aligned}}
                    p &= \frac{{R}}{{k}} \\
                    p &= \frac{{{range_value}}}{{{k_final}}} \\
                    p &= {p_raw:.2f} \\
                    p &\approx \mathbf{{{p_final}}}
                \end{{aligned}}
                ''')
        
        st.write("Tabel Distribusi Frekuensi")
        # 1. Menentukan batas-batas (bins)
        bins = [data.min() + i * p_final for i in range(k_final + 1)]

        # 2. Membuat label interval
        labels = [f"{int(bins[i])} - {int(bins[i+1]-1)}" for i in range(len(bins)-1)]

        # 3. Menghitung frekuensi
        df_dist = pd.cut(data, bins=bins, labels=labels, include_lowest=True).value_counts().sort_index().reset_index()
        df_dist.columns = ['Interval Kelas', 'Frekuensi (f)']
        df_dist.insert(0, 'Kelas', range(1, len(df_dist) + 1)) 
        total_n = df_dist['Frekuensi (f)'].sum()
        df_dist['Frekuensi Relatif (%)'] = (df_dist['Frekuensi (f)'] / total_n * 100).round(2)
        df_dist['Fk. Kurang Dari'] = df_dist['Frekuensi (f)'].cumsum()
        df_dist['Fk. Lebih Dari'] = total_n - df_dist['Fk. Kurang Dari'] + df_dist['Frekuensi (f)']

        # Merapikan Urutan Kolom
        kolom_rapi = [
            'Kelas', 'Interval Kelas', 'Frekuensi (f)', 'Frekuensi Relatif (%)',
            'Fk. Kurang Dari', 'Fk. Lebih Dari'
        ]
        df_dist = df_dist[kolom_rapi]

        total_row = pd.DataFrame({
            'Kelas': ['TOTAL :'],
            'Interval Kelas': ['-'],
            'Frekuensi (f)': [total_n],
            'Frekuensi Relatif (%)': [100.00],
            'Fk. Kurang Dari': ['-'],
            'Fk. Lebih Dari': ['-']
        })

        # Gabungkan tabel dengan baris total
        df_display = pd.concat([df_dist, total_row], ignore_index=True)

        # Ubah tipe data ke string untuk keperluan display
        df_display['Kelas'] = df_display['Kelas'].astype(str)
        df_display['Fk. Kurang Dari'] = df_display['Fk. Kurang Dari'].astype(str)
        df_display['Fk. Lebih Dari'] = df_display['Fk. Lebih Dari'].astype(str)

        # Tampilkan Tabel
        st.dataframe(
            df_display, 
            width='stretch',            # Agar tabel selebar halaman
            height=300,                 # Tinggi dalam pixel (sesuaikan kebutuhan)
            hide_index=True,            # Agar lebih rapi tanpa nomor urut tambahan
            column_config={
                "Frekuensi Relatif (%)": st.column_config.NumberColumn(
                "Frekuensi Relatif (%)",
                format="%.2f%%"  
                )
            }
        )
    else:
        st.warning("Silakan pilih setidaknya satu kolom.")
    
    #-------GRAFIK HISTOGRAM-------
    st.write('')
    st.subheader("Grafik Histogram")
    if selected_columns == None:
        st.write("Grafik menyesuaikan pilihan kolom tabel distribusi yang ingin di hitung.")
    else:
        # 1. Hitung Titik Tengah untuk Poligon
        midpoints = [(bins[i] + bins[i+1]) / 2 for i in range(len(bins)-1)]
        # 2. Hitung Batas Bawah dan Batas Atas untuk Ogif
        # Batas bawah pertama ditambahkan frekuensi 0 agar kurva mulai dari garis x
        ogif_x = [bins[0]] + [b for b in bins[1:]]
        ogif_y_kurang = [0] + df_dist['Fk. Kurang Dari'].tolist()
        ogif_y_lebih = [total_n] + (total_n - df_dist['Fk. Kurang Dari']).tolist()
        
        kiri, kanan = st.columns([2, 1]) 
        with kiri :
            st.write("Histogram dan Poligon Frekuensi")
            fig = go.Figure()
            # 1. Tambahkan Histogram (Bar)
            fig.add_trace(go.Bar(
                x=midpoints,
                y=df_dist['Frekuensi (f)'],
                name='Histogram',
                marker_color="#65DB50",
                marker_line_color="green",
                marker_line_width=1,
                customdata=labels, # Memasukkan label interval ke hover
                hovertemplate="<br>".join([
                    "Interval: %{customdata}",
                    "Frekuensi: %{y}",
                    "Titik Tengah: %{x}"
                ])
            ))
            # 2. Tambahkan Poligon (Line)
            fig.add_trace(go.Scatter(
                x=midpoints,
                y=df_dist['Frekuensi (f)'],
                mode='lines+markers',
                name='Poligon',
                line=dict(color="#2F7425", width=2),
                hoverinfo='skip' # Agar tidak tumpang tindih dengan hover histogram
            ))
            # Pengaturan Layout
            fig.update_layout(
                plot_bgcolor='white',   
                paper_bgcolor='white',  
                # 2. Pengaturan Font Global (PASTIKAN HANYA ADA SATU)
                font=dict(color='black'), # Semua tulisan jadi HITAM
                # 3. Pengaturan Sumbu & Grid (Garis Titik-titik)
                xaxis=dict(
                    tickvals=midpoints, # atau ogif_x jika di fig2
                    title=dict(text="Batas Kelas", font=dict(color='black')),
                    tickfont=dict(color='black'),
                    showgrid=True,          
                    gridcolor='lightgrey',  
                    gridwidth=0.5,
                    griddash='dot',         
                    showline=True,          
                    linecolor='black',      
                    mirror=True             
                ),
                yaxis=dict(
                    title=dict(text="Frekuensi Kumulatif", font=dict(color='black')),
                    tickfont=dict(color='black'),
                    showgrid=True,          
                    gridcolor='lightgrey',
                    gridwidth=0.5,
                    griddash='dot',
                    showline=True,          
                    linecolor='black',      
                    mirror=True             
                ),
                # 4. Legend
                legend=dict(
                    font=dict(color='black'),
                    bordercolor="lightgrey",
                    borderwidth=1,
                    orientation="v",         
                    yanchor="middle", 
                    y=0.5, 
                    xanchor="right", 
                    x=0.98
                ),
                margin=dict(l=50, r=20, t=50, b=50),
                height=450,
                hovermode="x unified"
            )
            # Tampilkan di Streamlit
            st.plotly_chart(fig, width='stretch')

        kiri, kanan = st.columns([2, 1]) 
        with kiri :
            st.write("Kurva Ogif (Kumulatif)")
            fig2 = go.Figure()
            # 1. Ogif Positif (Fk Kurang Dari) - Marker Bulat, Garis Solid
            fig2.add_trace(go.Scatter(
                x=ogif_x, 
                y=ogif_y_kurang,
                mode='lines+markers',
                name='Ogif Positif (Fk <)',
                line=dict(color='green', width=3),
                marker=dict(symbol='circle', size=8)
            ))
            # 2. Ogif Negatif (Fk Lebih Dari) - Marker Kotak, Garis Putus-putus
            fig2.add_trace(go.Scatter(
                x=ogif_x, 
                y=ogif_y_lebih,
                mode='lines+markers',
                name='Ogif Negatif (Fk >)',
                line=dict(color='#5EC14D', width=3, dash='dash'),
                marker=dict(symbol='square', size=8)
            ))
            # 3. Layout (Tema Putih, Teks Hitam, Grid Titik-titik)
            fig2.update_layout(
                plot_bgcolor='white',   
                paper_bgcolor='white',  
                font=dict(color='black'), # Pastikan teks hitam
                xaxis=dict(
                    title="Batas Kelas",
                    tickvals=ogif_x,
                    showgrid=True,
                    gridcolor='lightgrey',
                    griddash='dot', # Garis grid titik-titik
                    showline=True,
                    linecolor='black',
                    mirror=True # Membuat bingkai kotak
                ),
                yaxis=dict(
                    title="Frekuensi Kumulatif",
                    showgrid=True,
                    gridcolor='lightgrey',
                    griddash='dot',
                    showline=True,
                    linecolor='black',
                    mirror=True # Membuat bingkai kotak
                ),
                legend=dict(
                    bordercolor="lightgrey",
                    borderwidth=1,
                    orientation="h",      # Horizontal seperti aslinya
                    yanchor="bottom", 
                    y=1.02, 
                    xanchor="right", 
                    x=1
                ),
                margin=dict(l=50, r=20, t=50, b=50),
                height=500,
                hovermode="x unified"
            )
            # Tampilkan di Streamlit
            st.plotly_chart(fig2, width='stretch', theme=None)
            
if __name__ == "__main__":
    header()



# current_selection = "-".join(selected_columns)
# if "last_selection" not in st.session_state or st.session_state.last_selection != current_selection:
#     st.session_state.button_clicked = False
#     st.session_state.last_selection = current_selection
# if not st.session_state.button_clicked:
#     filtered_df = df[selected_columns]
#     st.dataframe(filtered_df, width='stretch')
#     if st.button("Buat Tabel Distribusi"):
#         st.session_state.button_clicked = True
#         st.rerun()
# if not st.session_state.button_clicked:

                # title="Histogram & Poligon Frekuensi Interaktif",
                # xaxis=dict(title="Interval Kelas", tickvals=midpoints, ticktext=labels),
                # yaxis=dict(title="Frekuensi"),
                # plot_bgcolor='#f0f2f6',
                # hovermode="x unified", # Menampilkan hover secara vertikal sejajar sumbu X
                # template="plotly_white",
                # height=450, # Bisa atur tinggi di sini
                # margin=dict(l=20, r=20, t=50, b=20)

                            # 
            # fig1, ax1 = plt.subplots(figsize=(10, 5))
            # # Plot Histogram
            # ax1.bar(midpoints, df_dist['Frekuensi (f)'], width=p_final, 
            #         color='#5EC14D', edgecolor='green', alpha=0.7, label='Histogram')
            # # Plot Poligon (Garis)
            # ax1.plot(midpoints, df_dist['Frekuensi (f)'], marker='o', 
            #         color='#13BE13', linewidth=2, label='Poligon Frekuensi')
            # ax1.set_xlabel("Interval Kelas")
            # ax1.set_ylabel("Frekuensi")
            # ax1.set_xticks(midpoints)
            # ax1.set_xticklabels(labels, rotation=45)
            # ax1.legend()
            # ax1.grid(axis='y', linestyle='--', alpha=0.7)
            # st.pyplot(fig1)

                        # fig2, ax2 = plt.subplots(figsize=(10, 5))
            # # Ogif Positif (Fk Kurang Dari)
            # ax2.plot(ogif_x, ogif_y_kurang, marker='o', linestyle='-', 
            #         color='green', label='Ogif Positif (Fk Kurang Dari)')
            # # Ogif Negatif (Fk Lebih Dari)
            # ax2.plot(ogif_x, ogif_y_lebih, marker='s', linestyle='--', 
            #         color='#5EC14D', label='Ogif Negatif (Fk Lebih Dari)')
            # ax2.set_xlabel("Batas Kelas")
            # ax2.set_ylabel("Frekuensi Kumulatif")
            # ax2.set_xticks(ogif_x)
            # ax2.legend()
            # ax2.grid(True, linestyle=':', alpha=0.6)
            # st.pyplot(fig2)