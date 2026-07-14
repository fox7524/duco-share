import asyncio
from bless import BlessServer

async def test_ble():
    try:
        print("Bless Server başlatılıyor...")
        server = BlessServer(name="DUCO_Test")
        print("Bless Server nesnesi oluşturuldu.")
        await server.start()
        print("Bless Server başlatıldı!")
        await server.stop()
    except Exception as e:
        print(f"HATA: {e}")

if __name__ == "__main__":
    asyncio.run(test_ble())
