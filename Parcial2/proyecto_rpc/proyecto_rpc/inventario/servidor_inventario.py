from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import socket
from datetime import datetime

socket.setdefaulttimeout(5)

def timestamp():
    """Genera marca de tiempo legible"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Inventario:
    def __init__(self):
        # Productos iniciales
        self.productos = [
            {'id': 'P001', 'nombre': 'Laptop', 'precio': 1200.0, 'cantidad': 10, 'proveedor_id': 'PROV001'},
            {'id': 'P002', 'nombre': 'Mouse', 'precio': 25.0, 'cantidad': 50, 'proveedor_id': 'PROV001'},
            {'id': 'P003', 'nombre': 'Teclado', 'precio': 75.0, 'cantidad': 30, 'proveedor_id': 'PROV002'}
        ]

        # Registrar nodo en middleware
        try:
            mw = xmlrpc.client.ServerProxy('http://middleware:9000', allow_none=True)
            mw.registrar_nodo('inventario', 'http://inventario:9002')
            print(f"[INVENTARIO] [{timestamp()}] Registrado en middleware")
        except Exception as e:
            print(f"[INVENTARIO] [{timestamp()}] Error registrando en middleware: {e}")

    # === Métodos principales ===

    def listarInventario(self):
        """Devuelve la lista completa de productos"""
        try:
            print(f"[INVENTARIO] [{timestamp()}] Listando inventario")
            return {'success': True, 'data': self.productos, 'message': 'Inventario listado correctamente'}
        except Exception as e:
            return {'success': False, 'data': None, 'message': f'Error listarInventario: {e}'}

    def cargarProductos(self):
        """
        Método solicitado por el middleware.
        Devuelve la lista de productos como carga inicial o sincronización.
        """
        try:
            print(f"[INVENTARIO] [{timestamp()}] Cargando productos para middleware")
            return {'success': True, 'data': self.productos, 'message': 'Productos cargados correctamente'}
        except Exception as e:
            return {'success': False, 'data': None, 'message': f'Error cargarProductos: {e}'}

    def actualizarInventario(self, productos_vendidos):
        """
        Actualiza las existencias del inventario tras una venta.
        productos_vendidos: [{'producto_id': 'P001', 'cantidad': 2}, ...]
        """
        try:
            for item in productos_vendidos:
                pid = item.get('producto_id')
                qty = int(item.get('cantidad', 0))
                found = False
                for p in self.productos:
                    if p['id'] == pid:
                        p['cantidad'] = max(0, p['cantidad'] - qty)
                        found = True
                        break
                if not found:
                    return {'success': False, 'data': None, 'message': f'Producto {pid} no encontrado'}
            print(f"[INVENTARIO] [{timestamp()}] Inventario actualizado tras venta")
            return {'success': True, 'data': None, 'message': 'Inventario actualizado correctamente'}
        except Exception as e:
            return {'success': False, 'data': None, 'message': f'Error actualizarInventario: {e}'}

    def verificarStockBajo(self, umbral=10):
        """Devuelve los productos cuyo stock es menor o igual al umbral"""
        try:
            bajos = [p for p in self.productos if p['cantidad'] <= umbral]
            print(f"[INVENTARIO] [{timestamp()}] Verificando stock bajo (umbral={umbral})")
            return {'success': True, 'data': bajos, 'message': 'Productos con stock bajo obtenidos'}
        except Exception as e:
            return {'success': False, 'data': None, 'message': f'Error verificarStockBajo: {e}'}

    def ping(self):
        """Verifica que el servidor esté activo"""
        return True

# === Servidor XML-RPC ===
if __name__ == '__main__':
    server = SimpleXMLRPCServer(("0.0.0.0", 9002), allow_none=True, logRequests=False)
    inv = Inventario()
    server.register_instance(inv)

    print(f"[INVENTARIO] [{timestamp()}] Servidor Inventario iniciado en 0.0.0.0:9002")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"[INVENTARIO] [{timestamp()}] Terminando inventario")
