# Sistema Distribuido de Gestión Comercial con RPC y Docker

## Descripción
Sistema distribuido simple usando RPC (xmlrpc) y Docker. Cada nodo corre en su propio contenedor y la comunicación entre nodos se realiza exclusivamente a través del **Middleware**.

Nodos:
- middleware (9000)
- tienda (9001)
- inventario (9002)
- compras_ventas (9003)
- contabilidad (9004)
- transportador (9005)
- atencion_proveedores (9006)

## Prerrequisitos
- Docker
- Docker Compose
- Python 3.9+ (para ejecutar scripts de prueba localmente)

## Instalación y ejecución
Desde la carpeta raíz del proyecto (`proyecto_rpc/`):

```bash
# Levantar sistema
docker-compose up --build

# En otra terminal, ejecutar pruebas (esperar ~5-10 s después del up)
python3 clientes/cliente_prueba.py
python3 proveedores/proveedor_prueba.py

# Detener sistema
docker-compose down
    