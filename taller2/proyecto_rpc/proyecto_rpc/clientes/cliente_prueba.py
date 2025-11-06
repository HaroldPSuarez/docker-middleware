import xmlrpc.client
import time
import sys

def main():
    print("=== CLIENTE DE PRUEBA MEJORADO ===\n")
    
    # Dar más tiempo a que los servicios se inicialicen
    print("Esperando inicialización de servicios (15 segundos)...")
    time.sleep(15)
    
    MIDDLEWARE_URL = "http://localhost:9000"
    
    try:
        middleware = xmlrpc.client.ServerProxy(MIDDLEWARE_URL, allow_none=True)
        
        print("1. Verificando salud del sistema...")
        health = middleware.health_check()
        print("   Estado de servicios:")
        for servicio, estado in health.items():
            status = "✅ Activo" if estado else "❌ Inactivo"
            print(f"   - {servicio}: {status}")
        print()
        
        if not all(health.values()):
            print("⚠️  Algunos servicios no están respondiendo. Continuando de todos modos...\n")
        
        print("2. Realizando compra de prueba...")
        cliente_id = "CLI001"
        productos = [
            {'producto_id': 'P001', 'cantidad': 1},  # Solo 1 laptop para prueba
            {'producto_id': 'P002', 'cantidad': 2}   # 2 mouses
        ]
        destino = "Calle 123, Bogotá"
        
        print(f"   Cliente: {cliente_id}")
        print(f"   Productos: {productos}")
        print(f"   Destino: {destino}")
        print("   Enviando solicitud...")
        
        resultado = middleware.rutear('tienda', 'registrarVenta', cliente_id, productos, destino)
        
        if resultado.get('success'):
            data = resultado['data']
            print(f"   ✅ Venta exitosa!")
            print(f"   - ID Venta: {data.get('venta_id')}")
            print(f"   - Factura: {data.get('factura', {}).get('numero', 'N/A')}")
            print(f"   - Total: ${data.get('factura', {}).get('total', 'N/A')}")
            if data.get('transporte'):
                print(f"   - Transporte: {data.get('transporte', {}).get('id', 'N/A')}")
            print()
        else:
            print(f"   ❌ Error en venta: {resultado.get('message')}\n")
        
        # Las otras consultas...
        print("3. Verificando inventario actualizado...")
        inventario = middleware.rutear('inventario', 'cargarProductos')
        if inventario.get('success'):
            print("   Inventario actual:")
            for p in inventario['data']:
                print(f"   - {p['nombre']}: {p['cantidad']} unidades")
            print()
        
        print("4. Consultando balance contable...")
        balance = middleware.rutear('contabilidad', 'obtenerBalance')
        if balance.get('success'):
            print(f"   Balance actual: ${balance['data']}\n")
        
        print("5. Listando ventas registradas...")
        ventas = middleware.rutear('tienda', 'listar_ventas')
        if ventas.get('success'):
            print(f"   Ventas totales: {len(ventas['data'])}")
            for v in ventas['data']:
                print(f"   - Venta {v['id']}: ${v['total']} para cliente {v['cliente_id']}")
        
    except Exception as e:
        print(f"❌ Error general del cliente: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()