from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import socket
import time
from datetime import datetime

socket.setdefaulttimeout(5)

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Transportador:
    def __init__(self):
        self.ordenes = []
        self.counter = 1
        
        # Esperar a que middleware esté listo
        time.sleep(3)
        
        self.middleware_url = 'http://middleware:9000'
        self.middleware = xmlrpc.client.ServerProxy(self.middleware_url, allow_none=True)
        
        # Registrar nodo en middleware
        for intento in range(5):
            try:
                resultado = self.middleware.registrar_nodo('transportador', 'http://transportador:9005')
                if resultado.get('success'):
                    print(f"[TRANSPORTADOR] [{timestamp()}] Registrado en middleware (intento {intento + 1})")
                    break
                else:
                    print(f"[TRANSPORTADOR] [{timestamp()}] Error registrando: {resultado.get('message')}")
            except Exception as e:
                print(f"[TRANSPORTADOR] [{timestamp()}] Error conectando con middleware (intento {intento + 1}): {e}")
            time.sleep(2)

    def ordenarTransporte(self, venta_id, destino):
        try:
            orden_id = f"T{self.counter:03d}"
            self.counter += 1
            
            orden = {
                'id': orden_id,
                'venta_id': venta_id,
                'destino': destino,
                'estado': 'programado',
                'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.ordenes.append(orden)
            print(f"[TRANSPORTADOR] [{timestamp()}] Orden de transporte creada: {orden_id} para venta {venta_id}")
            
            return {'success': True, 'data': orden, 'message': 'Transporte ordenado correctamente'}
            
        except Exception as e:
            return {'success': False, 'data': None, 'message': f'Error ordenarTransporte: {e}'}

    def ping(self):
        return True

if __name__ == '__main__':
    server = SimpleXMLRPCServer(("0.0.0.0", 9005), allow_none=True, logRequests=False)
    transportador = Transportador()
    server.register_instance(transportador)
    print(f"[TRANSPORTADOR] [{timestamp()}] Servidor Transportador iniciado en 0.0.0.0:9005")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"[TRANSPORTADOR] [{timestamp()}] Terminando transportador")