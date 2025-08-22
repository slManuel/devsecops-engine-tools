---
sidebar_position: 1
---

# Introducción

## DevSecOps Engine Tools

**DevSecOps Engine Tools** es una plataforma integral que automatiza, centraliza y facilita la gestión de seguridad, cumplimiento y calidad en el ciclo de vida del desarrollo de software. El ecosistema está compuesto por modulos y utilidades que permiten a los equipos de desarrollo, seguridad y operaciones:

- Orquestar y automatizar escaneos de seguridad (SAST, SCA, DAST, IaC) sobre código, contenedores, artefactos y entornos.
- Generar y gestionar SBOMs (Software Bill of Materials) para trazabilidad y cumplimiento normativo.
- Integrar y consolidar resultados de diferentes motores de análisis, generando reportes unificados y accionables.
- Facilitar la integración con pipelines CI/CD y repositorios de artefactos.
- Proveer métricas, alertas y tableros para la toma de decisiones y mejora continua.

### Que hace

#### Componentes principales:

- **Ingesta de vulnerabilidades:** Recibe información desde múltiples fuentes externas, como webhooks de proveedores de hacking continuo, escáneres de contenedores, plataformas de seguridad en la nube (Prisma, Tenable, etc.) y resultados de análisis SAST/SCA/DAST/IaC.
- **Procesamiento y normalización:** Estandariza y transforma los datos recibidos mediante flujos batch y streaming, asegurando la consistencia y calidad de la información.
- **Orquestador de flujos:** Coordina la ejecución de tareas, la integración con otros sistemas y la gestión de eventos para mantener actualizada la información de vulnerabilidades y cumplimiento.
- **Integración con ASPM:** Envía los resultados procesados a una plataforma centralizadora de gestión de vulnerabilidades y cumplimiento, y sincroniza los estados con las bases de datos de los proveedores.
- **Gestión de SBOM y artefactos:** Permite la generación, almacenamiento y consulta de SBOMs, facilitando la trazabilidad de componentes y dependencias en los artefactos analizados.


### ¿Qué problema resuelve?

DevSecOps Engine Tools resuelve el desafío de la fragmentación y dispersión de la información de seguridad, centralizando y normalizando datos de vulnerabilidades y cumplimiento provenientes de diversas fuentes. Gracias a su arquitectura reactiva y procesamiento eficiente, permite:

- Unificar la gestión de vulnerabilidades y cumplimiento
- Automatizar el flujo de información entre sistemas externos y la plataforma centralizada
- Proporcionar datos procesados y listos para su análisis, remediación y auditoría

Esta documentación está dirigida a desarrolladores, ingenieros de seguridad y administradores de sistemas que necesiten comprender, mantener o extender la funcionalidad de DevSecOps Engine Tools.