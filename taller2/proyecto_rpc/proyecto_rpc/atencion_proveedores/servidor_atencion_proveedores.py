from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from datetime import datetime
import socket

socket.setdefaulttimeout(5)
def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class AtencionProveedores:
    def __init__(self):
        self.requerimientos = []
        self.counter = 1
        # Registrar en middleware
        try:
            mw = xmlrpc.client.ServerProxy('http://middleware:9000', allow_none=True)
            mw.registrar_nodo('atencion_proveedores', 'http://atencion_proveedores:9006')
            print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Registrado en middleware")
        except Exception as e:
            print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Error registrando en middleware: {e}")

    def _next_id(self):
        rid = f"REQ{self.counter:03d}"
        self.counter += 1
        return rid

    def cargarRequerimientosProductos(self):
        try:
            mw = xmlrpc.client.ServerProxy('http://middleware:9000', allow_none=True)
            inv_resp = mw.rutear('inventario', 'verificarStockBajo', 10)
            if not inv_resp.get('success'):
                return {'success': False, 'data': None, 'message': 'No se pudo consultar inventario: ' + inv_resp.get('message', '')}
            productos_bajos = inv_resp.get('data', [])
            creados = []
            for p in productos_bajos:
                req = {
                    'id': self._next_id(),
                    'producto_id': p['id'],
                    'cantidad_solicitada': max(10, p['cantidad']),  # ejemplo simple
                    'proveedor_id': p.get('proveedor_id'),
                    'estado': 'pendiente',
                    'fecha': datetime.now().strftime("%Y-%m-%d")
                }
                self.requerimientos.append(req)
                # Registrar pedido en Compras/Ventas via middleware
                reg = mw.rutear('compras_ventas', 'registrarPedido', req)
                if not reg.get('success'):
                    # No abortamos; registramos el problema en el mensaje
                    print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Error registrando pedido en compras_ventas: {reg.get('message')}")
                creados.append(req)
            print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Requerimientos creados: {len(creados)}")
            return {'success': True, 'data': creados, 'message': 'Requerimientos creados'}
        except Exception as e:
            return {'success': False, 'data': None, 'message': f'Error cargarRequerimientosProductos: {e}'}

    def registrarPedido(self, producto_id, cantidad, proveedor_id):
        try:
            req = {
                'id': self._next_id(),
                'producto_id': producto_id,
                'cantidad_solicitada': cantidad,
                'proveedor_id': proveedor_id,
                'estado': 'pendiente',
                'fecha': datetime.now().strftime("%Y-%m-%d")
            }
            self.requerimientos.append(req)
            print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Pedido registrado {req['id']}")
            return {'success': True, 'data': req, 'message': 'Pedido registrado'}
        except Exception as e:
            return {'success': False, 'data': None, 'message': f'Error registrarPedido: {e}'}

    def ping(self):
        return True

if __name__ == '__main__':
    server = SimpleXMLRPCServer(("0.0.0.0", 9006), allow_none=True, logRequests=False)
    svc = AtencionProveedores()
    server.register_instance(svc)
    print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Servidor Atención Proveedores iniciado en 0.0.0.0:9006")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Terminando atencion_proveedores")
