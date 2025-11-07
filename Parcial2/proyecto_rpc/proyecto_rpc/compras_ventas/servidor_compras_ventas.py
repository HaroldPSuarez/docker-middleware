from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client
from datetime import datetime
import socket
import time

socket.setdefaulttimeout(30)

def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class ComprasVentas:
    def __init__(self):
        self.ventas = []
        self.compras = []
        self.facturas = []
        self.counter = 1
        
        # URLs directas
        self.inventario_url = 'http://inventario:9002'
        self.contabilidad_url = 'http://contabilidad:9004'
        
        print(f"[COMPRAS_VENTAS] [{timestamp()}] Inicializando...")

    def _llamar_servicio(self, url, metodo, *args):
        """Llama directamente a un servicio"""
        try:
            proxy = xmlrpc.client.ServerProxy(url, allow_none=True)
            fn = getattr(proxy, metodo)
            return fn(*args)
        except Exception as e:
            print(f"[COMPRAS_VENTAS] [{timestamp()}] Error llamando {url}.{metodo}: {e}")
            return {'success': False, 'message': str(e)}

    def registrarCompra(self, datos_venta):
        try:
            print(f"[COMPRAS_VENTAS] [{timestamp()}] Registrando compra: {datos_venta.get('id')}")
            
            # Actualizar inventario directo
            productos_a_actualizar = []
            for producto in datos_venta.get('productos', []):
                productos_a_actualizar.append({
                    'producto_id': producto['producto_id'],
                    'cantidad': producto['cantidad']
                })
            
            print(f"[COMPRAS_VENTAS] [{timestamp()}] Actualizando inventario...")
            inv_resp = self._llamar_servicio(self.inventario_url, 'actualizarInventario', productos_a_actualizar)
            
            if not inv_resp.get('success'):
                return {'success': False, 'message': f'Error inventario: {inv_resp.get("message")}'}
            
            # Generar factura directo
            print(f"[COMPRAS_VENTAS] [{timestamp()}] Generando factura...")
            fact_resp = self._llamar_servicio(self.contabilidad_url, 'generarFactura', datos_venta)
            
            if not fact_resp.get('success'):
                return {'success': False, 'message': f'Error contabilidad: {fact_resp.get("message")}'}
            
            # Guardar localmente
            self.ventas.append(datos_venta)
            self.facturas.append(fact_resp.get('data'))
            
            print(f"[COMPRAS_VENTAS] [{timestamp()}] Compra {datos_venta.get('id')} registrada")
            
            return {
                'success': True, 
                'data': {
                    'venta_id': datos_venta.get('id'),
                    'factura': fact_resp.get('data')
                }, 
                'message': 'Compra registrada correctamente'
            }
            
        except Exception as e:
            error_msg = f'Error registrarCompra: {e}'
            print(f"[COMPRAS_VENTAS] [{timestamp()}] {error_msg}")
            return {'success': False, 'message': error_msg}

    def registrarPedido(self, pedido):
        try:
            print(f"[COMPRAS_VENTAS] [{timestamp()}] Registrando pedido: {pedido.get('id')}")
            
            # Guardar pedido localmente
            self.compras.append(pedido)
            
            # Registrar movimiento contable (egreso)
            cont_resp = self._llamar_servicio(self.contabilidad_url, 'registrarMovimiento', 
                                             'egreso', 
                                             f"Pedido {pedido.get('id')} - {pedido.get('nombre_producto', 'Producto')}", 
                                             500.0)  # Costo estimado
            
            print(f"[COMPRAS_VENTAS] [{timestamp()}] ✅ Pedido {pedido.get('id')} registrado")
            
            return {
                'success': True, 
                'data': pedido, 
                'message': 'Pedido registrado correctamente'
            }
            
        except Exception as e:
            error_msg = f'Error en registrarPedido: {e}'
            print(f"[COMPRAS_VENTAS] [{timestamp()}] ❌ {error_msg}")
            return {'success': False, 'message': error_msg}

    def ping(self):
        return True

if __name__ == '__main__':
    server = SimpleXMLRPCServer(("0.0.0.0", 9003), allow_none=True, logRequests=True)
    svc = ComprasVentas()
    server.register_instance(svc)
    print(f"[COMPRAS_VENTAS] [{timestamp()}] Servidor Compras/Ventas iniciado en 0.0.0.0:9003")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"[COMPRAS_VENTAS] [{timestamp()}] Terminando compras_ventas")