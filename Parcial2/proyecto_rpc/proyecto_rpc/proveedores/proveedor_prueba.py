import xmlrpc.client
import time

def main():
    print("=== CLIENTE PROVEEDOR DE PRUEBA ===\n")
    
    # Esperar inicialización
    print("Esperando inicialización de servicios...")
    time.sleep(10)
    
    MIDDLEWARE_URL = "http://localhost:9000"
    
    try:
        middleware = xmlrpc.client.ServerProxy(MIDDLEWARE_URL, allow_none=True)
        
        print("1. Verificando conexión con middleware...")
        if middleware.ping():
            print("   ✓ Middleware respondiendo\n")
        else:
            print("   ✗ Middleware no responde")
            return

        print("2. Ejecutando requerimientos de productos...")
        resultado = middleware.rutear('atencion_proveedores', 'cargarRequerimientosProductos')
        
        if resultado.get('success'):
            requerimientos = resultado['data']
            print(f"   ✓ Requerimientos creados: {len(requerimientos)}")
            for req in requerimientos:
                print(f"   - {req['id']}: {req.get('nombre_producto', req['producto_id'])} - Cantidad: {req['cantidad_solicitada']}")
            print()
        else:
            print(f"   ✗ Error: {resultado.get('message')}\n")

        print("3. Listando requerimientos existentes...")
        req_list = middleware.rutear('atencion_proveedores', 'listarRequerimientos')
        if req_list.get('success'):
            print(f"   Total de requerimientos: {len(req_list['data'])}")
            for req in req_list['data']:
                print(f"   - {req['id']}: {req.get('producto_id')} - Estado: {req.get('estado')}")
        else:
            print("   ✗ Error listando requerimientos")

        print("\n4. Verificando movimientos contables...")
        balance = middleware.rutear('contabilidad', 'obtenerBalance')
        if balance.get('success'):
            print(f"   Balance actual: ${balance['data']}")

    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()