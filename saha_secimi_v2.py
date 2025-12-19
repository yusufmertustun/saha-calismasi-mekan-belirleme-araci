# -*- coding: utf-8 -*-
import streamlit as st
from fpdf import FPDF
import datetime
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- YARDIMCI: Türkçe Karakter Temizleyici ---
def tr_to_en(text):
    if text is None: return ""
    tr_map = {"ı": "i", "İ": "I", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ş": "s", "Ş": "S", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
    text = str(text)
    for tr, en in tr_map.items():
        text = text.replace(tr, en)
    return text

# --- GRAFİK OLUŞTURUCU ---
def create_radar_chart(categories, values, saha_ismi):
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    values += values[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    plt.xticks(angles[:-1], categories, color='black', size=9)
    ax.set_rlabel_position(0)
    plt.yticks([1, 2, 3, 4, 5], ["1", "2", "3", "4", "5"], color="grey", size=7)
    plt.ylim(0, 5)
    
    line_color = '#1E88E5'
    fill_color = '#42A5F5'
    
    ax.plot(angles, values, linewidth=2, linestyle='solid', color=line_color)
    ax.fill(angles, values, fill_color, alpha=0.3)
    plt.title(f"{saha_ismi} - Uygunluk Grafigi", size=14, color='black', y=1.1)
    
    chart_path = "temp_chart.png"
    plt.savefig(chart_path, bbox_inches='tight', dpi=100)
    plt.close()
    return chart_path, fig

# --- PDF OLUŞTURUCU ---
def create_pdf(saha_info, results_text, categories_dict, user_scores, omitted_items, observation_note, chart_path, lat, lon):
    pdf = FPDF()
    pdf.add_page()
    
    # Başlık
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=tr_to_en("SAHA CALISMASI DEGERLENDIRME RAPORU"), ln=True, align='C')
    pdf.set_font("Arial", "I", 10)
    pdf.cell(200, 5, txt=tr_to_en("Ortaogretim Cografya Dersleri - Gunubirlik Saha Calismasi"), ln=True, align='C')
    
    # Saha Bilgileri
    pdf.set_font("Arial", size=11)
    pdf.ln(10)
    for key, value in saha_info.items():
        pdf.cell(200, 7, txt=tr_to_en(f"{key}: {value}"), ln=True)
    
    # Konum Bilgisi ve Link
    if lat != 0 and lon != 0:
        pdf.set_text_color(0, 0, 255)
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"
        pdf.cell(200, 7, txt=f"Konum: {lat}, {lon} (Haritada Goruntulemek Icin Tiklayin)", ln=True, link=maps_link)
        pdf.set_text_color(0, 0, 0)
    
    # Grafiği Ekle
    if chart_path:
        pdf.image(chart_path, x=130, y=35, w=70)
    
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)
    
    # Sonuç Metni
    pdf.set_font("Arial", "B", 11)
    pdf.multi_cell(0, 8, txt=tr_to_en(f"GENEL DEGERLENDIRME SONUCU: {results_text}"))
    pdf.ln(5)
    
    if observation_note:
        pdf.set_font("Arial", "I", 10)
        pdf.multi_cell(0, 8, txt=tr_to_en(f"GOZLEM VE ONERILER: {observation_note}"))
        pdf.ln(5)

    # Detaylar
    i = 0
    score_idx = 0
    for cat, items in categories_dict.items():
        pdf.set_font("Arial", "B", 10)
        pdf.cell(200, 6, txt=tr_to_en(cat.upper()), ln=True)
        pdf.set_font("Arial", size=9)
        for item in items.keys():
            clean_item = tr_to_en(item)
            if item not in omitted_items:
                pdf.cell(200, 5, txt=f"- {clean_item}: {user_scores[score_idx]}/5", ln=True)
                score_idx += 1
            else:
                pdf.cell(200, 5, txt=f"- {clean_item}: -- (Degerlendirme Disi)", ln=True)
        pdf.ln(2)
        
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- UYGULAMA BAŞLANGICI ---
st.set_page_config(page_title="Saha Değerlendirme Formu", layout="wide")

st.header("Saha Çalışması Uygunluk Değerlendirme Formu")

# --- AÇIKLAMA METNİ ---
st.markdown("""
<div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 5px solid #1E88E5;'>
    <strong>FORMUN AMACI:</strong> Bu değerlendirme aracı, 
    <em>Ortaöğretim Coğrafya Dersleri Öğretim Programı</em> kapsamında gerçekleştirilmesi planlanan 
    <strong>günübirlik saha/arazi çalışmaları</strong> için belirlenen lokasyonların eğitsel, lojistik ve güvenlik 
    standartlarına uygunluğunu değerlendirmek amacıyla <strong>Arş. Gör. Yusuf Mert Üstün</strong> tarafından 
    AI kullanılarak hazırlanmıştır.
</div>
""", unsafe_allow_html=True)
st.write("") 

st.sidebar.markdown("### Puanlama Rehberi")
st.sidebar.info("1: Hiç Uygun Değil\n3: Kısmen Uygun\n5: Tamamen Uygun")

# --- GİRİŞ BİLGİLERİ VE TIKLANABİLİR HARİTA ---
with st.expander("📍 Saha Kimlik ve Konum Seçimi", expanded=True):
    col1, col2, col3 = st.columns(3)
    saha_ismi = col1.text_input("Saha/Lokasyon İsmi", "Saha Adi Giriniz")
    degerlendiren = col2.text_input("Değerlendirmeyi Yapan")
    tarih = col3.date_input("Tarih", datetime.date.today())
    
    st.write("---")
    st.markdown("**Konum Seçimi:** Harita üzerinde saha çalışması yapılacak noktaya tıklayınız.")
    
    col_map, col_info = st.columns([3, 1])
    
    with col_map:
        if 'lat' not in st.session_state:
            st.session_state.lat = 41.0082
        if 'lon' not in st.session_state:
            st.session_state.lon = 28.9784
            
        m = folium.Map(location=[st.session_state.lat, st.session_state.lon], zoom_start=6)
        
        if st.session_state.lat != 41.0082:
             folium.Marker(
                [st.session_state.lat, st.session_state.lon], 
                popup="Seçilen Saha", 
                tooltip="Seçilen Saha"
            ).add_to(m)

        output = st_folium(m, width=700, height=400)

        if output['last_clicked']:
            st.session_state.lat = output['last_clicked']['lat']
            st.session_state.lon = output['last_clicked']['lng']
    
    with col_info:
        st.info("Seçilen Koordinatlar:")
        st.metric("Enlem", f"{st.session_state.lat:.5f}")
        st.metric("Boylam", f"{st.session_state.lon:.5f}")
        lat = st.session_state.lat
        lon = st.session_state.lon

# Kategoriler
categories = {
    "Müfredat ve İçerik": {
        "Kazanımlarla Uyum*": "Müfredat kazanımlarını sahada somutlaştırma imkanı.", 
        "Merak Uyandırma": "Öğrencide ilgi ve keşif duygusu oluşturma potansiyeli."
    },
    "Ulaşım ve Erişim": {
        "Yol Güvenliği": "Yolun fiziki yapısı (viraj, asfalt kalitesi vb.).", 
        "Trafik Yoğunluğu": "Gidiş-dönüş güzergahındaki trafik riski.", 
        "Mesafe Uygunluğu*": "Günübirlik gezi sınırları içinde kalma durumu.", 
        "Araç Park İmkanı": "Otobüs/servis için güvenli park alanı."
    },
    "Temel Altyapı": {
        "Yeme-İçme Tesisleri**": "Hijyenik ve erişilebilir beslenme alanları.", 
        "Su Erişimi": "Temiz içme suyuna ulaşım.", 
        "Toplanma Alanı": "Brifing ve dinlenme için uygun düzlük alan.", 
        "Tuvalet İmkanı": "Temiz ve yeterli WC kapasitesi.", 
        "İletişim Ağı": "Telefon ve internet çekim gücü.", 
        "Engelli Erişimi***": "Özel gereksinimli bireyler için fiziksel uygunluk."
    },
    "Güvenlik ve Riskler": {
        "Doğal Riskler*": "Heyelan, uçurum, kaya düşmesi vb. risklerin yokluğu.", 
        "Beşeri Riskler*": "Trafik, asayiş vb. dış tehditlerin yokluğu.", 
        "Sağlık Riskleri*": "Alerjen bitki, haşere vb. risklerin düşüklüğü.", 
        "Acil Yardım Erişimi": "En yakın sağlık kuruluşuna ulaşım süresi."
    }
}

all_scores = []
cat_averages = []
cat_names = []
critical_fails = []
omitted_items = []

st.divider()

col_left, col_right = st.columns([1, 1])

with col_left:
    for cat_name, items in categories.items():
        st.subheader(cat_name)
        cat_scores_temp = []
        for item, help_text in items.items():
            if "**" in item or "***" in item:
                if st.checkbox(f"{item} - İhtiyaç Yok", key=f"skip_{item}"):
                    omitted_items.append(item)
                    continue
            val = st.slider(item, 1, 5, 3, help=help_text)
            all_scores.append(val)
            cat_scores_temp.append(val)
            if "*" in item and val < 3:
                critical_fails.append(item)
        
        if cat_scores_temp:
            cat_avg = sum(cat_scores_temp) / len(cat_scores_temp)
            cat_averages.append(cat_avg)
            cat_names.append(tr_to_en(cat_name))
        else:
            cat_averages.append(0)
            cat_names.append(cat_name)

with col_right:
    st.markdown("### Analiz Grafiği")
    if cat_averages:
        chart_path, fig = create_radar_chart(cat_names, list(cat_averages), saha_ismi)
        st.pyplot(fig)
    st.write("")
    observation_note = st.text_area("Gözlem Notları ve Öneriler", height=150)

st.divider()

# --- BUTON KISMI SADELEŞTİRİLDİ ---
if st.button("Analizi Tamamla ve Rapor Oluştur", type="primary"):
    if not all_scores:
        st.error("Lütfen puanlama yapınız.")
    else:
        total_avg = sum(all_scores) / len(all_scores)
        
        # Sonuç Belirleme
        if critical_fails:
            status_text = "UYGUN DEGIL (Kritik Guvenlik/Erisim Riskleri Mevcut)"
            st.error(f"SONUÇ: {status_text}", icon="⛔")
        elif total_avg >= 4:
            status_text = "UYGUN (Saha Calismasi Icin Elverisli)"
            st.success(f"SONUÇ: {status_text}", icon="✅")
        elif total_avg >= 3:
            status_text = "KISMEN UYGUN (Gelistirilebilir/Onlem Gerektirir)"
            st.warning(f"SONUÇ: {status_text}", icon="⚠️")
        else:
            status_text = "UYGUN DEGIL (Yetersiz Altyapi/Icerik)"
            st.error(f"SONUÇ: {status_text}", icon="❌")
            
        st.info(f"Genel Puan: {total_avg:.2f} / 5")
        
        # --- PDF OLUŞTURMA (Excel kısmı çıkarıldı) ---
        info = {"Saha": saha_ismi, "Uzman": degerlendiren, "Tarih": tarih, "Puan": f"{total_avg:.2f}"}
        pdf_bytes = create_pdf(info, status_text, categories, all_scores, omitted_items, observation_note, chart_path, lat, lon)
        
        st.download_button(
            label="📄 PDF Raporunu İndir",
            data=pdf_bytes,
            file_name=f"Rapor_{saha_ismi}.pdf",
            mime="application/pdf"
        )
        
        if os.path.exists("temp_chart.png"):
            os.remove("temp_chart.png")