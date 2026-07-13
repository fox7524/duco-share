# DUCOFEX LAN Auto-Discovery Uygulama Planı

## 1. Özet
Bu plan, DUCOFEX P2P Terminal Chat uygulamasına `peers.json` dosyasına gerek kalmadan ağdaki diğer kullanıcıları otomatik bulmayı sağlayan "LAN Auto-Discovery" (Yerel Ağ Otomatik Keşif) özelliğini eklemeyi kapsar. Kullanıcının talebi üzerine, kodlamayı yapay zeka doğrudan yapmayacak, kullanıcıya eğitici görevler (tasks) halinde verip rehberlik edecektir.

## 2. Mevcut Durum Analizi (Current State Analysis)
- Uygulama şu an Python UDP soketleri kullanarak şifreli (AES/şifreleme modülleri üzerinden) mesajlaşıyor.
- Kullanıcılar birbirlerini manuel olarak `peers.json` dosyasında (MagicDNS veya IP bazlı) tanımlamak zorunda.
- `udp.py`, `udp_send.py` ve `udp_rec.py` dosyalarında temel UDP gönderme/dinleme mantıkları mevcut. 
- `main.py` dosyası çalıştırıldığında nick, kanal ve şifre alıp bir dinleme thread'i (iş parçacığı) başlatıyor.

## 3. Önerilen Değişiklikler ve Öğrenme Görevleri (Proposed Changes)
Yapay zeka, kullanıcıya aşağıdaki adımları sırayla görev olarak verecek ve her adımda kullanıcının yazdığı kodu inceleyip (TRAE-code-review ve test-driven-development yeteneklerini kullanarak) yönlendirecektir:

### Görev 1: UDP Broadcast Gönderme Fonksiyonu (Kullanıcı Tarafından Yazılacak)
- **Hedef:** `udp.py` içine tüm ağa yayın yapacak bir fonksiyon eklemek.
- **Detaylar:** Kullanıcı, `socket.SO_BROADCAST` ayarını aktif ederek `255.255.255.255` adresine ve belirli bir keşif portuna (örn. 5001) paket gönderen `broadcast_discovery` adında bir fonksiyon yazacaktır.
- **Yapay Zeka Rolü:** Soketlerde broadcast izinlerinin nasıl açılacağını teorik olarak anlatmak ve kodu incelemek.

### Görev 2: Discovery (Keşif) Dinleyici Thread'i (Kullanıcı Tarafından Yazılacak)
- **Hedef:** Keşif mesajlarını sürekli dinleyen bir yapı kurmak.
- **Detaylar:** `main.py` veya `udp.py` içerisinde, 5001 portunu dinleyip gelen paketlerdeki (IP, Nick, Kanal) bilgilerini ayrıştıran bir fonksiyon yazılması.
- **Yapay Zeka Rolü:** Thread'lerin mantığını ve sonsuz döngü (while True) ile soket dinlemeyi anlatmak.

### Görev 3: Dinamik Peer Listesi ve Ana Koda Entegrasyon (Kullanıcı Tarafından Yazılacak)
- **Hedef:** Gelen keşif mesajlarındaki IP'leri bellekte (bir Python Sözlüğü / Dictionary veya Kümesi / Set) tutmak.
- **Detaylar:** 
  - `peers.json` okuma kısmı kaldırılacak.
  - Uygulama başladığında ve periyodik olarak (örn. 5 saniyede bir) ağa "Ben buradayım" mesajı yollanacak.
  - Mesajlaşma işlemi, artık sadece bellekteki dinamik peer'lara gönderilecek.
- **Yapay Zeka Rolü:** Paylaşımlı verilerde (shared memory) thread güvenliği (thread-safety) konularına değinmek ve rehberlik etmek.

## 4. Varsayımlar ve Kararlar (Assumptions & Decisions)
- Keşif (Discovery) portu olarak `5001` kullanılacaktır (Kullanıcı aksini belirtmedikçe).
- Keşif mesajları JSON formatında şifresiz veya sabit bir formatta düz metin (plain text) olarak gönderilecektir (örneğin: `DISCOVER:nick:kanal`), böylece ağa yeni katılan biri şifreyi bilmese bile keşfedilebilir, ancak sohbet mesajlarını okuyamaz/yazamaz.
- Öğrenme süreci olduğu için Bluetooth entegrasyonu bu planın kapsamı dışındadır (Sonraki aşamada ele alınacak).
- Kodlama süreci "Test-Driven" mantığına yakın, parça parça kod yazıp test edilerek ilerleyecektir.

## 5. Doğrulama Adımları (Verification Steps)
1. **Birim Testi (Manuel/Script):** Sadece `broadcast_discovery` fonksiyonu çalıştırılarak Wireshark veya basit bir script ile ağa paketin düşüp düşmediği kontrol edilecek.
2. **Yerel Test (Dogfooding):** Kullanıcı, kendi bilgisayarında 2 farklı terminal penceresi açıp uygulamanın 2 kopyasını (farklı portlarla) çalıştırarak birbirlerini otomatik bulduklarını görecek.
3. **Tailscale Testi:** Farklı bir cihazla (eğer mevcutsa) Tailscale ağı üzerinden otomatik keşfin çalışıp çalışmadığı denenecek.