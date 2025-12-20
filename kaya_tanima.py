import streamlit as st
import google.generativeai as genai
from PIL import Image
from fpdf import FPDF
import os
import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="AI Kayaç Analisti", page_icon="🪨", layout="centered")

# --- GİZLİ KASADAN ANAHTARI AL ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    st.error("HATA: API Anahtarı bulunamadı! Lütfen .streamlit/secrets.toml dosyasını kontrol edin.")
    st.stop()

# --- PDF OLUŞTURMA FONKSİYONU ---
def create_rock_pdf(rock_data, image_file):
    pdf = FPDF()
    
    font_path = "tr_font.ttf"
    if os.path.exists(font_path):
        pdf.add_font('TrFont', '', font_path, uni=True)
        font_name = 'TrFont'
    else:
        font_name = 'Arial'

    pdf.add_page()
    
    # Başlık
    pdf.set_font(font_name, '', 16)
    pdf.cell(0, 10, txt="ARAZI KAYAC GOZLEM FISI", ln=True, align='C')
    pdf.ln(5)
    
    # Tarih
    pdf.set_font(font_name, '', 10)
    bugun = datetime.date.today().strftime("%d/%m/%Y")
    pdf.cell(0, 10, txt=f"Tarih: {bugun} | Analiz: AI Destekli Cografya Asistani", ln=True, align='C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    # Analiz Metni
    pdf.set_font(font_name, '', 11)
    clean_text = rock_data.replace("**", "").replace("*", "-")
    
    if font_name == 'Arial':
        tr_map = {"ı": "i", "İ": "I", "ğ": "g", "Ğ": "G", "ü": "u", "Ü": "U", "ş": "s", "Ş": "S", "ö": "o", "Ö": "O", "ç": "c", "Ç": "C"}
        for tr, en in tr_map.items():
            clean_text = clean_text.replace(tr, en)

    pdf.multi_cell(0, 7, txt=clean_text)
    
    # Alt Bilgi
    pdf.set_y(-30)
    pdf.set_font(font_name, '', 8)
    
    footer_text = "Bu rapor Ars. Gor. Yusuf Mert Ustun projesi kapsaminda yapay zeka ile uretilmistir."
    if font_name == 'Arial': 
         footer_text = footer_text.replace("ş", "s").replace("Ü", "U").replace("ü", "u")

    pdf.cell(0, 10, txt=footer_text, align='C')
    
    try:
        return pdf.output(dest='S').encode('latin-1', 'ignore') 
    except UnicodeEncodeError:
        return pdf.output(dest='S').encode('latin-1', 'replace')

# --- YAPAY ZEKA ANALİZ FONKSİYONU ---
def analyze_image(image, key):
    genai.configure(api_key=key)
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = """
    Sen uzman bir Jeolog ve Akademik Coğrafyacısın. Bu kayaç/mineral fotoğrafını analiz et.
    Cevabı şu başlıklarla, Türkçe ve akademik bir dille ver:
    
    1. **Kayaç/Mineral Adı:** (En olası tahmin)
    2. **Jeolojik Grubu:** (Magmatik / Tortul / Başkalaşım ve alt grubu)
    3. **Görsel Kanıtlar:** (Rengi, dokusu, kristal yapısı vb.)
    4. **Oluşum Süreci:** (Kısaca ve bilimsel açıklama)
    5. **Tahmini Sertlik (Mohs):** 6. **Türkiye'de Yayılışı:** (DİKKAT: Asla "Bölge" ismi kullanma. Bunun yerine "Kuzey Anadolu Dağları, Toros Kuşağı, Menderes Masifi, Karadeniz kıyı şeridi" gibi jeomorfolojik birim veya havza isimleri kullan.)
    7. **Öğretim İpuçları:** (Öğrenciler bunu neyle karıştırabilir? Ayırt edici ipucu nedir?)
    
    Eğer bu bir taş değilse, bilimsel bir dille görselin analiz edilemediğini belirt.
    """
    with st.spinner('💎 Numune inceleniyor... Kristal yapı taranıyor...'):
        try:
            response = model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            return f"Hata oluştu: {e}"

# --- ARAYÜZ TASARIMI ---
st.image("https://img.icons8.com/fluency/96/rock.png", width=80)
st.title("🪨 Akademik Kayaç Analisti")

# --- AÇIKLAMA METNİ (DÜZELTİLMİŞ HALİ) ---
st.markdown("""
<div style='background-color: #f8f9fa; color: #333333; padding: 15px; border-radius: 5px; border-left: 5px solid #1E88E5; font-size: 14px;'>
    <strong>UYGULAMANIN AMACI:</strong><br>
    Bu yapay zekâ tabanlı araç, <em>Kayaç Sergisi ve Saha Çalışmaları</em> kapsamında incelenen kayaç ve minerallerin 
    görsel veriler üzerinden ön tanımlamasının yapılması, jeolojik kökenlerinin yorumlanması ve eğitsel nitelikte raporlanması amacıyla geliştirilmiştir.<br><br>
    Uygulama; kayaç/mineral adı, jeolojik grup, oluşum süreci, dokusal ve yapısal özellikler (tabakalanma, tanelilik, renk, ayrışma direnci vb.), 
    tahmini Mohs sertliği, Türkiye’deki olası yayılım alanları ve öğretim amaçlı ayırt edici ipuçları gibi başlıklarda kullanıcıya 
    rehberlik edici analizler sunmayı hedeflemektedir.<br><br>
    Bu araç, özellikle öğrencilerin saha ve sergi ortamlarında gözlemsel becerilerini geliştirmelerine yardımcı olmak üzere tasarlanmıştır.<br><br><strong>⚠️ Kesin tanı için laboratuvar testlerinin gerekli olduğunu unutmayınız.</strong><br>
    Sunulan çıktılar, <strong>kesin tanı yerine ön değerlendirme ve eğitim amaçlı yorumlar</strong> niteliğindedir.<br><br>
    <em>Bu çalışma henüz geliştirilme aşamasında olup, bir pilot uygulama niteliği taşımaktadır. Geliştirilme sürecinde Google Gemini yaygın bir şekilde kullanılmıştır. Görüş ve önerileriniz için: 
    <strong>Arş. Gör. Yusuf Mert Üstün, yusuf.ustun@marmara.edu.tr</strong></em>
</div>
""", unsafe_allow_html=True)
st.write("")

# --- FOTOĞRAF YÜKLEME ---
st.warning("⚠️ **Yasal Uyarı (KVKK):** Lütfen sisteme yüklediğiniz fotoğraflarda kişisel veri (insan yüzü, kimlik, plaka vb.) bulunmadığından emin olunuz. Sadece kayaç/mineral odaklı görseller yükleyiniz.")

uploaded_file = st.file_uploader("📸 Fotoğraf Seç / Yükle (Sadece Kayaç)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='İncelenecek Numune', width=300)
    
    if st.button("🔍 DETAYLI ANALİZ BAŞLAT", type="primary"):
        result_text = analyze_image(image, api_key)
        
        st.markdown("### 📝 Jeolojik Analiz Raporu")
        st.markdown(f"""
        <div style='background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e0e0e0; color: #333333;'>
            {result_text}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.success("✅ Rapor oluşturuldu. Çıktı alabilirsiniz.")
        
        pdf_bytes = create_rock_pdf(result_text, image)
        st.download_button(
            label="📄 PDF Gözlem Fişini İndir",
            data=pdf_bytes,
            file_name="Kayac_Gozlem_Fisi.pdf",
            mime="application/pdf"
        )