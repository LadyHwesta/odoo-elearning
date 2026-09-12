# eLearning: Building Your Organization's Website

A pure-data module: installing it drops a ready-built course,
*"Building Your Organization's Website"*, into Odoo's **eLearning** app
- nothing to author by hand.

## Who this is for

A non-technical person - an office admin, an ED, a volunteer coordinator
- who's been asked to keep their organization's public website up to
date, with no coding or design background assumed.

## What's in the course

Four sections: getting oriented (opening the editor, finding your way
around the Site menu), building pages (adding a new page, working with
blocks, editing text/images/colors), menus and publishing (the Menu
Editor, the Published/Unpublished toggle), and the settings worth knowing
early on (name, favicon, company info, and a plain-language word on SEO
that deliberately leaves the more technical settings - Google Search
Console, robots.txt - for later). A 4-question quiz at the end.

## Look and feel

Each lesson uses callout boxes, numbered step lists, state badges, and a
few illustrative diagrams (labeled as such - built with styled HTML/CSS,
not screenshots of the real running app, so they never go stale as the
UI changes). The styling lives in
`static/src/scss/course_content.scss`, loaded via `web.assets_frontend`
and scoped under `.oe-course-content` so it can't leak into the rest of
the site's theme. This is the pattern the other eLearning packs in this
account are being brought in line with.

## Access

Gated (`visibility="members"`, `enroll="invite"`); everyone in
`website.group_website_designer` ("Editor and Designer") is auto-enrolled
via `enroll_group_ids`.

## Dependencies

Only `website_slides` + stock Odoo's `website` app - no custom module, no
one organization. Installable on any Odoo 19 Community instance.
