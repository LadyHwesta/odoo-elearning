# Odoo eLearning

Reusable Odoo 19 **eLearning** training packs - pure-data modules that
each drop one ready-built course into Odoo's own eLearning app
(`website_slides`), for stock Odoo apps rather than one specific
organization's custom modules. If you're looking for training on a
custom suite instead, see
[`nonprofit-addons`](https://github.com/LadyHwesta/nonprofit-addons),
[`odoo-addons`](https://github.com/LadyHwesta/odoo-addons) (amateur radio
club), or [`paramedic-tattoo-addons`](https://github.com/LadyHwesta/paramedic-tattoo-addons) -
each has its own eLearning packs for what it builds.

## Modules

- [`elearning_website/`](elearning_website/) - *Building Your
  Organization's Website*, for a non-technical person configuring their
  org's public site: pages, blocks, menus, publishing, and the handful of
  settings worth knowing (name, favicon, company info) without wading
  into the more technical ones (SEO consoles, analytics keys, robots.txt).

## Why a separate repo

Each of these depends only on stock Odoo apps (`website_slides` plus
whatever app it documents) - no custom module, no one organization. That
makes them installable by *any* Odoo 19 CE instance, not just the ones
this account already builds for, so they get their own home rather than
being bolted onto an org-specific suite.

## Conventions

Same shape as the eLearning packs in the other repos: one course per
module, pure data (`data/slide_channel_data.xml`, `noupdate="1"`), gated
(`visibility="members"`, `enroll="invite"`) with the closest-fit stock
Odoo security group auto-enrolled via `enroll_group_ids`, ending in a
4-question quiz. See any module's own README for specifics.

**Gotcha worth knowing before adding a lesson**: a `slide.slide`'s
`html_content` field (`type="html"`) needs real inline XML elements as
its children, not a `<![CDATA[...]]>` block - Odoo's data-loader schema
requires element content there, and a CDATA section is a single text
node. Write the markup as literal XML (`<p>`, `<strong>`, etc.) and use
real Unicode characters instead of HTML named entities like `&hellip;` -
only `&amp; &lt; &gt; &apos; &quot;` are defined in plain XML.

## Testing

[`testing/`](testing/) is a self-contained local Odoo 19 + Postgres
instance - see [`testing/README.md`](testing/README.md).

## Compatibility

Targets **Odoo 19.0**, tracked on `main` (mirrored to a `19.0` branch).

## License

LGPL-3 (see [`LICENSE`](LICENSE)).
