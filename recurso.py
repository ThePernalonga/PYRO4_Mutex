import threading
import time

TIME_HOLD = 3

mutex = threading.Lock()

class recursoPri(threading.Thread):
	def run(self):
		global mutex
		print("Primeiro recurso em uso")
		time.sleep(TIME_HOLD)
		print("Primeiro recurso liberado")
		mutex.release()
 
class recursoSec(threading.Thread):
	def run(self):
		global mutex
		print("Segundo recurso em uso")
		time.sleep(TIME_HOLD)
		mutex.acquire()
		print("Segundo recurso liberado")
  
mutex.acquire()
t1 = recursoPri()
t2 = recursoSec()
t1.start()
t2.start()