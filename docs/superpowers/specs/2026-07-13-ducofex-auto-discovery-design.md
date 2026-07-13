# DUCOFEX Auto-Discovery Design Spec

## 1. Amaç
Uygulamanın şu anki halinde kullanıcılar birbirlerini `peers.json` dosyası üzerinden bulmaktadır. Bu tasarım, ağdaki (LAN veya Tailscale) cihazların birbirlerini dinamik olarak bulmasını (Auto-Discovery) sağlayacak yapıyı tanımlar. Kullanıcı, ek bağımlılık olmadan standart UDP kütüphanesi kullanarak bu yapıyı kendisi kodlayacak, yapay zeka sadece rehberlik edip kodu inceleyecektir.

## 2. Mimari ve Yaklaşım
- **Yöntem:** UDP Broadcast (Yayın)
- **Mantık:** 
  - Uygulama başlatıldığında ağdaki tüm cihazlara "Ben buradayım" (Discovery) mesajı yayınlanır (örn. `255.255.255.255` adresine veya ilgili alt ağ yayın adresine).
  - Diğer cihazlar bu mesajı dinleyen ayrı bir thread (iş parçacığı) üzerinden alır ve gönderenin IP adresini dinamik peer (eş) listesine ekler.
  - Aynı zamanda keşif mesajı alan cihaz, "Ben de buradayım" diyerek cevap dönebilir (veya periyodik yayın yapılabilir).
  
## 3. Bileşenler
- **Discovery Gönderici (Broadcaster):**
  - Belirli bir port üzerinden (örn. port 5001) ağa UDP yayın mesajları gönderir.
  - Mesaj içeriğinde kullanıcının "nick" (kullanıcı adı) ve sohbet için dinlediği "kanal" (port) bilgisi yer alır.
- **Discovery Dinleyici (Listener):**
  - 5001 numaralı portu dinler.
  - Gelen keşif paketlerini çözer, listesinde yoksa yeni IP ve kullanıcıyı bellekte tutulan peer listesine ekler.
- **Dinamik Peer Yönetimi:**
  - `peers.json` dosyası tamamen kaldırılır veya isteğe bağlı hale getirilir.
  - Yeni mesaj gönderileceğinde, bellekte toplanan dinamik peer listesine gönderim yapılır.

## 4. Geliştirme ve Öğrenme Süreci (Kullanıcı Liderliğinde)
- Bu geliştirme süreci **öğretici bir yaklaşımla** ilerleyecektir.
- Yapay zeka kodu doğrudan yazmayacak, bunun yerine kullanıcıya küçük, yönetilebilir görevler verecektir.
- **Örnek Görev Adımları:**
  1. UDP Broadcast paketinin nasıl gönderileceğinin kodlanması.
  2. UDP Broadcast dinleyicisinin kodlanması ve main.py'ye entegre edilmesi.
  3. Dinamik listenin bellekte tutulması ve mesajlaşma fonksiyonuna bağlanması.
  
## 5. İleride Eklenecekler (Out of Scope)
- Bluetooth üzerinden eşleşme ve mesajlaşma (Bir sonraki aşamada ele alınacaktır).

## 6. Hata Yönetimi
- Aynı cihazın kendi yayınını (loopback) kendisine peer olarak eklemesi engellenmelidir.
- Ağdan kopan cihazların listeden düşürülmesi için bir zamanlayıcı (timeout) veya periyodik yayın (heartbeat) mekanizması eklenebilir.