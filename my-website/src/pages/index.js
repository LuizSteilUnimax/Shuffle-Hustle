import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import HomepageFeatures from '@site/src/components/HomepageFeatures';

import Heading from '@theme/Heading';
import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  const deckImage = useBaseUrl('/img/baralho-copag.webp');
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <div className={styles.heroContent}>
          <div>
            <p className={styles.eyebrow}>Cartas na mesa. Estratégia na mão.</p>
            <Heading as="h1" className="hero__title">
              {siteConfig.title}
            </Heading>
            <p className="hero__subtitle">{siteConfig.tagline}</p>
            <div className={styles.buttons}>
              <Link className="button button--secondary button--lg" to="/docs/regras">
                Conheça as regras
              </Link>
              <Link className={styles.secondaryLink} to="/docs/intro">
                Sobre o projeto
              </Link>
            </div>
          </div>
          <img className={styles.deckImage} src={deckImage} alt="Dois baralhos de cartas" />
        </div>
      </div>
    </header>
  );
}

export default function Home() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={siteConfig.title}
      description="Conheça o jogo de cartas Mexe-Mexe, suas regras e sua implementação em Python e Pygame.">
      <HomepageHeader />
      <main>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
