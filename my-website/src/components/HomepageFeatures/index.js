import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Arquitetura Organizada',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        O projeto segue a estrutura proposta na disciplina,
        separando <code>entidades</code>, <code>mundo</code>,
        <code>regras</code> e <code>ui</code> para facilitar a manutenção.
      </>
    ),
  },
  {
    title: 'Regras do Mexe-Mexe',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        Implementação das regras de trincas, sequências 
        e validação das jogadas conforme o jogo
        tradicional Mexe-Mexe.
      </>
    ),
  },
  {
    title: 'Python + Pygame',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        Desenvolvido utilizando Python e Pygame, com foco
        em programação orientada a objetos e boas práticas
        de desenvolvimento de jogos.
      </>
    ),
  },
];

function Feature({ Svg, title, description }) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>

      <div className="text--center padding-horiz--md">
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}