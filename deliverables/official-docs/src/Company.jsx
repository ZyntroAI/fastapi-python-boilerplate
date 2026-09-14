/**
 * Company.jsx — ZyntroAI FastAPI Boilerplate reference surface.
 *
 * Renders the official documentation bar and an image gallery where every card
 * links back to the official docs of the provider the asset came from.
 * All provider knowledge lives in ./official-docs.js — this file only renders.
 */
import React from "react";
import PropTypes from "prop-types";
import styles from "./Company.module.css";
import {
  OFFICIAL_DOCS,
  REGISTRY_VERSION,
  VERIFIED_ON,
  IMAGE_SKILL,
  analyze,
  getSourceDoc,
  getPrimaryUrl,
  isSafeUrl,
} from "./official-docs.js";

// ==============================================
// 📚 OFFICIAL DOCUMENTATION LINKS
// ==============================================
export { OFFICIAL_DOCS, IMAGE_SKILL };

export const COMPANY_CONFIG = {
  brand: {
    name: "ZyntroAI",
    tagline: "Secure FastAPI • Official Docs Linked",
    version: REGISTRY_VERSION,
    branch: "Origin",
    officialDocs: getPrimaryUrl("fastapi"),
  },
  gallery: [
    {
      id: "fastapi-core",
      src: "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
      alt: "FastAPI Architecture",
      source: "FastAPI",
    },
    {
      id: "fig-platform",
      src: "https://hellofig.app/og-image.png",
      alt: "FIG Builder Interface",
      source: "FIG",
    },
    {
      id: "dola-diagram",
      src: "https://dola.ai/og-image.png",
      alt: "Dola AI Analysis",
      source: "Dola",
    },
  ],
  security: { shaPinned: true, gpgSigned: true },
  ui: { linkOfficial: true, externalIcon: true },
};

// ==============================================
// 🏷️ SOURCE BADGE
// ==============================================
const BADGE_CLASS = {
  FIG: styles.badgeFig,
  Dola: styles.badgeDola,
  FastAPI: styles.badgeFastapi,
};

export const SourceBadge = ({ source }) => (
  <span className={`${styles.badge} ${BADGE_CLASS[source] || styles.badgeGeneric}`}>
    {source}
  </span>
);

SourceBadge.propTypes = { source: PropTypes.string.isRequired };

// ==============================================
// 📚 SUB-COMPONENT: Official Documentation Bar
// ==============================================
export const OfficialDocsBar = () => (
  <section className={styles.docsBar} aria-label="Official documentation">
    <h3>📚 Official Documentation &amp; References</h3>
    <div className={styles.docLinks}>
      {Object.entries(OFFICIAL_DOCS).map(([key, doc]) => {
        const url = getPrimaryUrl(key);
        const label = `${doc.name} — ${doc.label}`;
        // A registry entry without a live URL renders as plain text, never a dead link.
        return url && isSafeUrl(url) ? (
          <a
            key={key}
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.docLink}
            title={label}
          >
            <span className={styles.docName}>{doc.name}</span>
            <span className={styles.docLabel}>{doc.label}</span>
            <span className={styles.docHost}>{new URL(url).host}</span>
            <span className={styles.externalIcon} aria-hidden="true">
              ↗
            </span>
          </a>
        ) : (
          <span key={key} className={styles.docLink} title={label}>
            <span className={styles.docName}>{doc.name}</span>
            <span className={styles.docLabel}>{doc.label}</span>
          </span>
        );
      })}
    </div>
  </section>
);

// ==============================================
// 🖼️ IMAGE CARD — with its source's official doc
// ==============================================
export const UnifiedImageCard = ({ image }) => {
  const meta = analyze(image.src, { alt: image.alt });
  const source = image.source || meta.source;
  const doc = getSourceDoc(source);
  const docUrl = doc ? getPrimaryUrl(Object.keys(OFFICIAL_DOCS).find(
    (k) => OFFICIAL_DOCS[k] === doc
  )) : null;

  return (
    <div className={`${styles.imageCard} ${styles[source] || ""}`}>
      <div className={styles.imgWrapper}>
        <img src={image.src} alt={image.alt} loading="lazy" className={styles.mainImage} />
      </div>
      <div className={styles.imageInfo}>
        <SourceBadge source={source} />
        <h4>{image.alt}</h4>
        {doc && docUrl && isSafeUrl(docUrl) && (
          <a
            href={docUrl}
            target="_blank"
            rel="noopener noreferrer"
            className={styles.sourceLink}
          >
            📖 Official Reference: {doc.name} ↗
          </a>
        )}
      </div>
    </div>
  );
};

UnifiedImageCard.propTypes = {
  image: PropTypes.shape({
    id: PropTypes.string,
    src: PropTypes.string.isRequired,
    alt: PropTypes.string,
    source: PropTypes.string,
  }).isRequired,
};

// ==============================================
// 🚀 MAIN
// ==============================================
const Company = () => (
  <div className={styles.wrapper}>
    <header className={styles.header}>
      <h1>ZyntroAI FastAPI Boilerplate</h1>
      <p>
        Official docs verified {VERIFIED_ON} • v{REGISTRY_VERSION}
      </p>
    </header>

    <OfficialDocsBar />

    <section className={styles.gallery}>
      {COMPANY_CONFIG.gallery.map((img) => (
        <UnifiedImageCard key={img.id} image={img} />
      ))}
    </section>
  </div>
);

export default Company;
