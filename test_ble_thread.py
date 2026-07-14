import asyncio
import threading
from bless import BlessServer

def run_in_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    async def test_ble():
        try:
            print("Thread: Bless Server başlatılıyor...")
            server = BlessServer(name="DUCO_Test")
            print("Thread: Bless Server nesnesi oluşturuldu.")
            await server.start()
            print("Thread: Bless Server başlatıldı!")
            await server.stop()
        except Exception as e:
            print(f"Thread HATA: {e}")

    loop.run_until_complete(test_ble())

if __name__ == "__main__":
    t = threading.Thread(target=run_in_thread)
    t.start()
    t.join()
