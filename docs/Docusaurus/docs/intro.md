---
sidebar_position: 1
---

# How to use this documentation

Keeping technical documentation up to date is crucial to ensure that it accurately reflects changes, improvements, and new features implemented in the software. This section describes the purpose of documentation, how to navigate it effectively, and the procedures to follow when the software undergoes modifications, ensuring that all users and team members have access to accurate and current information.

## Documentation structure

The documentation is divided into several main sections to ensure that all relevant areas are covered. In each section, you will find details on how to document them:

- How to use this documentation
- General information
    - Here are the .md files from the repository
- Life cycle
    - Introduction
    - Getting started
    - Project structure
    - Quality metrics and testing
    - Security
    - Architecture

## Documentation update

It is essential that documentation is kept up to date to reflect any changes in the software. The process for ensuring that information is up to date is described here:

- **Update procedure:** Whenever changes are made to the code, new features are added, or improvements are made, the documentation must be reviewed and updated. This includes updating user guides, code examples, and references to commands or configurations.

- **Responsibility for updating:** It is important to assign responsibility for updating the documentation to a team member whenever changes are made. This person will ensure that the documentation accurately reflects the current state of the software.

- **Parallel versions:** If the software has multiple active versions, the documentation must be managed in parallel to avoid confusion between versions. Each version must have its own documentation so that users can access the correct information for their implementation.

    <details>
        <summary>How to version?</summary>

        if you need to use more than one version in your code, Docosaurus is the perfect tool to quickly automate this. First, make sure you are not going to add anything else to the old version and that you want to start documenting the new version. Before you start creating the new documentation, run the following command:

        ```bash npm2yarn
        npm run docusaurus docs:version 1.1.0
        ```

        This will create a new folder within the project called **versioned_docs** where you will find a copy of the **docs** folder. You will also find a folder called **versioned_sidebars** that will reference the **sidebars** for each version, and finally a file called **versions.json** where you will find the versions you want to display.

        Finally, to enable the versions, you will need to open the Docosaurus configuration file called **docosaurus.config.js** and modify the following lines:

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
    