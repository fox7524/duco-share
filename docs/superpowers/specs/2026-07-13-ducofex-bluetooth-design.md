# DUCOFEX Bluetooth (BLE) Hybrid Mode Design Spec

## 1. Amaç
Mevcut yerel ağ ve Tailscale destekli UDP mesajlaşma uygulamasına, İnternet veya yerel ağ olmadan cihazların birbirini bulup mesajlaşmasını sağlayan **Bluetooth Low Energy (BLE)** desteğinin eklenmesi. Uygulama **Hibrit Mod**'da çalışarak hem UDP hem de Bluetooth bağlantılarını aynı anda yönetecek ve mesajları uygun kanaldan (veya her ikisinden) iletecektir.

## 2. Mimari ve Kütüphaneler (Apple Silicon Uyumluluğu)
macOS üzerinde standart AF_BLUETOOTH soketleri çalışmadığı için modern BLE mimarisi kullanılacaktır.
- **Bleak (İstemci / Central):** Ağdaki diğer DUCOFEX cihazlarını taramak (scan) ve onlara şifreli mesaj paketlerini yazmak için kullanılacak.
- **Bless (Sunucu / Peripheral):** Cihazın kendi Bluetooth radyosu üzerinden "Ben bir DUCOFEX cihazıyım" yayını (advertise) yapması ve diğer cihazlardan gelen mesajları karşılaması (GATT Server) için kullanılacak.
- **Asenkron Yapı:** BLE kütüphaneleri `async/await` mimarisiyle çalışır. Mevcut `threading` tabanlı UDP yapısıyla asenkron BLE yapısını uyumlu çalıştırmak için `asyncio` event loop'ları kullanılacaktır.

## 3. BLE GATT Yapısı (Servisler ve Karakteristikler)
BLE cihazları verileri Servis (Service) ve Karakteristik (Characteristic) adı verilen UUID'ler ile taşır.
- **DUCOFEX_SERVICE_UUID:** Uygulamaya özel sabit bir UUID. Sadece bu UUID'yi yayınlayan cihazlar peer olarak kabul edilecek.
- **CHAT_CHARACTERISTIC_UUID:** Yazma (Write) yetkisine sahip bir karakteristik. Karşı taraf mesaj göndermek istediğinde bu karakteristiğe byte dizisini (şifreli mesajı) yazacak.

## 4. Bileşenler
- **BLE Peripheral Task (Bless):** 
  - Kendi GATT sunucusunu ayağa kaldırır.
  - Cihazın `nick` bilgisini de içerecek şekilde yayın (advertise) yapar.
  - `CHAT_CHARACTERISTIC` üzerine bir yazma işlemi olduğunda, gelen veriyi mevcut `on_packet` (şifre çözme ve ekrana yazdırma) fonksiyonuna iletir.
- **BLE Central Task (Bleak):**
  - Arka planda sürekli tarama yapar.
  - `DUCOFEX_SERVICE_UUID` yayını yapan bir cihaz bulursa, onu `dynamic_peers` listesine Bluetooth etiketiyle (örn. `{"type": "ble", "address": MAC/UUID}`) ekler.
- **Mesaj Yönlendirici (Message Router):**
  - Kullanıcı mesaj yazdığında, `dynamic_peers` listesi döngüye sokulur.
  - Peer bir IP adresiyse (UDP), paket UDP soketinden atılır.
  - Peer bir BLE adresiyse, `bleak` üzerinden ilgili cihaza bağlanılıp karakteristiğine yazılır.

## 5. Geliştirme ve Öğrenme Süreci (Kullanıcı Liderliğinde)
Bu aşama asenkron programlama ve BLE konseptleri içerdiğinden, görevler dikkatli bölünecektir:
1. **Görev 1: Gerekli Kütüphanelerin Kurulumu:** `bleak` ve `bless` paketlerinin yüklenmesi.
2. **Görev 2: BLE Sunucu (Bless) Kodlanması:** Yeni bir `bluetooth_server.py` dosyası oluşturup, cihazın kendini anons etmesinin kodlanması.
3. **Görev 3: BLE Tarayıcı (Bleak) Kodlanması:** Yeni bir `bluetooth_client.py` dosyasında etraftaki cihazların taranması.
4. **Görev 4: Hibrit Entegrasyon:** Yazılan asenkron BLE kodlarının `main.py` içindeki mevcut Thread mimarisiyle birleştirilmesi.

## 6. Hata Yönetimi ve Kısıtlamalar
- macOS, BLE cihazlarının gerçek MAC adreslerini gizler ve yerine dinamik UUID'ler verir. Bu yüzden cihazları eşleştirirken MAC adresi yerine UUID bazlı ilerlenecektir.
- BLE paket boyutları küçüktür (genellikle 20-512 byte). Eğer mesajlar şifrelemeyle birlikte çok büyürse, mesaj parçalama (chunking) gerekebilir. İlk aşamada kısa mesajların doğrudan gönderildiği varsayılacaktır.