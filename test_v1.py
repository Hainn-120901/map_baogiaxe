
from map_general.map_hang_muc_xe.map_hang_muc_xe_final import MapHangMucXe
import time
model = MapHangMucXe()
test = '''Kính chắn gió trước KGQC/KGQDE4'''

for text in test.split('\n'):
    print(text)
    # text = ('Sơn cửa sau trái')
    start = time.time()
    rs = model.map_hang_muc_xe(text)
    print(time.time() - start)
    print(rs)
