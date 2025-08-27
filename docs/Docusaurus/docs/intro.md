---
sidebar_position: 1
---

# How to use this documentation

Mantener la documentación técnica al día es crucial para asegurar que refleje con precisión los cambios, mejoras y nuevas funcionalidades que se implementan en el software. Esta sección describe el propósito de la documentación, cómo navegarla eficazmente y los procedimientos a seguir cuando el software sufre modificaciones, garantizando que todos los usuarios y miembros del equipo tengan acceso a la información correcta y vigente.

## Estructura de la documentación

La documentación está dividida en varias secciones principales para asegurar que se cubran todas las áreas relevantes, en cada una de ellas podra encontrar el detalle de como documentarlas:

- Como usar esta documentación
- Generalidades
    - Aqui van los archivos .md del repositorio
- Ciclo de Vida
    - Introducción
    - Primeros pasos
    - Estructura del proyecto
    - Seguridad
    - DevOps
    - Métricas de calidad y pruebas
    - Arquitectura Cloud
    - Artefactos

## Actualización de la documentación

Es esencial que la documentación se mantenga actualizada para reflejar cualquier cambio en el software. Aquí se describe el proceso para garantizar que la información esté al día:

- **Procedimiento de actualización:** Cada vez que se realicen cambios en el código, nuevas características, o mejoras, la documentación debe ser revisada y actualizada. Esto incluye actualizar las guías de usuario, ejemplos de código, y referencias a comandos o configuraciones.

- **Responsabilidad de actualización:** Es importante que se asigne la responsabilidad de actualizar la documentación a un miembro del equipo cada vez que se realicen cambios. Este responsable se asegurará de que la documentación refleje con precisión el estado actual del software.

- **Versiones paralelas:** Si el software tiene múltiples versiones activas, la documentación debe manejarse en paralelo para evitar confusión entre versiones. Cada versión debe tener su propia documentación para que los usuarios accedan a la información correcta según su implementación.

    <details>
        <summary>¿Como hacer el versionamiento?</summary>

        Si requiere usar más de una versión en su código, Docosaurus es la herramienta perfecta para automatizar rápidamente esto. Primero asegúrese que no va a agregar nada más a la versión vieja y quiere empezar a hacer la documentación de la nueva versión, antes de empezar a hacer la nueva documentación ejecute el siguiente comando:

        ```bash npm2yarn
        npm run docusaurus docs:version 1.1.0
        ```

        Esto generara una nueva carpeta dentro del proyecto llamada **versioned_docs** donde encontrara una copia de la carpeta **docs**, también encontrara una carpeta **versioned_sidebars** que harán referencias a las **sidebars** de cada versión y por último un archivo llamado **versions.json** donde encontrara las versiones que quiere mostrar.

        Finalmente, para habilitar las versiones tendrá que entrar dentro del archivo de configuración de Docosaurus llamado **docosaurus.config.js** y modificar las siguientes líneas:

        ```js title="docosaurus.config.js"
        const config = {
            // ...
            presets: [
                [
                "classic",
                /** @type {import('@docusaurus/preset-classic').Options} */
                ({
                    docs: {
                        lastVersion: 'current',
                        versions: {
                            current: {
                                label: 'current',
                            },
                            '1.1.0': {
                                label: '1.1.0',
                                banner: 'unmaintained',
                            },
                            '1.2.0': {
                                label: '1.2.0',
                                banner: 'unreleased',
                            },
                        },
                    }
                    // ...
                })
                ]
            ]
        }       

        ```

    </details>
    