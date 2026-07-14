import asyncio
import threading
from bleak import BleakScanner, BleakClient
from bless import (
    BlessServer,
    BlessGATTCharacteristic,
    GATTCharacteristicProperties,
    GATTAttributePermissions
)

DUCOFEX_SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHAT_CHAR_UUID = "87654321-4321-8765-4321-0fedcba98765"

class BluetoothManager:
    def __init__(self, nick, kanal, dynamic_peers, on_message_callback):
        self.nick = nick
        self.kanal = kanal
        self.dynamic_peers = dynamic_peers
        self.on_message_callback = on_message_callback
        self.server = None
        self.loop = asyncio.new_event_loop()

    def start(self):
        # Asenkron döngüyü arka planda çalıştıran thread
        t = threading.Thread(target=self._run_loop, daemon=True)
        t.start()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        # Hem server'ı (GATT) hem de scanner'ı başlat
        self.loop.create_task(self._run_server())
        self.loop.create_task(self._run_scanner())
        self.loop.run_forever()

    def write_request_handler(self, characteristic: BlessGATTCharacteristic, value: bytearray, **kwargs):
        """Bless sunucusuna (bize) mesaj geldiğinde tetiklenir."""
        if characteristic.uuid == CHAT_CHAR_UUID:
            # Gelen veriyi şifre çözücüye yolla
            # value: bytearray
            # Bless adres vermez, bu yüzden adres yerine "BLE_Peer" yazıyoruz
            self.on_message_callback(bytes(value), ("BLE_Peer", 0))

    async def _run_server(self):
        try:
            server_name = f"DUCO_{self.nick}"
            self.server = BlessServer(name=server_name)

            # Karakteristiğe yazma tetikleyicisini ekliyoruz
            self.server.write_request_func = self.write_request_handler

            char_flags = (
                GATTCharacteristicProperties.write |
                GATTCharacteristicProperties.write_without_response
            )
            permissions = GATTAttributePermissions.writeable

            await self.server.add_new_service(DUCOFEX_SERVICE_UUID)
            await self.server.add_new_characteristic(
                DUCOFEX_SERVICE_UUID,
                CHAT_CHAR_UUID,
                char_flags,
                None,
                permissions
            )

            await self.server.start()
            # print(f"[BLE] GATT Sunucu baslatildi: {server_name}")
        except Exception as e:
            # Linux'ta dbus veya adaptör bulanamadığında KeyError vb. hatalar verebilir.
            # Uygulamanın çökmemesi için sessizce yakalıyoruz.
            pass

    async def _run_scanner(self):
        """Etraftaki DUCOFEX BLE cihazlarını sürekli arar."""
        while True:
            try:
                devices = await BleakScanner.discover(timeout=5.0)
                for d in devices:
                    # Cihazın yayınladığı servisler arasında DUCOFEX var mı?
                    if DUCOFEX_SERVICE_UUID in d.metadata.get("uuids", []):
                        # Kendi cihazımızı eklememek için isim kontrolü yapabiliriz
                        if d.name and d.name != f"DUCO_{self.nick}":
                            if d.address not in self.dynamic_peers:
                                self.dynamic_peers[d.address] = {
                                    "nick": d.name.replace("DUCO_", ""), 
                                    "kanal": self.kanal, 
                                    "type": "ble"
                                }
                                # Bildirimi engellemek istersen silebilirsin, şimdilik main'e bırakıyoruz
            except Exception:
                pass
            await asyncio.sleep(2)

    def send_message(self, address: str, payload: bytes):
        """Ana koddan BLE üzerinden mesaj atmak için kullanılır."""
        # Asenkron fonksiyonu thread-safe şekilde loop'a gönder
        asyncio.run_coroutine_threadsafe(self._async_send(address, payload), self.loop)

    async def _async_send(self, address: str, payload: bytes):
        try:
            async with BleakClient(address, timeout=5.0) as client:
                await client.write_gatt_char(CHAT_CHAR_UUID, payload, response=False)
        except Exception as e:
            pass # Bağlantı hatası
