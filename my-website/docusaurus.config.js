// @ts-check

import { themes as prismThemes } from "prism-react-renderer";

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: "Mexe-Mexe",
  tagline: "Um jogo de cartas feito em Python e Pygame",
  favicon: "img/baralho-copag.webp",

  future: {
    v4: true,
  },

  url: "https://mexe-mexe.local",
  baseUrl: "/",

  organizationName: "unimax",
  projectName: "mexe-mexe",

  onBrokenLinks: "throw",

  i18n: {
    defaultLocale: "pt-BR",
    locales: ["pt-BR"],
  },

  presets: [
    [
      "classic",
      {
        docs: {
          sidebarPath: "./sidebars.js",
        },

        blog: false,

        theme: {
          customCss: "./src/css/custom.css",
        },
      },
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      image: "img/baralho-copag.webp",

      colorMode: {
        defaultMode: "light",
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },

      navbar: {
        title: "Mexe-Mexe",

        logo: {
          alt: "Logo Mexe-Mexe",
          src: "img/baralho-copag.webp",
        },

        items: [
          {
            type: "docSidebar",
            sidebarId: "projectSidebar",
            position: "left",
            label: "Documentação",
          },

          {
            to: "/docs/regras",
            label: "Como jogar",
            position: "left",
          },
          {
            to: "/docs/arquitetura",
            label: "Arquitetura",
            position: "left",
          },
        ],
      },

      footer: {
        style: "dark",

        links: [
          {
            title: "Projeto",
            items: [
              {
                label: "Sobre o projeto",
                to: "/docs/intro",
              },
              {
                label: "Arquitetura",
                to: "/docs/arquitetura",
              },
            ],
          },

          {
            title: "Jogo",
            items: [
              {
                label: "Regras do Mexe-Mexe",
                to: "/docs/regras",
              },
              {
                label: "Entidades",
                to: "/docs/entidades",
              },
            ],
          },

          {
            title: "Código",
            items: [
              { label: "Próximas etapas", to: "/docs/roadmap" },
            ],
          },
        ],

        copyright: `© ${new Date().getFullYear()} Projeto Mexe-Mexe - UniMAX / UniFAJ`,
      },

      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;