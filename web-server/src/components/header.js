import * as React from "react"
import { Link } from "gatsby"
import { StaticImage } from "gatsby-plugin-image"

const Header = ({ siteTitle }) => (
  <header
    style={{
      margin: `0 auto`,
      padding: `var(--space-4) var(--size-gutter)`,
      display: `flex`,
      alignItems: `center`,
      justifyContent: `space-between`,
    }}
  >
    <Link
      to="/"
      style={{
        fontSize: `var(--font-lg)`,
        textDecoration: `none`,
      }}
    >
      <StaticImage
        src="../images/product_logo.png"
        placeholder="product logo"
        loading="eager"
        height={30}
        quality={95}
        formats={["auto", "webp", "avif"]}
        alt=""
        style={{ margin: 0 }}
      />
      <b style={{ verticalAlign: "bottom" }}>
        {siteTitle}
      </b>
    </Link>
    <StaticImage
      src="../images/team_logo.png"
      placeholder="team logo"
      loading="eager"
      height={30}
      quality={95}
      formats={["auto", "webp", "avif"]}
      alt=""
      style={{ margin: 0 }}
    />
  </header>
)

export default Header
