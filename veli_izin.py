import streamlit as st
from fpdf import FPDF
import datetime
import os

# --- PDF OLUŞTURMA FONKSİYONLARI ---
def create_dual_pdf(school_name, class_name, student_no, student_name, teacher_name, destination, trip_date, transport, purpose):
    pdf = FPDF()
    
    # Font Kontrolü
    font_path = "tr_font.ttf"
    if os.path.exists(font_path):
        pdf.add_font('TrFont', '', font_path, uni=True)
        has_tr_font = True
    else:
        has_tr_font = False

    def txt_fix(text):
        if has_tr_font: return str(text)
        tr_map = {"ı": "i", "İ": "I", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ş": "s", "Ş": "S", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
        text = str(text)
        for tr, en in tr_map.items(): text = text.replace(tr, en)
        return text

    pdf.add_page()

    def draw_slip(start_y):
        pdf.set_xy(10, start_y + 5)
        
        # Başlıklar
        if has_tr_font: pdf.set_font('TrFont', '', 11)
        else: pdf.set_font("Arial", "B", 11)
            
        pdf.cell(0, 5, txt=txt_fix("T.C."), ln=True, align='C')
        pdf.cell(0, 5, txt=txt_fix(f"{school_name.upper()} MÜDÜRLÜĞÜ"), ln=True, align='C')
        pdf.cell(0, 5, txt=txt_fix("VELİ İZİN VE MUVAFAKAT BELGESİ"), ln=True, align='C')
        
        # Metin
        pdf.set_xy(10, start_y + 22)
        if has_tr_font: pdf.set_font('TrFont', '', 9)
        else: pdf.set_font("Arial", "", 9)
        
        c_name = txt_fix(class_name) if class_name else "..................."
        s_no = student_no if student_no else "..................."
        s_name = txt_fix(student_name) if student_name else "................................................................"
        t_name = txt_fix(teacher_name) if teacher_name else "..............................................."
        
        body_text = (
            f"Okulunuz {c_name} sınıfı, {s_no} numaralı öğrencisi, velisi bulunduğum "
            f"{s_name}'nın; okulunuz coğrafya dersi kapsamında, sorumlu öğretmen "
            f"{t_name} gözetiminde düzenlenecek olan saha çalışmasına katılmasına izin veriyorum."
        )
        pdf.multi_cell(0, 4, txt=body_text)
        
        # Tablo
        current_y = pdf.get_y() + 3
        pdf.set_xy(10, current_y)
        if has_tr_font: pdf.set_font('TrFont', '', 9) 
        else: pdf.set_font("Arial", "B", 9)  
        pdf.cell(0, 5, txt=txt_fix("SAHA ÇALIŞMASI BİLGİLERİ"), ln=True, border='B')
        
        if has_tr_font: pdf.set_font('TrFont', '', 8)
        else: pdf.set_font("Arial", "", 8)
            
        line_height = 4.5
        pdf.cell(40, line_height, txt=txt_fix("Gidilecek Yer"), border=0)
        pdf.cell(3, line_height, txt=":", border=0)
        pdf.cell(0, line_height, txt=txt_fix(destination), ln=True)
        
        pdf.cell(40, line_height, txt=txt_fix("Tarih"), border=0)
        pdf.cell(3, line_height, txt=":", border=0)
        pdf.cell(0, line_height, txt=txt_fix(trip_date.strftime("%d/%m/%Y")), ln=True)
        
        pdf.cell(40, line_height, txt=txt_fix("Ulaşım Aracı"), border=0)
        pdf.cell(3, line_height, txt=":", border=0)
        pdf.cell(0, line_height, txt=txt_fix(transport), ln=True)
        
        pdf.cell(40, line_height, txt=txt_fix("Etkinliğin Amacı"), border=0)
        pdf.cell(3, line_height, txt=":", border=0)
        pdf.multi_cell(0, line_height, txt=txt_fix(purpose))
        
        # Sağlık
        current_y = pdf.get_y() + 2
        pdf.set_xy(10, current_y)
        if has_tr_font: pdf.set_font('TrFont', '', 9)
        else: pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 5, txt=txt_fix("SAĞLIK VE İLETİŞİM BİLGİLERİ"), ln=True, border='B')
        
        if has_tr_font: pdf.set_font('TrFont', '', 7)
        else: pdf.set_font("Arial", "", 7)
        health_q = "Öğrencimin etkinliğe katılmasına engel kronik rahatsızlığı (fobi, kalp, astım vb.) var mı?"
        pdf.cell(0, 4, txt=txt_fix(health_q), ln=True)
        
        if has_tr_font: pdf.set_font('TrFont', '', 8)
        else: pdf.set_font("Arial", "", 8)
        pdf.cell(5, 4, txt="", border=1)
        pdf.cell(20, 4, txt=txt_fix(" Hayır"), ln=False)
        pdf.cell(5, 4, txt="", border=1)
        pdf.cell(20, 4, txt=txt_fix(" Evet"), ln=False)
        pdf.cell(0, 4, txt=txt_fix("(Açıklayınız: ..............................................................)"), ln=True)
        
        pdf.ln(2)
        pdf.cell(35, 4, txt=txt_fix("Veli Tel"), border=0)
        pdf.cell(0, 4, txt=": ...........................................................", ln=True)
        pdf.cell(35, 4, txt=txt_fix("Acil Durum 2. Kişi"), border=0)
        pdf.cell(0, 4, txt=": ........................................................... (Tel: .......................................)", ln=True)

        # İmza
        pdf.ln(3)
        if has_tr_font: pdf.set_font('TrFont', '', 7)
        else: pdf.set_font("Arial", "", 7)
        taahhut = "Yukarıdaki bilgilerin doğruluğunu beyan eder, öğrencimin sorumluluğunu kabul ederim."
        pdf.multi_cell(0, 3, txt=txt_fix(taahhut), align='C')
        
        pdf.ln(3)
        if has_tr_font: pdf.set_font('TrFont', '', 9)
        else: pdf.set_font("Arial", "", 9)
        pdf.cell(95, 5, txt=txt_fix(f"Tarih: ..../..../20...."), align='C')
        pdf.cell(95, 5, txt=txt_fix("Velinin Adı Soyadı - İmza"), align='C')

    # İki tane çiz
    draw_slip(0)
    
    # Kesme çizgisi
    pdf.set_line_width(0.5)
    pdf.set_draw_color(150, 150, 150)
    pdf.dashed_line(0, 148, 210, 148, dash_length=2, space_length=2)
    pdf.set_xy(100, 146)
    pdf.set_font("Arial", size=8)
    pdf.cell(10, 4, "- - - - Kesme Çizgisi - - - -", align='C')

    draw_slip(148)
    
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# --- ARAYÜZ BAŞLANGICI ---
st.set_page_config(page_title="Veli İzin Belgesi", page_icon="📝", layout="centered")

st.header("📝 Veli İzin Belgesi Oluşturucu")

# --- AÇIKLAMA KUTUSU ---
st.markdown("""
<div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 5px solid #1E88E5;'>
    <strong>UYGULAMANIN AMACI:</strong> Bu araç, 
    <em>Ortaöğretim Coğrafya Dersleri Öğretim Programı</em> kapsamında gerçekleştirilmesi planlanan 
    <strong>günübirlik saha/arazi çalışmaları</strong> için gerekli olan resmi veli izin ve muvafakat belgelerini 
    standartlara uygun, hızlı ve hatasız şekilde oluşturmak amacıyla <strong>Arş. Gör. Yusuf Mert Üstün</strong> tarafından 
    AI kullanılarak hazırlanmıştır.
</div>
""", unsafe_allow_html=True)
st.write("") 

# Font Uyarısı
if not os.path.exists("tr_font.ttf"):
    st.warning("⚠️ 'tr_font.ttf' dosyası bulunamadı! Türkçe karakterler (ğ, ş, İ) düzgün çıkmayabilir.")

# --- FORM GİRİŞLERİ (GÜNCELLENDİ) ---
st.markdown("### 🏫 Okul ve Saha Çalışması Bilgileri")

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        school_name = st.text_input("Okul Adı", "ATATÜRK ANADOLU LİSESİ")
        destination = st.text_input("Gidilecek Yer", "Belgrad Ormanı")
        transport = st.text_input("Ulaşım Aracı", "Özel Servis")
        
    with col2:
        teacher_name = st.text_input("Sorumlu Öğretmen", placeholder="Ad Soyad")
        # Format Gün/Ay/Yıl yapıldı
        trip_date = st.date_input("Saha Çalışması Tarihi", datetime.date.today() + datetime.timedelta(days=7), format="DD/MM/YYYY")
        purpose = st.text_area("Etkinlik Amacı", "Coğrafi gözlem ve inceleme gezisi.", height=105)

st.divider()

# --- ÇIKTI ALANI ---
st.markdown("### 🎓 Belge Oluşturma")

tab1, tab2 = st.tabs(["📄 Toplu Şablon (Boş)", "👤 Öğrenciye Özel"])

# TAB 1: BOŞ ŞABLON
with tab1:
    st.info("Bu seçenek ile isim kısımları boş bırakılır. Sınıfa dağıtmak için uygundur.")
    if st.button("Boş Şablonu Oluştur (2'li PDF)", type="primary"):
        pdf_data = create_dual_pdf(school_name, "", "", "", teacher_name, destination, trip_date, transport, purpose)
        st.success("Şablon oluşturuldu!")
        st.download_button("📥 Şablonu İndir (PDF)", pdf_data, "Veli_Izin_Sablon.pdf", "application/pdf")

# TAB 2: ÖZEL BELGE
with tab2:
    st.write("Tek bir öğrenci için dolu belge hazırlar.")
    c1, c2, c3 = st.columns(3)
    c_name = c1.text_input("Sınıf", "10-A")
    s_no = c2.text_input("Okul No", "123")
    s_name = c3.text_input("Öğrenci Adı Soyadı", "Ali Veli")
    
    if st.button("Öğrenci Belgesini Oluştur"):
        pdf_data = create_dual_pdf(school_name, c_name, s_no, s_name, teacher_name, destination, trip_date, transport, purpose)
        st.success(f"{s_name} için belge hazır!")
        st.download_button(f"📥 {s_name} İzin Belgesi İndir", pdf_data, f"Izin_{s_name}.pdf", "application/pdf")