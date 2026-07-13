# DUCOFEX Auto-Discovery Fix & UX Plan

## 1. Özet
Kullanıcıların tek taraflı mesaj gönderebilmesi (birinin mesajının gidip diğerininkinin gitmemesi) sorununu çözmek ve terminal arayüzünü renklendirerek (UX Friendly) daha iyi bir deneyim sunmak amaçlanmaktadır.

## 2. Mevcut Durum ve Sorun Analizi
- **Sorun:** 1. Kullanıcı uygulamayı açtığında ağa yayın (broadcast) yapıyor. 2. Kullanıcı uygulamayı sonradan açtığı için bu yayını duyamıyor ve bellekteki (dynamic_peers) listesi boş kalıyor. 2. Kullanıcı yayın yaptığında ise 1. Kullanıcı bunu duyup listesine ekliyor. Sonuç olarak 1. Kullanıcı mesaj atabiliyor, ancak 2. Kullanıcının listesi boş olduğu için yazdıkları ağa gitmiyor.
- **`peers.json` Durumu:** Dosyadan okuma işlemi zaten iptal edildi. Bahsedilen "liste", kod içindeki `dynamic_peers` isimli RAM'de tutulan sözlüktür.

## 3. Önerilen Değişiklikler

### Adım 1: Periyodik Yayın (Heartbeat) Thread'i
- **Dosya:** `main.py`
- **Aksiyon:** Uygulamanın sadece ilk açılışta değil, her 3-5 saniyede bir arka planda ağa "Ben buradayım" mesajı göndermesi sağlanacak.
- **Neden:** Böylece kim ne zaman katılırsa katılsın, en geç birkaç saniye içinde ağdaki herkesin belleğindeki `dynamic_peers` listesine eklenebilecek. Karşılıklı mesajlaşma sorunu çözülecek.

### Adım 2: UX ve Renkli Terminal
- **Dosya:** `main.py` (Gerekirse `requirements.txt` eklenebilir ancak standart terminal renk kodları (ANSI) kullanarak dışa bağımlılığı da sıfır tutabiliriz).
- **Aksiyon:** 
  - Kendi mesajlarımız, başkalarının mesajları ve sistem bildirimleri (örn. "Yeni biri katıldı") için ANSI renk kodları eklenecek.
  - Örneğin: Kendi mesajlarımız için varsayılan renk, başkalarından gelenler için MAVİ, sistem uyarıları için YEŞİL kullanılacak.
  - Gelen mesajlarda `\r` ve boşluklar kullanılarak terminal prompt'unun (`> `) üstüne düzgün yazdırılması (UX) sağlanacak.

## 4. Varsayımlar
- ANSI escape kodları (ör: `\033[92m`) modern terminallerde (macOS dahil) sorunsuz çalıştığı için ekstra bir kütüphane (rich/colorama) kurmadan hızlıca çözülecektir.

## 5. Doğrulama Adımları
1. Kodlar eklendikten sonra iki terminal açılacak.
2. 1. Terminal açılıp beklenecek, ardından 2. Terminal açılacak.
3. Birkaç saniye içinde her iki terminalin de birbirini "Yeni biri katıldı" olarak görüp görmediği teyit edilecek.
4. Her iki taraftan da renkli bir şekilde karşılıklı mesaj atılıp alınabildiği doğrulanacak.