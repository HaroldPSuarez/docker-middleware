from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from datetime import datetime
import socket

socket.setdefaulttimeout(30)

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class AtencionProveedores:
    def __init__(self):
        self.requerimientos = []
        self.counter = 1
        
        # URLs directas a servicios
        self.inventario_url = 'http://inventario:9002'
        self.compras_ventas_url = 'http://compras_ventas:9003'
        
        print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Inicializando con conexiones directas...")

    def _next_id(self):
        rid = f"REQ{self.counter:03d}"
        self.counter += 1
        return rid

    def _llamar_servicio(self, url, metodo, *args):
        """Llama directamente a un servicio"""
        try:
            proxy = xmlrpc.client.ServerProxy(url, allow_none=True)
            fn = getattr(proxy, metodo)
            return fn(*args)
        except Exception as e:
            print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Error llamando {url}.{metodo}: {e}")
            return {'success': False, 'message': str(e)}

    def cargarRequerimientosProductos(self):
        try:
            print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Consultando stock bajo...")
            
            # Consultar inventario directo
            inv_resp = self._llamar_servicio(self.inventario_url, 'verificarStockBajo', 10)
            
            if not inv_resp.get('success'):
                return {'success': False, 'data': None, 'message': 'No se pudo consultar inventario: ' + inv_resp.get('message', '')}
            
            productos_bajos = inv_resp.get('data', [])
            creados = []
            
            print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Productos con stock bajo: {len(productos_bajos)}")
            
            for p in productos_bajos:
                req = {
                    'id': self._next_id(),
                    'producto_id': p['id'],
                    'nombre_producto': p['nombre'],
                    'cantidad_actual': p['cantidad'],
                    'cantidad_solicitada': 20,  # Cantidad fija para reabastecer
                    'proveedor_id': p.get('proveedor_id', 'PROV001'),
                    'estado': 'pendiente',
                    'fecha': datetime.now().strftime("%Y-%m-%d")
                }
                self.requerimientos.append(req)
                
                # Registrar pedido en Compras/Ventas directo
                print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Registrando pedido {req['id']}...")
                reg = self._llamar_servicio(self.compras_ventas_url, 'registrarPedido', req)
                
                if not reg.get('success'):
                    print(f"[ATENCION_PROVEEDORES] [{timestamp()}] ⚠️ Error registrando pedido: {reg.get('message')}")
                else:
                    print(f"[ATENCION_PROVEEDORES] [{timestamp()}] ✅ Pedido {req['id']} registrado")
                
                creados.append(req)
            
            print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Requerimientos creados: {len(creados)}")
            return {'success': True, 'data': creados, 'message': f'Se crearon {len(creados)} requerimientos'}
            
        except Exception as e:
            error_msg = f'Error cargarRequerimientosProductos: {e}'
            print(f"[ATENCION_PROVEEDORES] [{timestamp()}] ❌ {error_msg}")
            return {'success': False, 'data': None, 'message': error_msg}

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

    def listarRequerimientos(self):
        """Nuevo método para listar todos los requerimientos"""
        return {'success': True, 'data': self.requerimientos, 'message': 'Requerimientos listados'}

    def ping(self):
        return True

if __name__ == '__main__':
    server = SimpleXMLRPCServer(("0.0.0.0", 9006), allow_none=True, logRequests=True)
    svc = AtencionProveedores()
    server.register_instance(svc)
    print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Servidor Atención Proveedores iniciado en 0.0.0.0:9006")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"[ATENCION_PROVEEDORES] [{timestamp()}] Terminando atencion_proveedores")