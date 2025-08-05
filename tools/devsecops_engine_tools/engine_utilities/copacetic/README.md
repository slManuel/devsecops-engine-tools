# Copacetic Integration

## Overview

Esta integración permite usar Copacetic para parchear vulnerabilidades directamente en imágenes de contenedores sin necesidad de reconstruir completamente las imágenes.

Copacetic (Copa) es una herramienta CLI que puede parchear vulnerabilidades de contenedores usando reportes de escaneo de herramientas como Trivy o Grype.

## Características

- Parcheo directo de imágenes de contenedores
- Soporte para reportes de Trivy y Grype
- Integración con registries de contenedores
- Configuración flexible mediante remote config
- Métricas y logging integrados
- Soporte para BuildKit personalizado

## Uso

### Parámetros requeridos

- `--integration copacetic`: Especifica que se usará la integración de Copacetic
- `--container_image`: Imagen de contenedor a parchear
- `--vulnerability_report`: Ruta al archivo de reporte de vulnerabilidades

### Parámetros opcionales

- `--output_image`: Nombre de la imagen patcheada (por defecto se agrega `-patched`)
- `--patch_format`: Formato del reporte (trivy, grype)
- `--token_registry`: Token para autenticación en el registry
- `--registry_url`: URL del registry de contenedores
- `--buildkit_addr`: Dirección del daemon BuildKit

### Ejemplo de uso

```bash
python runner_engine_integrations.py \
    --integration copacetic \
    --container_image nginx:1.20 \
    --vulnerability_report /path/to/trivy-report.json \
    --patch_format trivy \
    --output_image nginx:1.20-patched \
    --platform_devops local \
    --remote_config_repo my-config-repo \
    --use_secrets_manager false
```

## Configuración

### ConfigTool.json

La configuración principal se encuentra en `/copacetic/ConfigTool.json`:

```json
{
  "IGNORE_SEARCH_PATTERN": "(?i).*(?:test|demo|sample).*",
  "TARGET_BRANCHES": ["main", "master", "develop", "release"],
  "TIMEOUT": 1800,
  "SECRETS": {
    "TOKEN_REGISTRY": "copacetic-registry-token"
  },
  "DEFAULT_OUTPUT_SUFFIX": "-patched",
  "SUPPORTED_FORMATS": ["trivy", "grype"],
  "REGISTRY_CONFIG": {
    "REGISTRY_URL": "registry.hub.docker.com",
    "AUTH_REQUIRED": true
  },
  "BUILDKIT_CONFIG": {
    "DEFAULT_ADDR": "docker-container://buildkit",
    "TIMEOUT": 600
  },
  "PATCH_CONFIG": {
    "CREATE_SBOM": true,
    "VERIFY_PATCHES": true,
    "CLEAN_TEMP_FILES": true
  }
}
```

### Exclusions.json

Pipelines excluidos en `/copacetic/Exclusions.json`:

```json
{
  "test-pipeline": "Pipeline for testing purposes only",
  "demo-application": "Demo application - not for production",
  "BY_PATTERN_SEARCH": {
    ".*-test$": "Test pipelines pattern",
    "^temp-.*": "Temporary pipelines pattern",
    ".*-poc$": "Proof of concept pipelines"
  }
}
```

### Engine Core Config

Habilitar Copacetic en `/engine_core/ConfigTool.json`:

```json
{
  "COPACETIC": {
    "ENABLED": true
  }
}
```

## Requisitos

- Copacetic (Copa) instalado en el sistema
- Docker o Podman para manejar imágenes
- BuildKit (opcional, para funcionalidades avanzadas)
- Acceso al registry de contenedores (si es necesario)

## Instalación de Copacetic

```bash
# Descargar e instalar Copa
curl -sSfL https://raw.githubusercontent.com/project-copacetic/copacetic/main/install.sh | sh -s -- -b /usr/local/bin

# Verificar instalación
copa --version
```

## Arquitectura

La integración sigue la arquitectura hexagonal del proyecto:

```
copacetic/
├── src/
│   ├── applications/
│   │   └── runner_copacetic.py
│   ├── domain/
│   │   └── usecases/
│   │       └── copacetic.py
│   └── infrastructure/
│       ├── entry_points/
│       │   └── entry_point_copacetic.py
│       └── driven_adapters/
│           └── copacetic/
│               └── copacetic_adapter.py
└── test/
    └── test_copacetic_adapter.py
```

## Flujo de Ejecución

1. **Validación**: Se validan los parámetros de entrada y configuración
2. **Autenticación**: Se obtienen tokens desde Secrets Manager si es necesario
3. **Preparación**: Se prepara el comando Copa con los parámetros apropiados
4. **Ejecución**: Se ejecuta Copa para parchear la imagen
5. **Procesamiento**: Se procesa la salida y se generan métricas
6. **Reporte**: Se envía el resultado al sistema de métricas si está habilitado

## Métricas

La integración genera métricas que incluyen:

- Módulo: `copacetic`
- Imagen original
- Imagen patcheada
- Número de vulnerabilidades patcheadas
- Detalles del proceso de parcheo

## Troubleshooting

### Copa no encontrado

Si Copa no se encuentra en el PATH, asegúrate de que esté instalado correctamente:

```bash
which copa
copa --version
```

### Errores de autenticación

Verifica que los tokens de registry estén configurados correctamente en Secrets Manager o como parámetros.

### Timeouts

Ajusta el valor de `TIMEOUT` en la configuración si el proceso toma mucho tiempo.

### BuildKit

Si tienes problemas con BuildKit, puedes especificar una dirección personalizada con `--buildkit_addr`.
