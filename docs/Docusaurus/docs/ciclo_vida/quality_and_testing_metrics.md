---
sidebar_position: 4
---


# Quality Metrics and Testing

Esta sección detalla cómo medimos la calidad del software, combinando métricas de calidad y pruebas. El objetivo es asegurar que el código sea de alta calidad y validar el comportamiento del sistema a través de diferentes tipos de pruebas.

---

## 1. Gestión de Código Fuente y Control de Versiones

Utilizamos Trunk Based Development como metodología de control de versiones. Este enfoque mantiene una única rama principal (trunk o main) donde los desarrolladores integran sus cambios frecuentemente. Los cambios pequeños y continuos ayudan a identificar problemas rápidamente y facilitan la integración continua.

Cada cambio en la rama principal se realiza mediante pull requests que deben ser revisados y aprobados antes de ser integrados.

---

## 2. Cobertura de Pruebas Unitarias

Nuestra libreria cuenta con pruebas unitarias rigurosas, manteniendo un mínimo del 70% de cobertura. Esta práctica garantiza la fiabilidad y mantenibilidad del código al validar que los componentes individuales funcionan como se espera.

Utilizamos herramientas de medición de cobertura integradas en nuestro pipeline de CI/CD para asegurar que se mantenga este umbral. Ningún código puede ser integrado a la rama principal si no cumple con el criterio de cobertura establecido.

---

## 3. Análisis de Código Estático y Deuda Técnica

El análisis de código estático está integrado en nuestro proceso de desarrollo para identificar problemas de calidad y seguridad antes de que el código llegue a producción. Utilizamos herramientas especializadas para este análisis que se ejecutan automáticamente en cada integración.

Gestionamos activamente la deuda técnica para mantenerla bajo control.

---