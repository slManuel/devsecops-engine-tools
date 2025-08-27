// @ts-check
// `@type` JSDoc annotations allow editor autocompletion and type checking
// (when paired with `@ts-check`).
// There are various equivalent ways to declare your Docusaurus config.
// See: https://docusaurus.io/docs/api/docusaurus-config

import { themes as prismThemes } from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'DevSecOps Engine Tools',
  tagline: 'Toolchain for the evaluation of different devsecops practices',
  favicon: 'img/bancolombia.ico',
  markdown: {
    mermaid: true, // Habilita el soporte para Mermaid
  },
  themes: ["@docusaurus/theme-mermaid"],
  // Set the production url of your site here
  url: 'https://bancolombia.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/devsecops-engine-tools/Docusaurus/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'bancolombia', // Usually your GitHub org/user name.
  projectName: 'devsecops-engine-tools', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          editUrl:
            'https://github.com/bancolombia/devsecops-engine-tools/tree/feature/docusaurus/docs/Docusaurus',
          
            // Agrega el wrapper para proteger la documentación
            docItemComponent: process.env.APP_ENV === 'pdn' ? require.resolve('./src/docsWrapper.js') : undefined,
          },
          theme: {
            customCss: './src/css/custom.css',
          },
          }),
        ],
        ],

    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    themeConfig:
    ({
      image: 'img/docusaurus-social-card.jpg',
      navbar: {
        title: 'DevSecOps Engine Tools',
        logo: {
          alt: 'DevSecOps Engine Tools',
          src: 'img/logo.png',
        },
        items: [

          {
            type: 'search',
            position: 'right',
          },
          {
            href: 'https://github.com/bancolombia/devsecops-engine-tools',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
      colorMode: {
        disableSwitch: true
      },
    }),
};

export default config;
