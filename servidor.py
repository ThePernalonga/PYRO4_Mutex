# Trabalho 2 de Sistemas Distribuidos
# Arquitetura Cliente-Servidor, Eventos e Notificações,
#
# JAVA RMI ou PYRO
#
# Andre L. G. Santos 2090279

import sys
import Pyro4
import Crypto.Hash.SHA256
import Crypto.PublicKey.RSA
from Crypto.Signature.pkcs1_15 import PKCS115_SigScheme as PKCS115
from Crypto.Hash import SHA256
from threading import Thread, Lock, Event

# Identificacao de chaves
SIGNER = PKCS115
SIGN_PUB = []
SIGN_PRI = []

# Tempo maximo de acesso ao recurso
TEMP_MAX = 10

# Identificacao de recurso
COCA = 1
PEPSI = 2

# Identificadores para fila de processos
IDENTIFIER1 = ""
IDENTIFIER2 = ""
REC1_FREE = True
REC2_FREE = True
FILAREC1 = []
FILAREC2 = []
CALLBACKS1 = []
CALLBACKS2 = []

# Lista dos processos conectados
PROC_NAME_LIST = []

@Pyro4.behavior(instance_mode="single")
class Servidor(object):
  @Pyro4.expose  
  def doCallback(self, callback): # Callback inicial
    print(">Realizando callback no client")
    self.notify = callback
    return callback.call1()
  
  # Fila de callbacks
  @Pyro4.expose  
  def iniCallbacks1(self, callback):
    if(len(FILAREC1) > 0):
      CALLBACKS1.append(callback)
  
  # Fila de callbacks
  @Pyro4.expose  
  def iniCallbacks2(self, callback):
    if(len(FILAREC2) > 0):
      CALLBACKS2.append(callback)
  
  notify = {} # Objeto de comunicacao callback
  # Eventos de wait e lock para os recursos
  lock1 = Lock()
  lock2 = Lock()
  exit1 = Event()
  exit2 = Event()
  
  # Retorna se o cliente tem o recurso
  @Pyro4.expose
  def isClientWithRec(self, procid):
    return procid == IDENTIFIER1
  
  # Funcao para liberar reursos
  @Pyro4.expose
  def freeRec(self, rec):
    if rec == COCA:
      self.exit1.set()
    elif rec == PEPSI:
      self.exit2.set()
    else:
      return -1
  
  # Fila de processos do recurso 1
  def task1(self, lock, identifier, value):
    global REC1_FREE, IDENTIFIER1
    with lock:
      REC1_FREE = False
      if len(FILAREC1) == 0:
        IDENTIFIER1 = ""
        REC1_FREE = True
        print(f'>Processo {IDENTIFIER1} liberou! COCA')
      else:
        self.exit1.clear()
        IDENTIFIER1 = FILAREC1[0]
        print(f'>Processo {IDENTIFIER1} está segurando por {value} segundos')
        while not self.exit1.is_set():
          self.exit1.wait(value)
          self.exit1.set()
        FILAREC1.pop(0)
        if len(CALLBACKS1) > 0 and len(FILAREC1) > 0:
          CALLBACKS1[1].notify("Recurso Livre!")
        CALLBACKS1.pop(0)
        REC1_FREE = True
        self.lock1 = Lock()
        self.task1(self.lock1, IDENTIFIER1, value)
  
  # Fila de processos do recurso 2
  def task2(self, lock, identifier, value):
    global REC2_FREE, IDENTIFIER2
    with lock:
      REC2_FREE = False
      if len(FILAREC2) == 0:
        IDENTIFIER2 = ""
        REC2_FREE = True
        print(f'>Processo {IDENTIFIER2} liberou! PEPSI')
      else:
        self.exit2.clear()
        IDENTIFIER2 = FILAREC2[0]
        print(f'>Processo {IDENTIFIER2} está segurando por {value} segundos')
        while not self.exit2.is_set():
          self.exit2.wait(value)
          self.exit2.set()
        FILAREC2.pop(0)
        if len(CALLBACKS2) > 0 and len(FILAREC2) > 0:
          CALLBACKS2[1].notify("Recurso Livre!")
        CALLBACKS2.pop(0)
        REC2_FREE = True
        self.lock2 = Lock()
        self.task2(self.lock2, IDENTIFIER2, value)
        
  # Funcao para adicionar processos e checar primeira conexao
  @Pyro4.expose
  def msgIni(self, name):
    print("Sua conexão foi estabelecida com sucesso! ID: " + name)
    PROC_NAME_LIST.append(name)
    return 1

  # Funcao para remover processos
  @Pyro4.expose
  def removeClient(self, name):
    print("Cliente " + name + " foi desconectado!")
    PROC_NAME_LIST.remove(name)
    return 1

  # Funcao para dar acesso aos recursos
  @Pyro4.expose
  def AcessoRecurso(self, name, tipo: int):
    global REC1_FREE, REC2_FREE
    if tipo == COCA:
      global FILAREC1
      if REC1_FREE == True:
        FILAREC1.append(name)
        CALLBACKS1.append(self.notify)
        Thread(target = self.task1, args=(self.lock1, name, TEMP_MAX)).start()
      
      elif REC1_FREE == False:
        FILAREC1.append(name)
        return 1
      return 1
    
    if tipo == PEPSI:
      global FILAREC2
      if REC2_FREE == True:
        FILAREC2.append(name)
        CALLBACKS2.append(self.notify)
        Thread(target = self.task2, args=(self.lock2, name, TEMP_MAX)).start()
      
      elif REC2_FREE == False:
        FILAREC2.append(name)
        return 1
      return 1
    
  # Funcao para enviar a chave publica
  @Pyro4.expose
  def get_public_key(self):
    return SIGN_PUB

  # Funcao que gera chaves
  def chavesPP():
    print("Gerando chaves...")
    SIGN_PRI = Crypto.PublicKey.RSA.generate(1024)
    SIGN_PUB = SIGN_PRI.publickey()
    SIGNER = PKCS115(SIGN_PRI)
    return 1

  print("Servidor iniciado!")
  # Caso eles nao consigam gerar chaves ele fecha o servidor
  try:
    inicio = chavesPP()
    if inicio == 1:
      print("Chaves geradas com sucesso!")
    else:
      print("Erro ao gerar chaves!")
      raise RuntimeError()
      
  
  except RuntimeError as e:
      # Any other exception - something happened, exit
      print('Reading error: '.format(str(e)))
      sys.exit()
      
  
  # Inicia o servidor
daemon = Pyro4.Daemon()
uri = daemon.register(Servidor)
print(uri)
ns = Pyro4.locateNS()
ns.register("Servidor", uri)
daemon.requestLoop()
