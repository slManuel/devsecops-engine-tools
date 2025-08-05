# Integración de Copacetic - Resumen de Cambios

## Archivos Modificados

### 1. runner_engine_integrations.py
**Ubicación**: `/tools/devsecops_engine_tools/engine_utilities/engine_integrations/src/applications/runner_engine_integrations.py`

**Cambios realizados**:
- Agregado "copacetic" a las opciones del argumento `--integration`
- Añadidas nuevas flags específicas para Copacetic:
  - `--container_image`: Imagen de contenedor a parchear
  - `--vulnerability_report`: Ruta al reporte de vulnerabilidades
  - `--token_registry`: Token para autenticación en registry
  - `--registry_url`: URL del registry de contenedores
  - `--output_image`: Nombre de la imagen patcheada
  - `--patch_format`: Formato del reporte (trivy/grype)
  - `--buildkit_addr`: Dirección del daemon BuildKit
- Actualizado el diccionario de retorno para incluir los nuevos parámetros

### 2. handle_integrations.py
**Ubicación**: `/tools/devsecops_engine_tools/engine_utilities/engine_integrations/src/domain/usecases/handle_integrations.py`

**Cambios realizados**:
- Importado el runner de Copacetic
- Agregada lógica para manejar la integración "copacetic"

### 3. ConfigTool.json (Engine Core)
**Ubicación**: `/example_remote_config_local/engine_core/ConfigTool.json`

**Cambios realizados**:
- Agregada sección "COPACETIC" con `"ENABLED": true`

## Archivos Creados

### Estructura de Directorios
```
tools/devsecops_engine_tools/engine_utilities/copacetic/
├── __init__.py
├── README.md
├── example_usage.sh
├── src/
│   ├── __init__.py
│   ├── applications/
│   │   ├── __init__.py
│   │   └── runner_copacetic.py
│   ├── domain/
│   │   ├── __init__.py
│   │   └── usecases/
│   │       ├── __init__.py
│   │       └── copacetic.py
│   └── infrastructure/
│       ├── __init__.py
│       ├── entry_points/
│       │   ├── __init__.py
│       │   └── entry_point_copacetic.py
│       └── driven_adapters/
│           ├── __init__.py
│           └── copacetic/
│               ├── __init__.py
│               └── copacetic_adapter.py
└── test/
    ├── __init__.py
    └── test_copacetic_adapter.py
```

### Archivos de Configuración
```
example_remote_config_local/copacetic/
├── ConfigTool.json
└── Exclusions.json
```

## Funcionalidades Implementadas

### 1. CopaceticAdapter
- Encuentra automáticamente el binario de Copa en el sistema
- Ejecuta comandos de parcheo con parámetros configurables
- Maneja autenticación de registries
- Parsea salida de Copa para extraer métricas
- Gestión de timeouts y errores
- Verificación de disponibilidad de Copa

### 2. Copacetic UseCase
- Validación de parámetros requeridos
- Integración con Secrets Manager
- Procesamiento de configuración remota
- Generación de reportes de parcheo
- Manejo de errores y logging

### 3. Entry Point
- Validación de pipelines y branches
- Integración con sistema de métricas
- Manejo de exclusiones
- Control de habilitación/deshabilitación

### 4. Runner Principal
- Orquestación de todos los componentes
- Manejo de excepciones a nivel global
- Integración con gateways existentes

## Parámetros de Configuración

### Flags de Línea de Comandos
- `--integration copacetic`: Activa la integración de Copacetic
- `--container_image`: Imagen a parchear (requerido)
- `--vulnerability_report`: Archivo de reporte (requerido)
- `--output_image`: Imagen de salida (opcional)
- `--patch_format`: Formato del reporte - trivy/grype (opcional, default: trivy)
- `--token_registry`: Token de registry (opcional)
- `--registry_url`: URL del registry (opcional)
- `--buildkit_addr`: Dirección de BuildKit (opcional)

### Configuración Remota
- **TARGET_BRANCHES**: Branches donde ejecutar Copacetic
- **TIMEOUT**: Timeout para operaciones de parcheo
- **SECRETS**: Configuración de tokens en Secrets Manager
- **REGISTRY_CONFIG**: Configuración de registries
- **BUILDKIT_CONFIG**: Configuración de BuildKit
- **PATCH_CONFIG**: Configuración específica de parcheo

## Tests Implementados
- Test de disponibilidad de Copa
- Test de obtención de versión
- Test de parcheo exitoso
- Test de parcheo fallido
- Test de parseo de salida
- Test de búsqueda de binario

## Compatibilidad
La integración sigue la misma arquitectura que las integraciones existentes:
- Misma estructura de directorios
- Mismo patrón de gateways
- Misma integración con métricas
- Mismo sistema de configuración remota
- Mismo manejo de secrets

## Próximos Pasos
1. Instalar Copacetic en el ambiente de ejecución
2. Configurar los archivos de remote config específicos del proyecto
3. Configurar tokens de registry en Secrets Manager si es necesario
4. Probar la integración con imágenes reales y reportes de vulnerabilidades
5. Ajustar timeouts y configuraciones según las necesidades del proyecto
