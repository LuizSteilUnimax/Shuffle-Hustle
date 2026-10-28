import Heading from '@theme/Heading';
import styles from './styles.module.css';

const features = [
  {
    symbol: 'A',
    suit: '♥',
    title: 'Forme combinações',
    description: 'Monte trincas e sequências para se livrar das cartas da mão.',
  },
  {
    symbol: '7',
    suit: '♦',
    title: 'Mexe na mesa',
    description: 'Use combinações comunitárias para criar novos jogos válidos.',
  },
  {
    symbol: 'K',
    suit: '♣',
    title: 'Feito para evoluir',
    description: 'A lógica das cartas é separada da interface para receber arte e sprites.',
  },
];

function Feature({symbol, suit, title, description}) {
  const cardClass = suit === '♦' ? `${styles.playingCard} ${styles.redSuit}` : styles.playingCard;
  return (
    <article className={styles.card}>
      <div className={cardClass} aria-hidden="true">
        <span>{symbol}</span>
        <span>{suit}</span>
      </div>
      <div>
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </article>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className={styles.cardGrid}>
          {features.map((feature) => <Feature key={feature.title} {...feature} />)}
        </div>
      </div>
    </section>
  );
}
