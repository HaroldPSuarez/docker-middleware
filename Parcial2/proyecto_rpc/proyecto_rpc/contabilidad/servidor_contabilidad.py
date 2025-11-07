from xmlrpc.server import SimpleXMLRPCServer
from datetime import datetime
import socket

socket.setdefaulttimeout(5)
def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class Contabilidad:
    def __init__(self):
        self.movimientos = []
        self.facturas = []
        self.counter_mov = 1
        self.counter_fact = 1
        # Registrar nodo en middleware
        try:
            import xmlrpc.client
            mw = xmlrpc.client.ServerProxy('http://middleware:9000', allow_none=True)
            mw.registrar_nodo('contabilidad', 'http://contabilidad:9004')
            print(f"[CONTABILIDAD] [{timestamp()}] Registrado en middleware")
        except Exception as e:
            print(f"[CONTABILIDAD] [{timestamp()}] Error registrando en middleware: {e}")

    def _next_mov_id(self):
        mid = f"MOV{self.counter_mov:03d}"
        self.counter_mov += 1
        return mid

    def _next_fact_num(self):
        num = f"F{self.counter_fact:03d}"
        self.counter_fact += 1
        return num

    def registrarMovimiento(self, tipo, concepto, monto):
        try:
            mov = {
                'id': self._next_mov_id(),
                'tipo': tipo,
                'concepto': concepto,
                'monto': monto,
                'fecha': datetime.now().strftime("%Y-%m-%d")
            }
            self.movimientos.append(mov)
            print(f"[CONTABILIDAD] [{timestamp()}] Movimiento registrado {mov['id']}")
            return {'success': True, 'data': mov, 'message': 'Movimiento registrado'}
        except Exception as e:
            return {'success': False, 'data': None, 'message': f'Error registrarMovimiento: {e}'}

    def generarFactura(self, venta):
        try:
            numero = self._next_fact_num()
            subtotal = float(venta.get('total', 0.0))
            iva = round(subtotal * 0.19, 2)
            total = round(subtotal + iva, 2)
            factura = {
                'numero': numero,
                'fecha': datetime.now().strftime("%Y-%m-%d"),
                'cliente_id': venta.get('cliente_id'),
                'venta_id': venta.get('id'),
                'subtotal': subtotal,
                'iva': iva,
                'total': total
            }
            self.facturas.append(factura)
            # Registrar movimiento de ingreso
            self.registrarMovimiento('ingreso', f'Venta {numero}', total)
            print(f"[CONTABILIDAD] [{timestamp()}] Factura generada {numero}")
            return {'success': True, 'data': factura, 'message': 'Factura generada'}
        except Exception as e:
            return {'success': False, 'data': None, 'message': f'Error generarFactura: {e}'}

    def obtenerBalance(self):
        try:
            ingresos = sum(m['monto'] for m in self.movimientos if m['tipo'] == 'ingreso')
            egresos = sum(m['monto'] for m in self.movimientos if m['tipo'] == 'egreso')
            balance = round(ingresos - egresos, 2)
            return {'success': True, 'data': balance, 'message': 'Balance calculado'}
        except Exception as e:
            return {'success': False, 'data': None, 'message': f'Error obtenerBalance: {e}'}

    def ping(self):
        return True

if __name__ == '__main__':
    server = SimpleXMLRPCServer(("0.0.0.0", 9004), allow_none=True, logRequests=False)
    cont = Contabilidad()
    server.register_instance(cont)
    print(f"[CONTABILIDAD] [{timestamp()}] Servidor Contabilidad iniciado en 0.0.0.0:9004")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"[CONTABILIDAD] [{timestamp()}] Terminando contabilidad")
