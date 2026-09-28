# Contributing a server

Submit only a public server you own or are authorised to represent.

## Files to submit

Create `listings/<your-server-id>/`, using lowercase letters, numbers and hyphens.
Include only these files:

- `server.json`: copy [the entry example](../spec/entry.example.json) and replace its values.
- One `logo.png` or `logo.gif`: square, 128 to 1024 pixels per side.
- One `banner.png` or `banner.gif`: exactly 16:9, 640 to 1920 pixels wide.

Each image must be at most 5 MiB. Animations are limited to 120 frames and 150
million decoded pixels per image. Use artwork you have permission to submit and
content suitable for all ages. Do not include executables, symlinks or tracking.

Names allow 1 to 48 characters; descriptions allow up to 240. List 1 to 16 exact,
lowercase hostnames in `domains`, including the hostname used in `address`.
The address can include a port from 1 to 65535, such as `play.example.com:25566`.
Wildcards, IP addresses and duplicate domains are not accepted. List each alias
explicitly; one hostname does not claim its subdomains or a shared hosting domain.

Do not add placement or Discord application IDs to your metadata. Only maintainers
change `placements.json`; ordinary submissions start as Community.

## Ownership and review

Open a PR explaining the server and your relationship to it. A maintainer will
issue a fresh DNS TXT challenge for each hostname, for example at
`_teho-directory.play.example.com`. Publish the value provided in the review.
Never share passwords or DNS provider tokens. Ownership verification is manual;
passing CI alone does not approve a listing or prove ownership.

By submitting artwork, you confirm you can authorise Teho to host, cache and display
it in the directory, client integrations and associated Discord presence. You
retain ownership. Other users do not receive a general licence to reuse it.

## Updates and removals

Edit your existing folder rather than adding duplicate entries. New hostnames
require verification. Request removal through a PR; a maintainer can also remove
any associated placement record. Keep billing details and personal data out of PRs.

## Local checks

```sh
python -m pip install -r tools/requirements.txt
python -m unittest discover -s tools/tests
python tools/build.py
```

Python 3.12 or newer is recommended. These checks need no CDN credentials.
The example under `spec/` is documentation, not a published server listing.
