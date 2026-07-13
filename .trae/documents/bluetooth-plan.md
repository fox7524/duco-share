# DUCOFEX Bluetooth (BLE) Uygulama Planı

## 1. Özet
Bu plan, daha önce oluşturulan tasarım spesifikasyonuna dayanarak, macOS (Apple Silicon) uyumlu asenkron BLE (Bleak ve Bless kütüphaneleri) yapısının adım adım nasıl uygulanacağını tanımlar. Tıpkı UDP'de olduğu gibi, kodlama süreci öğretici bir yaklaşımla kullanıcının katılımıyla yapılacaktır.

## 2. Mevcut Durum Analizi
- Uygulama şu an UDP üzerinden şifreli mesajlaşıyor, periyodik yayın (heartbeat) ile ağdaki kullanıcıları otomatik buluyor.
- Arayüz renkli ve UX açısından zenginleştirilmiş durumda.
- Mevcut mimari `threading` (iş parçacığı) kullanıyor. BLE kütüphaneleri ise `asyncio` (asenkron) kullanır. Bu ikisinin birbirine bağlanması (bridge) gerekmektedir.

## 3. Önerilen Değişiklikler ve Görevler (Kullanıcı Tarafından Yapılacak)

### Görev 1: Kütüphanelerin Kurulumu ve Hazırlık
- **Aksiyon:** `pip install bleak bless` komutuyla gerekli asenkron Bluetooth kütüphanelerinin kurulması.
- **Yapay Zeka Rolü:** Kütüphanelerin ne işe yaradığını kısaca açıklamak.

### Görev 2: Bluetooth Modülünün (GATT Sunucu) Oluşturulması
- **Dosya:** Yeni bir dosya `bluetooth_core.py` (veya benzeri)
- **Aksiyon:** Cihazın kendi MAC/UUID adresini ve "DUCOFEX" ismini yayması (advertise) için `Bless` kütüphanesini kullanan asenkron bir sunucu fonksiyonu yazılması. Gelen verileri alacak bir karakteristiğin (Characteristic) tanımlanması.
- **Yapay Zeka Rolü:** GATT, Servis ve Karakteristik kavramlarını açıklamak, kod iskeletini verip doldurulmasını istemek.

### Görev 3: Bluetooth Tarayıcı (Scanner) Oluşturulması
- **Dosya:** `bluetooth_core.py`
- **Aksiyon:** Etraftaki DUCOFEX servis UUID'sine sahip cihazları tarayan ve bulduğunda `dynamic_peers` sözlüğüne ekleyen (Bluetooth modunda olduğunu belirterek) bir `BleakScanner` fonksiyonu yazılması.
- **Yapay Zeka Rolü:** Asenkron tarama döngüsünü anlatmak.

### Görev 4: Ana Koda (main.py) Entegrasyon ve Mesaj Yönlendirme
- **Dosya:** `main.py`
- **Aksiyon:** 
  1. Asenkron Bluetooth döngüsünü arka planda bir Thread içinde başlatacak bir köprü (bridge) kurulması.
  2. Kullanıcı mesaj gönderdiğinde döngünün güncellenmesi: Peer'in tipi "udp" ise `send_to` fonksiyonu, "ble" ise Bleak üzerinden Bluetooth karakteristiğine yazma işlemi yapılması.
- **Yapay Zeka Rolü:** Senkron (Thread) ve Asenkron (asyncio) kodların nasıl birleştirileceğini göstermek.

## 4. Varsayımlar ve Kararlar
- Sabit bir Service UUID (örn. `0000ffe0-0000-1000-8000-00805f9b34fb`) ve Write/Read destekli bir Characteristic UUID kullanılacaktır.
- Şifreli paketler byte dizisi olarak Bluetooth üzerinden tek parça halinde (MTU limitlerine sığdığı varsayılarak) gönderilecektir. Gerekirse ileride parçalama eklenebilir.

## 5. Doğrulama Adımları
1. Kodlar yazıldıktan sonra `bluetooth_core.py` bağımsız çalıştırılarak cihazın Bluetooth üzerinden görünürlüğü test edilecek (Telefondaki bir BLE Scanner uygulamasıyla).
2. `main.py` üzerinden mesaj atılarak Bluetooth'tan hedefe ulaşıp ulaşmadığı kontrol edilecek.