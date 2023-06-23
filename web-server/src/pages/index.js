import * as React from "react"
import { StaticImage } from "gatsby-plugin-image"

import Layout from "../components/layout"
import Seo from "../components/seo"
import * as styles from "../components/index.module.css"
import { graphql, useStaticQuery } from "gatsby"

const links = [
  {
    text: "GenieSlackとは？",
    url: "/what-is",
    description:
      "GenieSlack seamlessly integrates Slack and Esa, showcasing its incredible capabilities in a single app.",
  },
  {
    text: "使い方",
    url: "/how-to-use",
    description:
      "GenieSlack, the app that integrates Slack and Esa, is incredibly user-friendly, making it super easy to use.",
  },
  {
    text: "プライバシーポリシー",
    url: "/privacy-policy",
    description:
      "Become a privacy-savvy GenieSlack expert, safeguarding your data while mastering the integration of Slack and Esa.",
  },
  {
    text: "利用規約",
    url: "/terms-of-service",
    description:
      "GenieSlack's Terms of Service, which govern the use of the app that integrates Slack and Esa, are outlined here.",
  },
  {
    text: "問い合わせ",
    url: "/contact",
    description:
      "Experience peace of mind with GenieSlack's seamless integration of Slack and Esa, backed by a dedicated inquiry form and reliable support.",
  },
]

const utmParameters = `?utm_source=starter&utm_medium=start-page&utm_campaign=default-starter`

const IndexPage = () => {
  const slackLogoImage = useStaticQuery(graphql`
    query {
      file(relativePath: { eq: "Slack-mark.svg" }) {
        publicURL
      }
    }
  `);

  console.log(slackLogoImage);

  const { publicURL } = slackLogoImage.file;

  return (
    <Layout>
      <div className={styles.textCenter}>
        <StaticImage
          src="../images/product_logo.png"
          placeholder="product logo"
          loading="eager"
          width={128}
          quality={95}
          formats={["auto", "webp", "avif"]}
          alt=""
          style={{ marginBottom: `var(--space-3)` }}
        />
        <h1 style={{ marginBottom: "0" }}>
          Welcome to <b>GenieSlack!</b>
        </h1>
        <h2 style={{fontSize: "1.17em"}}>
          情報のストックを、もっと手軽に
        </h2>
        <a href="https://genieslack.kusshi.dev/slack/install" className={styles.addToSlackBtn}>
          <div style={{display: "flex"}}>
            <img src={publicURL} width="50px" height="50px" style={{ margin: "0px"}} alt="slack-logo" />
            <div style={{lineHeight: "50px"}}>Install</div>
          </div>
        </a>
      </div>
      <ul className={styles.list}>
        {links.map(link => (
          <li key={link.url} className={styles.listItem}>
            <a
              className={styles.listItemLink}
              href={`${link.url}${utmParameters}`}
            >
              {link.text} ↗
            </a>
            <p className={styles.listItemDescription}>{link.description}</p>
          </li>
        ))}
      </ul>
    </Layout>
  )
}

/**
 * Head export to define metadata for the page
 *
 * See: https://www.gatsbyjs.com/docs/reference/built-in-components/gatsby-head/
 */
export const Head = () => <Seo title="Home" />

export default IndexPage
