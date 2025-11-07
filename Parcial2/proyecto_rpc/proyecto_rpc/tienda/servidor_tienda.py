from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
import socket
import time
from datetime import datetime

socket.setdefaulttimeout(30)

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Tienda:
    def __init__(self):
        self.ventas = []
        self.counter = 1
        
        # URLs directas a los servicios (sin pasar por middleware)
        self.inventario_url = 'http://inventario:9002'
        self.compras_ventas_url = 'http://compras_ventas:9003' 
        self.transportador_url = 'http://transportador:9005'
        
        print(f"[TIENDA] [{timestamp()}] Inicializando con conexiones directas...")

    def _next_id(self):
        vid = f"V{self.counter:03d}"
        self.counter += 1
        return vid

    def _llamar_servicio(self, url, metodo, *args):
        """Llama directamente a un servicio sin pasar por middleware"""
        try:
            proxy = xmlrpc.client.ServerProxy(url, allow_none=True)
            fn = getattr(proxy, metodo)
            return fn(*args)
        except Exception as e:
            print(f"[TIENDA] [{timestamp()}] Error llamando {url}.{metodo}: {e}")
            return {'success': False, 'message': str(e)}

    def registrarVenta(self, cliente_id, productos, destino):
        """
        pasos:
         1. Verificar stock en inventario (directo)
         2. Solicitar registro a compras_ventas (directo) 
         3. Si todo ok, ordenar transporte (directo)
        """
        print(f"[TIENDA] [{timestamp()}] INICIANDO venta para {cliente_id}")
        
        try:
            # Paso 1: Obtener inventario directo
            print(f"[TIENDA] [{timestamp()}] Consultando inventario...")
            inv_resp = self._llamar_servicio(self.inventario_url, 'cargarProductos')
            
            if not inv_resp.get('success'):
                return {'success': False, 'data': None, 'message': 'No se pudo consultar inventario: ' + inv_resp.get('message', '')}

            productos_inv = {p['id']: p for p in inv_resp['data']}

            # Verificar stock
            for item in productos:
                pid = item['producto_id']
                qty = int(item['cantidad'])
                if pid not in productos_inv:
                    return {'success': False, 'data': None, 'message': f'Producto {pid} no existe'}
                if productos_inv[pid]['cantidad'] < qty:
                    return {'success': False, 'data': None, 'message': f'Stock insuficiente para {pid}'}

            # Construir venta
            venta_id = self._next_id()
            venta = {
                'id': venta_id,
                'fecha': datetime.now().strftime("%Y-%m-%d"),
                'cliente_id': cliente_id,
                'productos': [],
                'total': 0.0
            }
            
            total = 0.0
            for item in productos:
                pid = item['producto_id']
                qty = int(item['cantidad'])
                precio_unit = productos_inv[pid]['precio']
                venta['productos'].append({
                    'producto_id': pid, 
                    'cantidad': qty, 
                    'precio_unitario': precio_unit
                })
                total += precio_unit * qty
                
            venta['total'] = round(total, 2)
            print(f"[TIENDA] [{timestamp()}] Venta construida: {venta_id}")

            # Paso 2: Registrar en compras_ventas directo
            print(f"[TIENDA] [{timestamp()}] Registrando en compras_ventas...")
            reg_resp = self._llamar_servicio(self.compras_ventas_url, 'registrarCompra', venta)
            
            if not reg_resp.get('success'):
                return {'success': False, 'data': None, 'message': 'No se pudo registrar en ComprasVentas: ' + reg_resp.get('message', '')}

            # Paso 3: Ordenar transporte directo
            print(f"[TIENDA] [{timestamp()}] Ordenando transporte...")
            tr_resp = self._llamar_servicio(self.transportador_url, 'ordenarTransporte', venta_id, destino)

            # Guardar localmente
            self.ventas.append(venta)
            print(f"[TIENDA] [{timestamp()}] Venta {venta_id} completada")
            
            return {
                'success': True, 
                'data': {
                    'venta_id': venta_id, 
                    'factura': reg_resp.get('data', {}).get('factura'),
                    'transporte': tr_resp.get('data') if tr_resp.get('success') else None
                }, 
                'message': 'Venta registrada correctamente'
            }
            
        except Exception as e:
            error_msg = f'Error registrarVenta: {e}'
            print(f"[TIENDA] [{timestamp()}] {error_msg}")
            return {'success': False, 'data': None, 'message': error_msg}

    def ping(self):
        return True

    def listar_ventas(self):
        return {'success': True, 'data': self.ventas, 'message': 'Ventas listadas'}

if __name__ == '__main__':
    server = SimpleXMLRPCServer(("0.0.0.0", 9001), allow_none=True, logRequests=True)
    tienda = Tienda()
    server.register_instance(tienda)
    print(f"[TIENDA] [{timestamp()}] Servidor Tienda iniciado en 0.0.0.0:9001")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"[TIENDA] [{timestamp()}] Terminando tienda")