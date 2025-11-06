import xmlrpc.client
import time

def main():
    print("=== INICIANDO PROVEEDOR DE PRUEBA ===\n")
    time.sleep(5)  # Esperar servicios
    middleware = xmlrpc.client.ServerProxy('http://localhost:9000', allow_none=True)

    print("1. Verificando conexión con middleware...")
    try:
        if middleware.ping():
            print("   ✓ Middleware respondiendo\n")
    except Exception as e:
        print("   ✗ No se pudo conectar al middleware:", e)
        return

    print("2. Proveedor verificando requerimientos de productos...")
    resultado = middleware.rutear('atencion_proveedores', 'cargarRequerimientosProductos')

    if resultado.get('success'):
        print("   Requerimientos generados:")
        for req in resultado['data']:
            print(f"   - Producto: {req['producto_id']}, Cantidad: {req['cantidad_solicitada']}")
        print("")
    else:
        print(f"   ✗ Error: {resultado.get('message')}\n")

if __name__ == '__main__':
    main()
