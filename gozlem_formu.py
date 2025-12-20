import streamlit as st
from fpdf import FPDF
import os
import google.generativeai as genai

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="AI Saha Gözlem Formu", page_icon="📋", layout="wide")

# --- API ANAHTARI KONTROLÜ ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    has_api = True
except:
    has_api = False

# --- VARSAYILAN VERİLER ---
DEFAULT_KAZANIM = "COĞ.12.5.3. Turizm faaliyetlerinin dünya ve Türkiye’deki sosyal, kültürel, ekonomik, politik ve çevresel etkilerini sorgulayabilme"

DEFAULT_MADDELER = """Farklı ülkelerden gelen turistler
Fotoğraf çeken / videoya kaydeden turistler
Sokaklarda taşıma kapasitesi üzerinde kalabalık
Çok sayıda çöp ve atık
Turist gruplarından kaynaklı yüksek sesli konuşmalar
Tarihi yapılarda turizm kaynaklı zararlar
Turizmin yerel ekonomi üzerinde etkisi
Turizm kaynaklı ekonomik canlılık
Yabancı dil konuşan esnaf sayısında yükseklik
Yabancı dilde tabelaların varlığı
Turizm kaynaklı, piyasa üzerinde yüksek fiyatlar
Gözlemlenen turistik dükkân sayısı
Gözlemlenen tur otobüsü sayısı
Gözlemlenen yabancı tabela sayısı"""

DEFAULT_SORULAR = """Gözlem Notları (Dikkatinizi çeken tüm unsurlar):
Turizmin inceleme sahanızda insan sayısına etkisini nasıl gözlemlediniz?
Turizmin inceleme sahanızdaki ekonomik etkileri nelerdir?
Turizmin yerel kültür ile olan etkilerini hangi örneklerle gözlemlediniz?
Turizmin inceleme sahanızdaki çevresel etkileri nelerdir?"""

# --- AI FONKSİYONU ---
def get_ai_suggestions(topic, form_type):
    model = genai.GenerativeModel('gemini-flash-latest')
    
    if form_type == "unstructured":
        prompt = f"""
        Sen uzman bir Coğrafya öğretmenisin. Aşağıdaki kazanım/konu için lise öğrencilerine yönelik 
        saha çalışmasında kullanılacak **Açık Uçlu Gözlem Soruları** hazırla.
        Konu: {topic}
        Kurallar: Türkçe olsun, madde işareti koyma, eleştirel düşünme gerektirsin.
        """
    else:
        prompt = f"""
        Sen uzman bir Coğrafya öğretmenisin. Aşağıdaki kazanım/konu için lise öğrencilerine yönelik 
        saha çalışmasında kullanılacak **Gözlem Formu Maddeleri (Checklist)** hazırla.
        Konu: {topic}
        Kurallar: Türkçe olsun, madde işareti koyma, somut gözlemler olsun (10-12 adet).
        """
        
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Hata: AI servisine ulaşılamadı. ({e})"

# --- GÜVENLİ METİN FONKSİYONU ---
def safe_text(text):
    if text is None: return ""
    text = str(text)
    replacements = {"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", "…": "..."}
    for old, new in replacements.items():
        text = text.replace(old, new)

    if not os.path.exists("tr_font.ttf"):
        tr_map = {"ı": "i", "İ": "I", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ş": "s", "Ş": "S", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
        for tr, en in tr_map.items():
            text = text.replace(tr, en)
    return text

# --- PDF MOTORU ---
class PDF(FPDF):
    def header(self): pass 
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Sayfa {self.page_no()}', 0, 0, 'C')

def create_observation_pdf(form_type, school_name, teacher_name, kazanim, items):
    pdf = PDF()
    font_path = "tr_font.ttf"
    has_font = os.path.exists(font_path)
    
    pdf.add_page()

    if has_font:
        try:
            pdf.add_font('TrFont', '', font_path, uni=True)
            main_font = 'TrFont'
        except:
            main_font = 'Arial'; has_font = False
    else:
        main_font = 'Arial'

    school_name = safe_text(school_name)
    teacher_name = safe_text(teacher_name)
    kazanim = safe_text(kazanim)
    items = [safe_text(i) for i in items]

    # Başlıklar
    pdf.set_font(main_font, '', 14)
    pdf.cell(0, 10, txt=school_name.upper(), ln=True, align='C')
    pdf.set_font(main_font, '', 11) # Başlık fontu biraz küçüldü
    
    title_map = {
        "structured": "YAPILANDIRILMIS GOZLEM FORMU",
        "semi": "YARI-YAPILANDIRILMIS GOZLEM FORMU",
        "unstructured": "YAPILANDIRILMAMIS (ACIK UCLU) GOZLEM FORMU"
    }
    title_text = safe_text(title_map[form_type])
    pdf.cell(0, 8, txt=title_text, ln=True, align='C')
    pdf.ln(3)
    
    # Kazanım Kutusu
    pdf.set_font(main_font, '', 9) # Kompakt
    lbl_kazanim = safe_text("Kazanım/Konu")
    pdf.multi_cell(0, 5, txt=f"{lbl_kazanim}: {kazanim}", border=1, align='L')
    pdf.ln(4)
    
    # Bilgiler
    l_yer, l_tar, l_ogr, l_sur, l_tea = map(safe_text, ["Gözlem Yeri", "Tarih", "Öğrenci Adı Soyadı", "Gözlem Süresi", "Öğretmen"])
    
    pdf.cell(95, 6, txt=f"{l_yer}: ...........................................", ln=0)
    pdf.cell(95, 6, txt=f"{l_tar}: ..../..../20....", ln=1)
    pdf.cell(95, 6, txt=f"{l_ogr}: ................................", ln=0)
    pdf.cell(95, 6, txt=f"{l_sur}: .....................................", ln=1)
    pdf.cell(95, 6, txt=f"{l_tea}: {teacher_name}", ln=1)
    pdf.ln(4)
    
    # --- DİNAMİK TABLOLAR (TAŞMAYI ÖNLEYEN SİSTEM) ---
    
    if form_type == "structured":
        pdf.set_fill_color(240, 240, 240)
        h = [safe_text(x) for x in ["Ölçütler / Gözlem Maddeleri", "Var", "Kısmen", "Yok"]]
        
        # Sütun Genişlikleri
        w_text = 130
        w_box = 20
        
        pdf.cell(w_text, 8, h[0], 1, 0, 'C', 1)
        pdf.cell(w_box, 8, h[1], 1, 0, 'C', 1)
        pdf.cell(w_box, 8, h[2], 1, 0, 'C', 1)
        pdf.cell(w_box, 8, h[3], 1, 1, 'C', 1)
        
        pdf.set_font(main_font, '', 8) # Font küçüldü (Kompakt)
        
        for item in items:
            # 1. Mevcut konumu kaydet
            x_start = pdf.get_x()
            y_start = pdf.get_y()
            
            # 2. Metni yaz (MultiCell) ve yeni Y konumunu al
            # Border=1 veriyoruz ki kutu çizsin
            pdf.multi_cell(w_text, 5, txt=f" {item}", border=1, align='L')
            y_end = pdf.get_y()
            
            # 3. Satır yüksekliğini hesapla
            row_height = y_end - y_start
            
            # 4. İmleci eski yerine (metnin sağına) taşı
            pdf.set_xy(x_start + w_text, y_start)
            
            # 5. Kutucukları bu yüksekliğe göre çiz
            pdf.cell(w_box, row_height, "", 1)
            pdf.cell(w_box, row_height, "", 1)
            pdf.cell(w_box, row_height, "", 1, 1) # Sonuncusu alt satıra atar

    elif form_type == "semi":
        pdf.set_fill_color(240, 240, 240)
        h = [safe_text(x) for x in ["Ölçütler", "Var", "Yok", "Açıklama (Nasıl Bir Etkisi Var?)"]]
        
        w_item, w_chk, w_exp = 65, 12, 100 # Genişlikler ayarlandı
        
        pdf.cell(w_item, 8, h[0], 1, 0, 'C', 1)
        pdf.cell(w_chk, 8, h[1], 1, 0, 'C', 1)
        pdf.cell(w_chk, 8, h[2], 1, 0, 'C', 1)
        pdf.cell(w_exp, 8, h[3], 1, 1, 'C', 1)
        
        pdf.set_font(main_font, '', 8)
        
        for item in items:
            x_start = pdf.get_x()
            y_start = pdf.get_y()
            
            # Metin hücresi (Otomatik kaydırmalı)
            pdf.multi_cell(w_item, 5, txt=f" {item}", border=1, align='L')
            
            # Eğer açıklama kısmı için ekstra yükseklik gerekiyorsa en az 10mm olsun
            y_end = pdf.get_y()
            row_height = max(y_end - y_start, 10) 
            
            # Eğer metin kısa kaldıysa, kutuyu tamamlamak için boşluğu doldur
            if (y_end - y_start) < row_height:
                pdf.set_xy(x_start, y_start)
                pdf.cell(w_item, row_height, "", 1) # Sadece çerçeve çiz
                # Metni tekrar yazmaya gerek yok, üstüne çizdik
            
            # İmleci sağa taşı
            pdf.set_xy(x_start + w_item, y_start)
            
            pdf.cell(w_chk, row_height, "", 1)
            pdf.cell(w_chk, row_height, "", 1)
            pdf.cell(w_exp, row_height, "", 1, 1)

    elif form_type == "unstructured":
        pdf.set_font(main_font, '', 10)
        for i, soru in enumerate(items, 1):
            pdf.multi_cell(0, 5, txt=f"{i}. {soru}")
            # Noktalı alan (Kompakt: 3 satır yeterli)
            for _ in range(3): 
                pdf.cell(0, 7, txt="."*145, ln=1)
            pdf.ln(2)

    try: return pdf.output(dest='S').encode('latin-1')
    except: return pdf.output(dest='S').encode('latin-1', 'replace')

# --- ARAYÜZ BAŞLANGICI ---
st.title("📋 AI Destekli Gözlem Formu Oluşturucu")

# --- AÇIKLAMA METNİ (YENİ EKLENEN KISIM) ---
st.markdown("""
<div style='background-color: #f8f9fa; color: #333333; padding: 15px; border-radius: 5px; border-left: 5px solid #2E7D32; font-size: 14px;'>
    <strong>UYGULAMANIN AMACI:</strong><br>
    Saha çalışmaları, coğrafya eğitiminin en temel yapıtaşlarından biridir. Öğrencilerin sahada sadece "bakmak" yerine, 
    bilinçli bir şekilde "görmelerini" sağlamak için sistemli gözlem araçlarına ihtiyaç vardır.<br><br>
    Bu yapay zeka destekli araç, öğretmenlerin ders kazanımlarına ve saha hedeflerine uygun;
    <ul>
        <li><strong>Yapılandırılmış:</strong> Kontrol listesi temelli (Var/Yok),</li>
        <li><strong>Yarı-Yapılandırılmış:</strong> Esnek ve açıklamalı,</li>
        <li><strong>Yapılandırılmamış:</strong> Açık uçlu ve derinlemesine gözlem</li>
    </ul>
    formlarını saniyeler içinde oluşturmasını sağlar. <strong>Google Gemini AI</strong> teknolojisi, girilen kazanıma uygun 
    akademik gözlem maddeleri önererek materyal hazırlama sürecini profesyonelleştirir.<br><br>
    <em>Bu çalışma, coğrafya eğitiminde dijital materyal geliştirme kapsamında <strong>Arş. Gör. Yusuf Mert Üstün</strong> tarafından hazırlanmıştır.
    (İletişim: yusuf.ustun@marmara.edu.tr)</em>
</div>
""", unsafe_allow_html=True)
st.write("")

# --- STATE YÖNETİMİ ---
if "form_content" not in st.session_state:
    st.session_state.form_content = DEFAULT_MADDELER
if "last_type" not in st.session_state:
    st.session_state.last_type = "structured"

# --- KENAR ÇUBUĞU ---
with st.sidebar:
    st.header("⚙️ Ayarlar")
    # GÜNCELLEME: Varsayılan Okul Adı Değişti
    school_name = st.text_input("Okul Adı", "ATAŞEHİR ANADOLU LİSESİ")
    teacher_name = st.text_input("Öğretmen", "")
    st.divider()
    
    form_type_display = st.selectbox("Form Türü", 
        ("Yapılandırılmış (Var/Kısmen/Yok)", "Yarı-Yapılandırılmış (Açıklamalı)", "Yapılandırılmamış (Açık Uçlu)"))
    
    if "Yarı" in form_type_display: selected_type = "semi"
    elif "Yapılandırılmış (" in form_type_display: selected_type = "structured"
    else: selected_type = "unstructured"

    if selected_type != st.session_state.last_type:
        st.session_state.last_type = selected_type
        if selected_type == "unstructured":
            st.session_state.form_content = DEFAULT_SORULAR
        else:
            st.session_state.form_content = DEFAULT_MADDELER
        st.rerun()

# --- ANA EKRAN ---
st.subheader("1. Konu ve Kazanım")
kazanim_text = st.text_area("Gözlem Konusu / Kazanımı", DEFAULT_KAZANIM, height=60)

if has_api:
    if st.button("✨ Yapay Zeka ile Madde Öner", type="secondary"):
        with st.spinner("Yapay zeka analiz ediyor..."):
            ai_result = get_ai_suggestions(kazanim_text, selected_type)
            if "Hata:" in ai_result: st.error(ai_result)
            else:
                st.session_state.form_content = ai_result
                st.rerun()

st.subheader("2. İçerik Düzenleme")
st.info(f"Mod: **{form_type_display}**")

user_text = st.text_area("Maddeler / Sorular", value=st.session_state.form_content, height=300)
if user_text != st.session_state.form_content:
    st.session_state.form_content = user_text

final_items = user_text.split("\n")
clean_items = [x for x in final_items if x.strip()]

st.divider()
col1, col2 = st.columns([2, 1])
with col1:
    st.write(f"**Toplam Madde:** {len(clean_items)}")

with col2:
    if st.button("📄 PDF Formu Oluştur", type="primary"):
        pdf_bytes = create_observation_pdf(selected_type, school_name, teacher_name, kazanim_text, clean_items)
        st.success("Form Hazır!")
        st.download_button("📥 İndir (PDF)", pdf_bytes, f"Gozlem_Formu.pdf", "application/pdf")