"""
cat_breed_info.py

59 kedi ırkı için detaylı bilgi veritabanı
Bakım, sağlık, beslenme, yaşam süresi ve davranış özellikleri
"""

CAT_BREED_INFO = {
    "Abyssinian": {
        "bakım": {
            "tüy_bakımı": "Haftalık fırçalama yeterli. Kısa tüylü olduğu için minimum bakım gerektirir.",
            "sosyalleşme": "Çok sosyal ve aktif. Günlük oyun ve etkileşim şart. Yalnız kalmayı sevmez.",
            "tırnak_bakımı": "2 haftada bir tırnak kesimi önerilir.",
        },
        "sağlık_riskleri": [
            "Progressive Retinal Atrophy (PRA) - Göz hastalığı",
            "Renal Amyloidosis - Böbrek hastalığı",
            "Pyruvate Kinase Deficiency - Kalıtsal anemi",
            "Diş eti hastalıkları",
        ],
        "beslenme": {
            "günlük_kalori": "250-300 kalori (3-5 kg için)",
            "protein": "En az %30-35 hayvansal protein",
            "özel_ihtiyaçlar": "Aktif olduğu için yüksek protein gereksinimi. Tahılsız mama tercih edilir.",
        },
        "yaşam_süresi": "12-15 yıl",
        "davranış": {
            "enerji": "Çok yüksek - sürekli hareket eder",
            "zeka": "Çok zeki - oyuncak ve puzzle severler",
            "ses": "Orta - düzenli miyavlama",
            "çocuk_uyumu": "Mükemmel - aktif çocuklarla iyi geçinir",
            "diğer_hayvanlar": "İyi - özellikle köpeklerle uyumlu",
        },
    },
    
    "American Bobtail": {
        "bakım": {
            "tüy_bakımı": "Haftada 2-3 kez fırçalama. Orta/uzun tüylü varyasyonlar daha fazla bakım gerektirir.",
            "sosyalleşme": "Sosyal ve oyuncu. Aile ortamında mutlu olur.",
            "tırnak_bakımı": "Düzenli tırnak kesimi gereklidir.",
        },
        "sağlık_riskleri": [
            "Kalça displazisi",
            "Omurga problemleri (kısa kuyruk nedeniyle)",
            "Genetik çeşitlilik sayesinde genel olarak sağlıklı",
        ],
        "beslenme": {
            "günlük_kalori": "280-320 kalori (4-6 kg için)",
            "protein": "En az %32 hayvansal protein",
            "özel_ihtiyaçlar": "Orta-yüksek aktivite için dengeli beslenme",
        },
        "yaşam_süresi": "13-15 yıl",
        "davranış": {
            "enerji": "Yüksek - oyun sever",
            "zeka": "Çok zeki - talim öğrenebilir",
            "ses": "Düşük - sessiz ırk",
            "çocuk_uyumu": "Mükemmel",
            "diğer_hayvanlar": "Çok iyi - köpek benzeri",
        },
    },
    
    "American Curl": {
        "bakım": {
            "tüy_bakımı": "Haftada 2 kez fırçalama yeterli.",
            "sosyalleşme": "Çok sevecen ve insanlara bağlı. Sürekli ilgi ister.",
            "kulak_bakımı": "⚠️ ÖNEMLİ: Kıvrık kulaklar hassastır. Hafifçe temizlenmeli, bükülemez!",
        },
        "sağlık_riskleri": [
            "Kulak enfeksiyonları (kıvrık yapı nedeniyle)",
            "Kıkırdak problemleri",
            "Genel olarak sağlıklı ırk",
        ],
        "beslenme": {
            "günlük_kalori": "240-280 kalori (3-5 kg için)",
            "protein": "En az %30 protein",
            "özel_ihtiyaçlar": "Standart yetişkin kedi maması uygun",
        },
        "yaşam_süresi": "12-16 yıl",
        "davranış": {
            "enerji": "Orta-yüksek",
            "zeka": "Zeki ve meraklı",
            "ses": "Orta - konuşkan",
            "çocuk_uyumu": "Mükemmel - çok sabırlı",
            "diğer_hayvanlar": "İyi",
        },
    },
    
    "American Shorthair": {
        "bakım": {
            "tüy_bakımı": "Haftada 1 kez fırçalama yeterli.",
            "sosyalleşme": "Bağımsız ama sevecen. Aşırı ilgi istemez.",
            "tırnak_bakımı": "Düzenli tırnak kesimi",
        },
        "sağlık_riskleri": [
            "Hipertrofik kardiyomiyopati (kalp hastalığı)",
            "Obezite - kilo kontrolü önemli",
            "Polikistik böbrek hastalığı",
        ],
        "beslenme": {
            "günlük_kalori": "260-300 kalori (4-6 kg için)",
            "protein": "En az %28-30 protein",
            "özel_ihtiyaçlar": "Kilolu olmaya eğilimli - porsiyon kontrolü şart",
        },
        "yaşam_süresi": "15-20 yıl",
        "davranış": {
            "enerji": "Orta",
            "zeka": "Zeki - avcılık içgüdüsü güçlü",
            "ses": "Düşük - sessiz",
            "çocuk_uyumu": "Çok iyi",
            "diğer_hayvanlar": "İyi - uyumlu",
        },
    },
    
    "Bengal": {
        "bakım": {
            "tüy_bakımı": "Minimal bakım - haftada 1 kez fırçalama.",
            "sosyalleşme": "ÇOK AKTİF! Günde en az 2 saat oyun şart. Tırmanma kuleleri gerekli.",
            "su": "Suyu sever - su havuzları/çeşmeleri tercih eder.",
        },
        "sağlık_riskleri": [
            "Progressive Retinal Atrophy (PRA)",
            "Hipertrofik kardiyomiyopati",
            "Piruvat kinaz eksikliği",
            "Hassas mide - ishal eğilimi",
        ],
        "beslenme": {
            "günlük_kalori": "300-350 kalori (5-7 kg için)",
            "protein": "En az %35-40 protein (vahşi atalarından gelen ihtiyaç)",
            "özel_ihtiyaçlar": "Tahılsız, yüksek proteinli mama. Probiyotik takviyesi önerilir.",
        },
        "yaşam_süresi": "12-16 yıl",
        "davranış": {
            "enerji": "ÇOK YÜKSEK - en aktif ırklardan",
            "zeka": "Son derece zeki - kapı açabilir, oyun öğrenir",
            "ses": "Yüksek - çok konuşkan",
            "çocuk_uyumu": "İyi - ama çok enerjik olabilir",
            "diğer_hayvanlar": "Dikkatli - dominant olabilir",
        },
    },
    
    "British Shorthair": {
        "bakım": {
            "tüy_bakımı": "Haftada 2 kez fırçalama. Yoğun tüyü var.",
            "sosyalleşme": "Sakin ve bağımsız. Aşırı kucaklanmayı sevmez ama yakında olmayı sever.",
            "göz_bakımı": "Yassı yüz - göz akıntısı temizlenmeli.",
        },
        "sağlık_riskleri": [
            "Hipertrofik kardiyomiyopati (HCM) - yaygın",
            "Polikistik böbrek hastalığı (PKD)",
            "Obezite - kilo kontrolü kritik",
            "A ve B kan grubu uyuşmazlığı (üreme için önemli)",
        ],
        "beslenme": {
            "günlük_kalori": "280-320 kalori (4-7 kg için)",
            "protein": "En az %30 protein",
            "özel_ihtiyaçlar": "Obeziteye eğilimli - porsiyon kontrolü ve düşük kalorili mama",
        },
        "yaşam_süresi": "12-17 yıl",
        "davranış": {
            "enerji": "Düşük - sakin ve uysal",
            "zeka": "Zeki ama tembel",
            "ses": "Çok düşük - sessiz",
            "çocuk_uyumu": "İyi - sabırlı",
            "diğer_hayvanlar": "Çok iyi",
        },
    },
    
    "Persian": {
        "bakım": {
            "tüy_bakımı": "GÜNLÜK fırçalama ŞART! Düğüm yapmaya çok eğilimli. Profesyonel tıraş gerekebilir.",
            "yüz_bakımı": "GÜNLÜK göz temizliği - gözyaşı lekeleri",
            "sosyalleşme": "Sakin, uysal. Sessiz ortam sever.",
        },
        "sağlık_riskleri": [
            "Polikistik böbrek hastalığı (PKD) - çok yaygın",
            "Hipertrofik kardiyomiyopati",
            "Solunum problemleri (yassı yüz)",
            "Diş problemleri (yanlış kapanış)",
            "Göz hastalıkları (PRA, cherry eye)",
        ],
        "beslenme": {
            "günlük_kalori": "250-300 kalori (3-5 kg için)",
            "protein": "En az %28 protein",
            "özel_ihtiyaçlar": "Hairball önleyici mama, yassı yüz için özel mama şekli",
        },
        "yaşam_süresi": "12-17 yıl",
        "davranış": {
            "enerji": "Çok düşük - çok sakin",
            "zeka": "Orta",
            "ses": "Çok düşük - neredeyse hiç ses çıkarmaz",
            "çocuk_uyumu": "İyi - sakin çocuklar için",
            "diğer_hayvanlar": "İyi",
        },
    },
    
    "Siamese": {
        "bakım": {
            "tüy_bakımı": "Minimal - haftada 1 kez fırçalama yeterli.",
            "sosyalleşme": "Son derece sosyal ve bağımlı. Yalnız kalamaz - ikinci kedi önerilir.",
            "diş_bakımı": "Diş fırçalama önerilir - diş eti hastalıklarına eğilimli.",
        },
        "sağlık_riskleri": [
            "Progressive Retinal Atrophy (PRA)",
            "Amyloidosis (böbrek ve karaciğer)",
            "Astım ve solunum problemleri",
            "Diş eti hastalıkları",
            "Şaşılık (kozmetik, sağlık sorunu değil)",
        ],
        "beslenme": {
            "günlük_kalori": "260-300 kalori (3-5 kg için)",
            "protein": "En az %32 protein",
            "özel_ihtiyaçlar": "Aktif olduğu için yüksek protein. İnce yapılı - düzenli beslenme",
        },
        "yaşam_süresi": "12-20 yıl (uzun ömürlü)",
        "davranış": {
            "enerji": "Çok yüksek",
            "zeka": "Son derece zeki - eğitilebilir",
            "ses": "ÇOK YÜKSEK - en konuşkan ırk, sürekli 'konuşur'",
            "çocuk_uyumu": "Mükemmel",
            "diğer_hayvanlar": "Mükemmel - arkadaşlık gereksinimi var",
        },
    },
    
    "Maine Coon": {
        "bakım": {
            "tüy_bakımı": "Haftada 3-4 kez fırçalama. Uzun tüy ama düğüm yapmaya az eğilimli.",
            "sosyalleşme": "Sosyal ve nazik. 'Köpek-kedi' olarak bilinir.",
            "su": "Suyu sever - su oyunları yapabilir.",
        },
        "sağlık_riskleri": [
            "Hipertrofik kardiyomiyopati (HCM) - yaygın",
            "Spinal Muscular Atrophy (SMA)",
            "Kalça displazisi",
            "Polikistik böbrek hastalığı",
        ],
        "beslenme": {
            "günlük_kalori": "350-450 kalori (6-10 kg için)",
            "protein": "En az %35 protein (büyük ırk)",
            "özel_ihtiyaçlar": "Yavaş büyür (4 yaşına kadar) - yüksek kalorili yavru maması uzun süre",
        },
        "yaşam_süresi": "12-15 yıl",
        "davranış": {
            "enerji": "Orta-yüksek",
            "zeka": "Çok zeki - talim öğrenir",
            "ses": "Orta - tatlı miyav (çipçip sesi)",
            "çocuk_uyumu": "Mükemmel - çok sabırlı",
            "diğer_hayvanlar": "Mükemmel",
        },
    },
    
    "Ragdoll": {
        "bakım": {
            "tüy_bakımı": "Haftada 2-3 kez fırçalama. İpeksi tüy, az düğüm yapar.",
            "sosyalleşme": "Çok bağımlı ve sevecen. 'Bez bebek' - kucağa alınınca gevşer.",
            "tırnak_bakımı": "Düzenli kesim - çok büyüyebilir.",
        },
        "sağlık_riskleri": [
            "Hipertrofik kardiyomiyopati (HCM)",
            "Polikistik böbrek hastalığı",
            "Mesane taşları",
            "Obezite - düşük aktivite nedeniyle",
        ],
        "beslenme": {
            "günlük_kalori": "300-350 kalori (5-8 kg için)",
            "protein": "En az %30 protein",
            "özel_ihtiyaçlar": "Tembelce eğilimli - kilo kontrolü önemli",
        },
        "yaşam_süresi": "12-17 yıl",
        "davranış": {
            "enerji": "Düşük - sakin ve rahat",
            "zeka": "Zeki ama sakin",
            "ses": "Düşük - yumuşak ses",
            "çocuk_uyumu": "Mükemmel - çok sabırlı",
            "diğer_hayvanlar": "Mükemmel",
        },
    },
    
    "Scottish Fold": {
        "bakım": {
            "tüy_bakımı": "Haftada 1-2 kez fırçalama.",
            "sosyalleşme": "Sevecen ve uyumlu. İlgi sever.",
            "kulak_bakımı": "⚠️ Katlı kulaklar düzenli kontrol edilmeli.",
        },
        "sağlık_riskleri": [
            "⚠️ Osteochondrodysplasia - eklem ve kemik hastalığı (GENETİK)",
            "Artrit - ağrılı eklemler",
            "Kalp hastalıkları",
            "⚠️ ETİK UYARI: Genetik hastalık nedeniyle üretimi bazı ülkelerde yasaklı",
        ],
        "beslenme": {
            "günlük_kalori": "250-300 kalori (4-6 kg için)",
            "protein": "En az %30 protein",
            "özel_ihtiyaçlar": "Eklem sağlığı için omega-3, glukozamin takviyesi",
        },
        "yaşam_süresi": "11-15 yıl",
        "davranış": {
            "enerji": "Orta - eklem ağrısı nedeniyle düşük olabilir",
            "zeka": "Zeki",
            "ses": "Düşük",
            "çocuk_uyumu": "İyi - nazik",
            "diğer_hayvanlar": "İyi",
        },
    },
    
    "Sphynx - Hairless Cat": {
        "bakım": {
            "tüy_bakımı": "TÜY YOK! HAFTALIK BANYO ŞART - yağ birikir.",
            "cilt_bakımı": "Güneşten koruma, nemlendirici gerekebilir.",
            "sosyalleşme": "Çok sosyal ve sıcaklık arar. Üşür - battaniye/kıyafet gerekir.",
        },
        "sağlık_riskleri": [
            "Hipertrofik kardiyomiyopati (HCM)",
            "Cilt enfeksiyonları - düzenli temizlik şart",
            "Üst solunum yolu enfeksiyonları",
            "Güneş yanığı",
        ],
        "beslenme": {
            "günlük_kalori": "350-400 kalori (3-5 kg için) - yüksek metabolizma",
            "protein": "En az %35 protein",
            "özel_ihtiyaçlar": "Vücut ısısını korumak için çok kalori harcar - sık beslenme",
        },
        "yaşam_süresi": "12-15 yıl",
        "davranış": {
            "enerji": "Yüksek",
            "zeka": "Çok zeki",
            "ses": "Yüksek - konuşkan",
            "çocuk_uyumu": "Mükemmel",
            "diğer_hayvanlar": "Mükemmel - sıcaklık için",
        },
    },
    
    "Russian Blue": {
        "bakım": {
            "tüy_bakımı": "Haftada 1-2 kez fırçalama. Çift katmanlı tüy.",
            "sosyalleşme": "Utangaç ama bağlı. Yabancılara mesafeli, ailesine sadık.",
            "rutin": "Rutine bağlı - değişikliklerden hoşlanmaz.",
        },
        "sağlık_riskleri": [
            "Mesane taşları",
            "Obezite eğilimi",
            "Genel olarak sağlıklı ve uzun ömürlü",
        ],
        "beslenme": {
            "günlük_kalori": "250-300 kalori (3-5 kg için)",
            "protein": "En az %30 protein",
            "özel_ihtiyaçlar": "Hassas mide olabilir - kaliteli mama tercih edilir",
        },
        "yaşam_süresi": "15-20 yıl",
        "davranış": {
            "enerji": "Orta",
            "zeka": "Çok zeki - gözlemci",
            "ses": "Düşük - sessiz",
            "çocuk_uyumu": "İyi - ama sakin çocuklarla",
            "diğer_hayvanlar": "İyi - yavaş tanıştırma gerekir",
        },
    },
    
    "American Wirehair": {
        "bakım": {"tüy_bakımı": "Minimal - haftada 1 kez fırçalama", "sosyalleşme": "Uyumlu ve sevecen", "tırnak_bakımı": "Düzenli kesim"},
        "sağlık_riskleri": ["Genel olarak sağlıklı", "Cilt hassasiyeti (tel tüy)", "Hipertrofik kardiyomiyopati"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Standart yetişkin kedi maması"},
        "yaşam_süresi": "14-18 yıl",
        "davranış": {"enerji": "Orta", "zeka": "Zeki", "ses": "Orta", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "İyi"},
    },
    
    "Applehead Siamese": {
        "bakım": {"tüy_bakımı": "Minimal - haftalık fırçalama", "sosyalleşme": "Çok sosyal ve bağımlı", "diş_bakımı": "Düzenli diş fırçalama önerilir"},
        "sağlık_riskleri": ["Progressive Retinal Atrophy", "Amyloidosis", "Diş eti hastalıkları", "Astım"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %32 protein", "özel_ihtiyaçlar": "Aktif - yüksek protein"},
        "yaşam_süresi": "15-20 yıl",
        "davranış": {"enerji": "Yüksek", "zeka": "Çok zeki", "ses": "Çok yüksek - konuşkan", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Balinese": {
        "bakım": {"tüy_bakımı": "Haftada 2 kez - orta uzunlukta tüy", "sosyalleşme": "Son derece sosyal - yalnız kalamaz", "göz_bakımı": "Göz akıntısı temizlenmeli"},
        "sağlık_riskleri": ["Progressive Retinal Atrophy", "Nystagmus (göz titremesi)", "Kardiyomiyopati", "Amyloidosis"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %32 protein", "özel_ihtiyaçlar": "Siamese benzeri - yüksek protein"},
        "yaşam_süresi": "12-20 yıl",
        "davranış": {"enerji": "Çok yüksek", "zeka": "Son derece zeki", "ses": "Çok yüksek", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Birman": {
        "bakım": {"tüy_bakımı": "Haftada 2-3 kez - ipeksi tüy, az düğüm yapar", "sosyalleşme": "Sakin ve sevecen", "göz_bakımı": "Mavi gözler - düzenli kontrol"},
        "sağlık_riskleri": ["Hipertrofik kardiyomiyopati", "Polikistik böbrek hastalığı", "Kornea distrofisi (göz)"],
        "beslenme": {"günlük_kalori": "280-320 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Kilo kontrolü - obeziteye eğilimli"},
        "yaşam_süresi": "12-16 yıl",
        "davranış": {"enerji": "Orta", "zeka": "Zeki", "ses": "Düşük - yumuşak ses", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "İyi"},
    },
    
    "Bombay": {
        "bakım": {"tüy_bakımı": "Haftalık - parlak siyah tüy", "sosyalleşme": "Çok sosyal - 'mini panter'", "göz_bakımı": "Bakır/altın gözler - akıntı olabilir"},
        "sağlık_riskleri": ["Hipertrofik kardiyomiyopati", "Aşırı gözyaşı", "Solunum problemleri (yassı yüz)", "Obezite"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Porsiyon kontrolü - yemek düşkünü"},
        "yaşam_süresi": "12-16 yıl",
        "davranış": {"enerji": "Yüksek", "zeka": "Çok zeki", "ses": "Yüksek - konuşkan", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "İyi"},
    },
    
    "Burmese": {
        "bakım": {"tüy_bakımı": "Minimal - haftalık fırçalama", "sosyalleşme": "Son derece sosyal ve oyuncu", "göz_bakımı": "Göz akıntısı olabilir"},
        "sağlık_riskleri": ["Hipertrofik kardiyomiyopati", "Diabetes mellitus", "Kraniyofasiyal defekt (yavru)", "Aşırı gözyaşı"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %32 protein", "özel_ihtiyaçlar": "Kilo kontrolü - obeziteye eğilimli"},
        "yaşam_süresi": "10-17 yıl",
        "davranış": {"enerji": "Yüksek", "zeka": "Çok zeki", "ses": "Orta - yumuşak", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Burmilla": {
        "bakım": {"tüy_bakımı": "Haftada 1-2 kez", "sosyalleşme": "Sosyal ve oyuncu", "göz_bakımı": "Yeşil gözler - düzenli kontrol"},
        "sağlık_riskleri": ["Polikistik böbrek hastalığı", "Hipertrofik kardiyomiyopati", "Genel olarak sağlıklı"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Standart yetişkin kedi maması"},
        "yaşam_süresi": "10-15 yıl",
        "davranış": {"enerji": "Orta-yüksek", "zeka": "Zeki", "ses": "Orta", "çocuk_uyumu": "İyi", "diğer_hayvanlar": "İyi"},
    },
    
    "Calico": {
        "bakım": {"tüy_bakımı": "Tüy uzunluğuna göre değişir", "sosyalleşme": "Bağımsız ve enerjik", "not": "Calico renk desenidir, ırk değil"},
        "sağlık_riskleri": ["Genetik çeşitlilik - genel sağlıklı", "Klinefelter sendromu (erkek calico - çok nadir)"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Altta yatan ırka göre değişir"},
        "yaşam_süresi": "12-16 yıl",
        "davranış": {"enerji": "Değişken", "zeka": "Değişken", "ses": "Değişken", "çocuk_uyumu": "Genelde iyi", "diğer_hayvanlar": "İrka bağlı"},
    },
    
    "Canadian Hairless": {
        "bakım": {"tüy_bakımı": "TÜY YOK - haftalık banyo şart", "cilt_bakımı": "Nemlendirici, güneş koruma", "sosyalleşme": "Çok sosyal - sıcaklık arar"},
        "sağlık_riskleri": ["Hipertrofik kardiyomiyopati", "Cilt enfeksiyonları", "Güneş yanığı", "Hipotermi riski"],
        "beslenme": {"günlük_kalori": "350-400 kalori - yüksek metabolizma", "protein": "En az %35 protein", "özel_ihtiyaçlar": "Sık beslenme - vücut ısısı koruma"},
        "yaşam_süresi": "12-15 yıl",
        "davranış": {"enerji": "Yüksek", "zeka": "Çok zeki", "ses": "Yüksek", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Chartreux": {
        "bakım": {"tüy_bakımı": "Haftada 1-2 kez - yoğun tüy", "sosyalleşme": "Sakin ve bağımsız", "diş_bakımı": "Düzenli kontrol"},
        "sağlık_riskleri": ["Patellar lüksasyon (diz kapağı)", "Polikistik böbrek hastalığı", "Genel olarak sağlıklı"],
        "beslenme": {"günlük_kalori": "280-320 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Kilo kontrolü önemli"},
        "yaşam_süresi": "12-15 yıl",
        "davranış": {"enerji": "Orta", "zeka": "Çok zeki", "ses": "Çok düşük - neredeyse sessiz", "çocuk_uyumu": "İyi", "diğer_hayvanlar": "İyi"},
    },
    
    "Chausie": {
        "bakım": {"tüy_bakımı": "Minimal - haftalık fırçalama", "sosyalleşme": "Çok aktif - günlük oyun şart", "alan": "Geniş alan gereksinimi"},
        "sağlık_riskleri": ["Hipertrofik kardiyomiyopati", "Hassas sindirim sistemi", "İntestinal malabsorpsiyon"],
        "beslenme": {"günlük_kalori": "320-380 kalori", "protein": "En az %35-40 protein", "özel_ihtiyaçlar": "Vahşi ata - tahılsız mama"},
        "yaşam_süresi": "12-14 yıl",
        "davranış": {"enerji": "Çok yüksek", "zeka": "Son derece zeki", "ses": "Yüksek", "çocuk_uyumu": "İyi - aktif çocuklar", "diğer_hayvanlar": "Dikkatli - dominant"},
    },
    
    "Chinchilla": {
        "bakım": {"tüy_bakımı": "Günlük fırçalama - uzun tüy", "yüz_bakımı": "Günlük göz temizliği", "sosyalleşme": "Sakin ve nazik"},
        "sağlık_riskleri": ["Polikistik böbrek hastalığı", "Solunum problemleri", "Göz problemleri", "Diş yanlış kapanışı"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %28 protein", "özel_ihtiyaçlar": "Hairball önleyici"},
        "yaşam_süresi": "12-15 yıl",
        "davranış": {"enerji": "Düşük", "zeka": "Orta", "ses": "Düşük", "çocuk_uyumu": "İyi", "diğer_hayvanlar": "İyi"},
    },
    
    "Cornish Rex": {
        "bakım": {"tüy_bakımı": "Haftalık hafif fırçalama - kıvırcık tüy", "cilt_bakımı": "Düzenli banyo - yağlanma", "sosyalleşme": "Çok aktif ve sosyal"},
        "sağlık_riskleri": ["Hipertrofik kardiyomiyopati", "Patellar lüksasyon", "Cilt yağı birikimi", "Üşümeye eğilim"],
        "beslenme": {"günlük_kalori": "300-350 kalori - yüksek metabolizma", "protein": "En az %32 protein", "özel_ihtiyaçlar": "Sık beslenme"},
        "yaşam_süresi": "12-16 yıl",
        "davranış": {"enerji": "Çok yüksek", "zeka": "Son derece zeki", "ses": "Yüksek", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Cymric": {
        "bakım": {"tüy_bakımı": "Haftada 3-4 kez - uzun tüy", "sosyalleşme": "Sosyal ve oyuncu", "kuyruk": "Kuyruksuz - omurga hassasiyeti"},
        "sağlık_riskleri": ["Manx sendromu (spina bifida)", "Megakolon", "Artrit", "Kalça displazisi"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Lif desteği - sindirim için"},
        "yaşam_süresi": "8-14 yıl",
        "davranış": {"enerji": "Orta-yüksek", "zeka": "Çok zeki", "ses": "Düşük", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "İyi"},
    },
    
    "Devon Rex": {
        "bakım": {"tüy_bakımı": "Haftalık hafif fırçalama - ince tüy", "kulak_bakımı": "Sık temizlik - büyük kulaklar", "sosyalleşme": "Son derece sosyal - 'köpek-kedi'"},
        "sağlık_riskleri": ["Hipertrofik kardiyomiyopati", "Patellar lüksasyon", "Herediter myopati", "Cilt yağı birikimi"],
        "beslenme": {"günlük_kalori": "300-350 kalori", "protein": "En az %32 protein", "özel_ihtiyaçlar": "Yüksek metabolizma"},
        "yaşam_süresi": "9-15 yıl",
        "davranış": {"enerji": "Çok yüksek", "zeka": "Çok zeki", "ses": "Yüksek", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Dilute Calico": {
        "bakım": {"tüy_bakımı": "Tüy uzunluğuna göre", "sosyalleşme": "Genelde sevecen", "not": "Renk deseni - ırk değil"},
        "sağlık_riskleri": ["Altta yatan ırka bağlı", "Genel olarak sağlıklı"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Irkına göre değişir"},
        "yaşam_süresi": "12-16 yıl",
        "davranış": {"enerji": "Değişken", "zeka": "Değişken", "ses": "Değişken", "çocuk_uyumu": "Genelde iyi", "diğer_hayvanlar": "İrka bağlı"},
    },
    
    "Dilute Tortoiseshell": {
        "bakım": {"tüy_bakımı": "Tüy uzunluğuna göre", "sosyalleşme": "Güçlü kişilik - 'tortitude'", "not": "Renk deseni"},
        "sağlık_riskleri": ["Altta yatan ırka bağlı", "Genel sağlıklı"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Irkına göre"},
        "yaşam_süresi": "12-16 yıl",
        "davranış": {"enerji": "Değişken", "zeka": "Değişken", "ses": "Değişken", "çocuk_uyumu": "Genelde iyi", "diğer_hayvanlar": "İrka bağlı"},
    },
    
    "Domestic Long Hair": {
        "bakım": {"tüy_bakımı": "Günlük fırçalama önerilir", "sosyalleşme": "Değişken kişilik", "not": "Melez - ırk değil"},
        "sağlık_riskleri": ["Genetik çeşitlilik - genelde sağlıklı", "Hairball oluşumu", "Düğümlenme"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %28 protein", "özel_ihtiyaçlar": "Hairball kontrolü"},
        "yaşam_süresi": "12-18 yıl",
        "davranış": {"enerji": "Değişken", "zeka": "Değişken", "ses": "Değişken", "çocuk_uyumu": "Genelde iyi", "diğer_hayvanlar": "Genelde iyi"},
    },
    
    "Domestic Medium Hair": {
        "bakım": {"tüy_bakımı": "Haftada 2-3 kez fırçalama", "sosyalleşme": "Uyumlu", "not": "Melez - ırk değil"},
        "sağlık_riskleri": ["Genetik çeşitlilik - sağlıklı", "Obezite eğilimi olabilir"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %28 protein", "özel_ihtiyaçlar": "Porsiyon kontrolü"},
        "yaşam_süresi": "12-18 yıl",
        "davranış": {"enerji": "Değişken", "zeka": "Değişken", "ses": "Değişken", "çocuk_uyumu": "Genelde iyi", "diğer_hayvanlar": "Genelde iyi"},
    },
    
    "Domestic Short Hair": {
        "bakım": {"tüy_bakımı": "Haftalık fırçalama yeterli", "sosyalleşme": "Uyumlu ve esnek", "not": "En yaygın - melez"},
        "sağlık_riskleri": ["Genetik çeşitlilik - çok sağlıklı", "Obezite kontrolü önemli"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %28 protein", "özel_ihtiyaçlar": "Kilo kontrolü"},
        "yaşam_süresi": "12-20 yıl",
        "davranış": {"enerji": "Değişken", "zeka": "Değişken", "ses": "Değişken", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Genelde iyi"},
    },
    
    "Egyptian Mau": {
        "bakım": {"tüy_bakımı": "Haftalık fırçalama", "sosyalleşme": "Bağlı ama utangaç", "aktivite": "Çok hızlı - en hızlı ev kedisi"},
        "sağlık_riskleri": ["Hipertrofik kardiyomiyopati", "Leukodystrophy (nadir nörolojik)", "Astım", "Hassas sindirim"],
        "beslenme": {"günlük_kalori": "280-320 kalori", "protein": "En az %32 protein", "özel_ihtiyaçlar": "Yüksek aktivite - protein"},
        "yaşam_süresi": "12-15 yıl",
        "davranış": {"enerji": "Çok yüksek", "zeka": "Çok zeki", "ses": "Orta", "çocuk_uyumu": "İyi - sakin çocuklar", "diğer_hayvanlar": "Seçici"},
    },
    
    "Exotic Shorthair": {
        "bakım": {"tüy_bakımı": "Haftada 2-3 kez", "yüz_bakımı": "Günlük göz temizliği - yassı yüz", "sosyalleşme": "Sevecen ve sakin"},
        "sağlık_riskleri": ["Polikistik böbrek hastalığı", "Solunum problemleri", "Göz akıntısı", "Diş problemleri"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %28 protein", "özel_ihtiyaçlar": "Yassı yüz - özel mama şekli"},
        "yaşam_süresi": "12-15 yıl",
        "davranış": {"enerji": "Düşük-orta", "zeka": "Orta", "ses": "Çok düşük", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "İyi"},
    },
    
    "Extra-Toes Cat - Hemingway Polydactyl": {
        "bakım": {"tüy_bakımı": "Değişken", "pati_bakımı": "Ekstra tırnaklar - sık kesim", "sosyalleşme": "Genelde sosyal", "not": "Genetik özellik - ırk değil"},
        "sağlık_riskleri": ["Genel olarak sağlıklı", "Tırnak batması riski", "Ekstra tırnak bakımı kritik"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %28 protein", "özel_ihtiyaçlar": "Altta yatan ırka göre"},
        "yaşam_süresi": "12-18 yıl",
        "davranış": {"enerji": "Değişken", "zeka": "Değişken", "ses": "Değişken", "çocuk_uyumu": "Genelde iyi", "diğer_hayvanlar": "Genelde iyi"},
    },
    
    "Havana": {
        "bakım": {"tüy_bakımı": "Haftalık fırçalama", "sosyalleşme": "Çok sosyal ve oyuncu", "diş_bakımı": "Düzenli kontrol"},
        "sağlık_riskleri": ["Üst solunum yolu enfeksiyonları", "Kalp hastalıkları", "Genel olarak sağlıklı - nadir ırk"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Kaliteli protein"},
        "yaşam_süresi": "10-15 yıl",
        "davranış": {"enerji": "Yüksek", "zeka": "Çok zeki", "ses": "Orta", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "İyi"},
    },
    
    "Himalayan": {
        "bakım": {"tüy_bakımı": "Günlük fırçalama ŞART", "yüz_bakımı": "Günlük göz temizliği", "sosyalleşme": "Sakin ve sevecen"},
        "sağlık_riskleri": ["Polikistik böbrek hastalığı", "Solunum problemleri", "Göz hastalıkları", "Diş yanlış kapanışı"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %28 protein", "özel_ihtiyaçlar": "Hairball önleyici, yassı yüz maması"},
        "yaşam_süresi": "9-15 yıl",
        "davranış": {"enerji": "Düşük", "zeka": "Orta", "ses": "Çok düşük", "çocuk_uyumu": "İyi", "diğer_hayvanlar": "İyi"},
    },
    
    "Japanese Bobtail": {
        "bakım": {"tüy_bakımı": "Haftalık fırçalama", "sosyalleşme": "Çok sosyal ve vokal", "kuyruk": "Kısa kuyruk - doğal özellik"},
        "sağlık_riskleri": ["Genel olarak çok sağlıklı", "Nadir genetik problemler"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Aktif - dengeli beslenme"},
        "yaşam_süresi": "15-18 yıl",
        "davranış": {"enerji": "Yüksek", "zeka": "Çok zeki", "ses": "Çok yüksek - şarkı söyler", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Javanese": {
        "bakım": {"tüy_bakımı": "Haftada 2 kez - orta uzunlukta", "sosyalleşme": "Son derece sosyal", "göz_bakımı": "Düzenli kontrol"},
        "sağlık_riskleri": ["Progressive Retinal Atrophy", "Amyloidosis", "Astım"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %32 protein", "özel_ihtiyaçlar": "Siamese benzeri ihtiyaçlar"},
        "yaşam_süresi": "10-15 yıl",
        "davranış": {"enerji": "Çok yüksek", "zeka": "Son derece zeki", "ses": "Çok yüksek", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Korat": {
        "bakım": {"tüy_bakımı": "Haftalık fırçalama - gümüş mavi tüy", "sosyalleşme": "Bağlı ama seçici", "göz_bakımı": "Yeşil gözler - kontrol"},
        "sağlık_riskleri": ["Gangliosidosis (GM1, GM2) - nadir", "Genel olarak sağlıklı", "Hassas immün sistem"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Kaliteli protein"},
        "yaşam_süresi": "10-15 yıl",
        "davranış": {"enerji": "Orta", "zeka": "Çok zeki", "ses": "Orta", "çocuk_uyumu": "İyi - sakin ortam", "diğer_hayvanlar": "Seçici"},
    },
    
    "LaPerm": {
        "bakım": {"tüy_bakımı": "Haftada 2 kez - kıvırcık tüy, az düğüm", "sosyalleşme": "Çok sevecen ve sosyal", "banyo": "Ara sıra - tüy yapısını korur"},
        "sağlık_riskleri": ["Genel olarak sağlıklı", "Cilt hassasiyeti olabilir"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Cilt sağlığı - omega-3"},
        "yaşam_süresi": "10-15 yıl",
        "davranış": {"enerji": "Orta-yüksek", "zeka": "Zeki", "ses": "Orta", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Manx": {
        "bakım": {"tüy_bakımı": "Haftada 2-3 kez", "sosyalleşme": "Sosyal ve oyuncu", "omurga": "Kuyruksuz - hassas omurga"},
        "sağlık_riskleri": ["Manx sendromu (spina bifida)", "Megakolon", "Artrit", "Mesane kontrolü problemleri"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Yüksek lif - sindirim"},
        "yaşam_süresi": "8-14 yıl",
        "davranış": {"enerji": "Yüksek", "zeka": "Çok zeki", "ses": "Düşük", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "İyi"},
    },
    
    "Munchkin": {
        "bakım": {"tüy_bakımı": "Değişken (kısa/uzun tüy)", "sosyalleşme": "Çok sosyal ve oyuncu", "bacaklar": "⚠️ Kısa bacaklar - tırmanma sınırlı"},
        "sağlık_riskleri": ["⚠️ Lordosis (omurga eğriliği)", "Pectus excavatum (göğüs deformitesi)", "Artrit riski", "⚠️ ETİK UYARI: Kısa bacak tartışmalı"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Kilo kontrolü - eklem sağlığı"},
        "yaşam_süresi": "12-15 yıl",
        "davranış": {"enerji": "Yüksek", "zeka": "Zeki", "ses": "Orta", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "İyi"},
    },
    
    "Nebelung": {
        "bakım": {"tüy_bakımı": "Haftada 2-3 kez - uzun gümüş-mavi tüy", "sosyalleşme": "Utangaç - yavaş ısınır", "göz_bakımı": "Yeşil gözler"},
        "sağlık_riskleri": ["Genel olarak sağlıklı", "Obezite eğilimi", "Mesane taşları"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Hassas mide - kaliteli mama"},
        "yaşam_süresi": "15-18 yıl",
        "davranış": {"enerji": "Orta", "zeka": "Çok zeki", "ses": "Düşük", "çocuk_uyumu": "İyi - sakin çocuklar", "diğer_hayvanlar": "İyi - yavaş tanıştırma"},
    },
    
    "Norwegian Forest Cat": {
        "bakım": {"tüy_bakımı": "Haftada 2-3 kez - su geçirmez tüy", "sosyalleşme": "Bağımsız ama sevecen", "tırmanma": "Tırmanma düşkünü"},
        "sağlık_riskleri": ["Hipertrofik kardiyomiyopati", "Kalça displazisi", "Glikojen depolama hastalığı tip IV", "Retinal displazi"],
        "beslenme": {"günlük_kalori": "320-380 kalori (6-9 kg)", "protein": "En az %32 protein", "özel_ihtiyaçlar": "Yavaş büyür - yüksek kalori"},
        "yaşam_süresi": "14-16 yıl",
        "davranış": {"enerji": "Orta", "zeka": "Çok zeki", "ses": "Düşük - tatlı ses", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "İyi"},
    },
    
    "Ocicat": {
        "bakım": {"tüy_bakımı": "Haftalık fırçalama", "sosyalleşme": "Son derece sosyal - yalnız kalamaz", "aktivite": "Çok aktif"},
        "sağlık_riskleri": ["Hipertrofik kardiyomiyopati", "Peri­odontal hastalık", "Renal amyloidosis", "Genel sağlıklı"],
        "beslenme": {"günlük_kalori": "280-320 kalori", "protein": "En az %32 protein", "özel_ihtiyaçlar": "Aktif - yüksek enerji"},
        "yaşam_süresi": "10-15 yıl",
        "davranış": {"enerji": "Çok yüksek", "zeka": "Çok zeki", "ses": "Yüksek", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Oriental Long Hair": {
        "bakım": {"tüy_bakımı": "Haftada 2-3 kez", "sosyalleşme": "Son derece sosyal ve bağımlı", "göz_bakımı": "Düzenli kontrol"},
        "sağlık_riskleri": ["Progressive Retinal Atrophy", "Amyloidosis", "Astım", "Hipertrofik kardiyomiyopati"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %32 protein", "özel_ihtiyaçlar": "İnce yapılı - düzenli beslenme"},
        "yaşam_süresi": "10-15 yıl",
        "davranış": {"enerji": "Çok yüksek", "zeka": "Son derece zeki", "ses": "Çok yüksek", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Oriental Short Hair": {
        "bakım": {"tüy_bakımı": "Haftalık fırçalama", "sosyalleşme": "Son derece sosyal", "diş_bakımı": "Düzenli"},
        "sağlık_riskleri": ["Progressive Retinal Atrophy", "Amyloidosis", "Astım", "Diş eti hastalıkları"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %32 protein", "özel_ihtiyaçlar": "İnce - düzenli beslenme"},
        "yaşam_süresi": "10-15 yıl",
        "davranış": {"enerji": "Çok yüksek", "zeka": "Son derece zeki", "ses": "Çok yüksek", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Oriental Tabby": {
        "bakım": {"tüy_bakımı": "Haftalık fırçalama", "sosyalleşme": "Sosyal ve aktif", "not": "Oriental desenli"},
        "sağlık_riskleri": ["Progressive Retinal Atrophy", "Amyloidosis", "Astım"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %32 protein", "özel_ihtiyaçlar": "Oriental benzeri"},
        "yaşam_süresi": "10-15 yıl",
        "davranış": {"enerji": "Çok yüksek", "zeka": "Çok zeki", "ses": "Çok yüksek", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Pixiebob": {
        "bakım": {"tüy_bakımı": "Haftada 1-2 kez", "sosyalleşme": "Köpek benzeri - sadık", "parmaklar": "Polidaktili olabilir"},
        "sağlık_riskleri": ["Hipertrofik kardiyomiyopati", "Kriptorşidizm", "Genel sağlıklı"],
        "beslenme": {"günlük_kalori": "300-350 kalori", "protein": "En az %32 protein", "özel_ihtiyaçlar": "Büyük ırk - yüksek kalori"},
        "yaşam_süresi": "13-15 yıl",
        "davranış": {"enerji": "Orta", "zeka": "Çok zeki", "ses": "Düşük - çipçip sesi", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "İyi"},
    },
    
    "Ragamuffin": {
        "bakım": {"tüy_bakımı": "Haftada 2-3 kez - ipeksi tüy", "sosyalleşme": "Çok sevecen ve sakin", "göz_bakımı": "Büyük gözler"},
        "sağlık_riskleri": ["Hipertrofik kardiyomiyopati", "Polikistik böbrek hastalığı", "Obezite"],
        "beslenme": {"günlük_kalori": "300-350 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Kilo kontrolü"},
        "yaşam_süresi": "12-16 yıl",
        "davranış": {"enerji": "Düşük", "zeka": "Zeki", "ses": "Düşük", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Selkirk Rex": {
        "bakım": {"tüy_bakımı": "Haftada 2-3 kez - kıvırcık tüy", "sosyalleşme": "Sakin ve sevecen", "banyo": "Düzenli - yağlanma"},
        "sağlık_riskleri": ["Hipertrofik kardiyomiyopati", "Polikistik böbrek hastalığı", "Kalça displazisi"],
        "beslenme": {"günlük_kalori": "280-320 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Cilt sağlığı - omega-3"},
        "yaşam_süresi": "10-15 yıl",
        "davranış": {"enerji": "Orta", "zeka": "Zeki", "ses": "Düşük", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Siberian": {
        "bakım": {"tüy_bakımı": "Haftada 3-4 kez - üç katmanlı tüy", "sosyalleşme": "Oyuncu ve sadık", "su": "Suyu sever"},
        "sağlık_riskleri": ["Hipertrofik kardiyomiyopati", "Polikistik böbrek hastalığı", "Genel sağlıklı - doğal ırk"],
        "beslenme": {"günlük_kalori": "320-380 kalori", "protein": "En az %32 protein", "özel_ihtiyaçlar": "Yavaş büyür - yüksek kalori"},
        "yaşam_süresi": "11-15 yıl",
        "davranış": {"enerji": "Yüksek", "zeka": "Çok zeki", "ses": "Orta - melodik", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Silver": {
        "bakım": {"tüy_bakımı": "Tüy uzunluğuna göre", "sosyalleşme": "Değişken", "not": "Renk deseni - ırk değil"},
        "sağlık_riskleri": ["Altta yatan ırka bağlı"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Irkına göre"},
        "yaşam_süresi": "12-16 yıl",
        "davranış": {"enerji": "Değişken", "zeka": "Değişken", "ses": "Değişken", "çocuk_uyumu": "İrka bağlı", "diğer_hayvanlar": "İrka bağlı"},
    },
    
    "Singapura": {
        "bakım": {"tüy_bakımı": "Haftalık fırçalama", "sosyalleşme": "Çok sosyal ama sessiz", "boyut": "En küçük kedi ırkı"},
        "sağlık_riskleri": ["Pyruvate kinase deficiency", "Uterin inertia (doğum sorunu)", "Hassas immün sistem"],
        "beslenme": {"günlük_kalori": "200-250 kalori (2-3 kg)", "protein": "En az %32 protein", "özel_ihtiyaçlar": "Küçük porsiyonlar - sık beslenme"},
        "yaşam_süresi": "9-15 yıl",
        "davranış": {"enerji": "Yüksek", "zeka": "Çok zeki", "ses": "Düşük - yumuşak", "çocuk_uyumu": "İyi - nazik", "diğer_hayvanlar": "İyi"},
    },
    
    "Snowshoe": {
        "bakım": {"tüy_bakımı": "Haftalık fırçalama", "sosyalleşme": "Sosyal ve vokal", "pati": "Beyaz 'kar ayakkabısı' patiler"},
        "sağlık_riskleri": ["Genel olarak sağlıklı", "Diş hastalıkları", "Kardiyomiyopati"],
        "beslenme": {"günlük_kalori": "260-300 kalori", "protein": "En az %30 protein", "özel_ihtiyaçlar": "Dengeli beslenme"},
        "yaşam_süresi": "14-19 yıl",
        "davranış": {"enerji": "Yüksek", "zeka": "Zeki", "ses": "Yüksek - konuşkan", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Somali": {
        "bakım": {"tüy_bakımı": "Haftada 2-3 kez - orta uzunlukta", "sosyalleşme": "Son derece aktif ve sosyal", "diş_bakımı": "Düzenli"},
        "sağlık_riskleri": ["Pyruvate kinase deficiency", "Progressive Retinal Atrophy", "Renal amyloidosis", "Diş eti hastalıkları"],
        "beslenme": {"günlük_kalori": "280-320 kalori", "protein": "En az %32 protein", "özel_ihtiyaçlar": "Çok aktif - yüksek protein"},
        "yaşam_süresi": "12-16 yıl",
        "davranış": {"enerji": "Çok yüksek", "zeka": "Çok zeki", "ses": "Orta", "çocuk_uyumu": "Mükemmel", "diğer_hayvanlar": "Mükemmel"},
    },
    
    "Tabby": {
        "bakım": {"tüy_bakımı": "Değişken", "sosyalleşme": "Değişken", "not": "Desen tipi - ırk değil"},
        "sağlık_riskleri": ["Altta yatan ırka bağlı", "Genel sağlıklı"],
        "beslenme": {"günlük_kalori": "250-300 kalori", "protein": "En az %28 protein", "özel_ihtiyaçlar": "Irkına göre"},
        "yaşam_süresi": "12-18 yıl",
        "davranış": {"enerji": "Değişken", "zeka": "Değişken", "ses": "Değişken", "çocuk_uyumu": "Genelde iyi", "diğer_hayvanlar": "Genelde iyi"},
    },
}

def get_breed_info(breed_name):
    """Belirli bir ırk için bilgi getirir"""
    return CAT_BREED_INFO.get(breed_name, None)

def get_all_breeds():
    """Tüm ırkların listesini döndürür"""
    return list(CAT_BREED_INFO.keys())
