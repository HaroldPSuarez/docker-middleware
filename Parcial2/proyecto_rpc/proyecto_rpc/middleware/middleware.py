from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import socket
import os
import time
from datetime import datetime

RPC_TIMEOUT = 30
socket.setdefaulttimeout(RPC_TIMEOUT)

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class MiddlewareRPC:
    def __init__(self):
        self.running_in_docker = os.path.exists('/.dockerenv')

        if self.running_in_docker:
            print(f"[MIDDLEWARE] [{timestamp()}] Ejecutándose dentro de Docker")
            self.nodos = {
                'tienda': 'http://tienda:9001',
                'inventario': 'http://inventario:9002',
                'compras_ventas': 'http://compras_ventas:9003',
                'contabilidad': 'http://contabilidad:9004',
                'transportador': 'http://transportador:9005',
                'atencion_proveedores': 'http://atencion_proveedores:9006'
            }
        else:
            print(f"[MIDDLEWARE] [{timestamp()}] Ejecutándose en entorno local")
            self.nodos = {
                'tienda': 'http://localhost:9001',
                'inventario': 'http://localhost:9002',
                'compras_ventas': 'http://localhost:9003',
                'contabilidad': 'http://localhost:9004',
                'transportador': 'http://localhost:9005',
                'atencion_proveedores': 'http://localhost:9006'
            }

    def rutear(self, nodo_destino, funcion, *args):
        """Solo para el cliente externo - no para comunicación interna"""
        try:
            if nodo_destino not in self.nodos:
                return {'success': False, 'data': None, 'message': f'Nodo desconocido: {nodo_destino}'}

            url = self.nodos[nodo_destino]
            print(f"[MIDDLEWARE] [{timestamp()}] Ruteando {nodo_destino}.{funcion} a {url}")

            proxy = xmlrpc.client.ServerProxy(url, allow_none=True)
            fn = getattr(proxy, funcion)
            respuesta = fn(*args)
            
            print(f"[MIDDLEWARE] [{timestamp()}] Respuesta de {nodo_destino}.{funcion}: {respuesta.get('success') if isinstance(respuesta, dict) else 'OK'}")
            return respuesta

        except Exception as e:
            error_msg = f'Error rutear {nodo_destino}.{funcion}: {e}'
            print(f"[MIDDLEWARE] [{timestamp()}] {error_msg}")
            return {'success': False, 'data': None, 'message': error_msg}

    def ping(self):
        return True

    def health_check(self):
        """Verifica el estado de todos los nodos"""
        resultados = {}
        for nombre, url in self.nodos.items():
            try:
                proxy = xmlrpc.client.ServerProxy(url, allow_none=True)
                resultados[nombre] = proxy.ping() if hasattr(proxy, 'ping') else False
            except:
                resultados[nombre] = False
        return resultados

if __name__ == '__main__':
    server = SimpleXMLRPCServer(("0.0.0.0", 9000), allow_none=True, logRequests=True)
    middleware = MiddlewareRPC()
    server.register_instance(middleware)
    print(f"[MIDDLEWARE] [{timestamp()}] Middleware RPC iniciado en 0.0.0.0:9000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"[MIDDLEWARE] [{timestamp()}] Terminando middleware")