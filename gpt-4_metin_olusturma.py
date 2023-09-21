import openai
import speech_recognition as sr
from gtts import gTTS
import subprocess
import os
from pydub import AudioSegment
import time

# API anahtarınızı buraya ekleyin
openai.api_key = "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"
recognizer = sr.Recognizer()

# Mikrofonu başlatın
microphone = sr.Microphone()
print("Ses dinleniyor...")

def sesten_metne():
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=10)
            # Ses tanıma işlemini gerçekleştirin
            text = recognizer.recognize_google(audio, language="tr-TR")
            if len(text) > 150:
                print("Ses belirlenmiş üst sınır olan '150' karakteri geçtiğinden dolayı fesh edildi!")
                return None
            else:
                print("Tanıma sonucu: " + text)
                return text
        except sr.WaitTimeoutError:
            print("Süre doldu. Tekrar dinlemek için devam ediliyor...")
            return None
        except sr.UnknownValueError:
            print("Ses anlaşılamadı.")
            return None
        except sr.RequestError as e:
            print("Ses tanıma hatası: {0}".format(e))
            return None

def metin_olusturma(metin):
    global reply
    # Kullanıcı girişini mesajlara ekle
    messages.append({"role": "user", "content": metin})
    
    # Modelin öğrenmesi ve tweet oluşturması için mesajları birleştir
    input_text = "\n".join([system_msg] + [database] + [metin])
    
    # Tweet tarzında bir yanıt oluştur
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=girdi_karakter  # İstenilen tweet uzunluğunu ayarla
    )
    
    reply = response["choices"][0]["message"]["content"]
    
    # Oluşturulan tweeti mesajlara ekle
    messages.append({"role": "assistant", "content": reply})
    
    # Oluşturulan tweeti yazdır
    print("\n" + reply + "\n")
    return reply
        
def puanlama(): # Kullanmıyoruz şu an
    # Kullanıcıdan puan alın
    user_rating = int(input("Bu çıktıyı 1 ila 5 arasında nasıl puanlarsınız? (1 = kötü, 5 = harika): "))
    
    # Kullanıcı değerlendirmesini kaydet
    with open("user_ratings.txt", "a", encoding="utf-8") as ratings_file:
        ratings_file.write(f"Çıktı: {reply}\nPuan: {user_rating}\n\n")
    
    # Kullanıcı puanına göre iyileştirme yap
    if user_rating < 3:
        # İyileştirme mekanizması burada olmalıdır.
        print("Bu çıktıyı iyileştirmeye çalışıyoruz...")
        # İyileştirilen çıktıyı kullanıcıya sunun ve kaydet
        improved_output = "İyileştirilen çıktı burada olacak."
        print("\n" + improved_output + "\n")
        messages[-1]["content"] = improved_output  # Son mesajı iyileştirilen çıktıyla değiştirin
        with open("user_ratings.txt", "a", encoding="utf-8") as ratings_file:
            ratings_file.write(f"İyileştirilmiş Çıktı: {improved_output}\n\n")

def metinden_sese(seslendirilecek):
    dil = 'tr'
    # gTTS tarafından metni ses dosyasına dönüştür
    ses = gTTS(text=seslendirilecek, lang=dil, slow=False)
    ses_dosyasi = "ses.mp3"
    ses.save(ses_dosyasi)
    
    # Ses dosyasını yükle
    ses_segment = AudioSegment.from_mp3(ses_dosyasi)
    
    # Ses hızını 1.25x olarak ayarla
    ses_hizlandirilmis = ses_segment.speedup(playback_speed=1.25)
    
    # Hızlandırılmış sesi kaydet
    hizlandirilmis_ses_dosyasi = "hizlandirilmis_ses.mp3"
    ses_hizlandirilmis.export(hizlandirilmis_ses_dosyasi, format="mp3")
    
    # Ses dosyasını oynat
    subprocess.Popen(["kde-open", hizlandirilmis_ses_dosyasi])
    
    # Sesin uzunluğunu al
    uzunluk_milisaniye = len(ses_hizlandirilmis)
    uzunluk_saniye = uzunluk_milisaniye / 1000
    
    # Ses çalınana kadar bekle
    time.sleep(uzunluk_saniye*0.85 + 1)
    
    # Geçici dosyaları temizle
    os.remove(ses_dosyasi)
    os.remove(hizlandirilmis_ses_dosyasi)
    
    time.sleep(2)

# Veritabanı dosyasından tweetleri oku
with open("database.txt", "r", encoding="utf-8") as file:
    database = file.read()

system_msg = """Ben yaşadığım bir hikayeyi anlatacağım ve bunları database'den öğrendiklerinle dönüştüreceksin.
asla hikaye dışında bir çıktı çıkmayacak. Bu hikaye çevrildiğinde eğlenceli ve doğal bir üslup kullanılarak yazılacak.
Cümlenin yapısı serbest, doğal ve hatta anlamsız olabilir. Sokak ağzıyla konuşmak, kelimelerin bozuk olması gibi.
Çok hafif sürece argo kullanımı da olabilir. Ben merkezli konuşacaksın, Özne sensin.
Çıktı karakter sayısı user input'un en fazla bir buçuk katı olacak."""
messages = [{"role": "system", "content": system_msg}]

while True:
    metin = sesten_metne()
    if metin is not None:
        if "komut kapat" in metin.lower():
            print("Döngüden çıktım")
            break
        else:
            # Girdi karakter sayısını hesapla
            girdi_karakter = len(metin) * 1.5
            girdi_karakter = int(girdi_karakter)

            reply = metin_olusturma(metin)

            # Yanıt boş değilse ve karakter sınırını aşmıyorsa seslendir
            if reply and girdi_karakter < 150:
                metinden_sese(reply)

print("Program sona erdi.")

print("Program sona erdi.")
