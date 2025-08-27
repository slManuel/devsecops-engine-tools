---
sidebar_position: 4
---

# Security

En esta sección detallamos las diferentes tácticas de seguridad que utilizamos en el proyecto, abarcando desde el manejo de secretos hasta la protección frente a ataques. Nuestro objetivo es garantizar que toda la infraestructura, datos y procesos del proyecto estén protegidos de amenazas externas e internas, cumpliendo con las mejores prácticas de seguridad.

## 1. Manejo de Secretos y Variables de Seguridad

Los secretos y variables de seguridad son administrados de manera centralizada a través de servicios dedicados para evitar su exposición en el código o archivos de configuración:

- **AWS Secrets Manager**: Utilizamos este servicio para almacenar y rotar secretos automáticamente.

- **GitHub Secrets**: Las variables de entorno y secretos necesarios en la integración continua se almacenan como GitHub Secrets.

## 2. Encriptación

Implementamos encriptación en múltiples niveles para proteger la información:

- **Encriptación en tránsito**: Todas las comunicaciones entre los servicios utilizan TLS 1.3 para garantizar la confidencialidad.

- **Encriptación en reposo**: Los datos almacenados en bases de datos, buckets S3, y otros servicios de almacenamiento están encriptados mediante AWS KMS

## 3. Monitoreo y Auditoría de Seguridad

Mantenemos vigilancia constante sobre nuestra infraestructura:

- **Logging centralizado**: Todos los eventos de seguridad se registran y almacenan de forma centralizada.

- **Alertas automáticas**: Configuración de notificaciones para actividades sospechosas.

- **Escaneo continuo**: Análisis regular de vulnerabilidades y configuraciones inseguras.

