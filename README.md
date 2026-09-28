# Teho Server Directory

A community-contributed home for Minecraft server identities in Teho Client.
Submit your server's name, addresses and artwork to give it a consistent presence
in the launcher server browser and Discord Rich Presence.

## Submit a server

1. Fork this repository.
2. Create `listings/<your-server-id>/` with your server details, logo and banner.
3. Open a pull request for review.

Start with [the submission guide](guides/submitting.md). It covers artwork
requirements, hostname verification and how to update an existing listing.

Your `server.json` should look like this:

```json
{
  "name": "My Server",
  "address": "play.example.com",
  "domains": ["play.example.com"],
  "description": "A short description of your server."
}
```

Include one `logo.png` or `logo.gif` and one `banner.png` or `banner.gif`.
Logos must be square, 128 to 1024 pixels per side. Banners must be 16:9,
640 to 1920 pixels wide. Each file can be up to 5 MiB, with additional animation
limits described in the guide.

You must own the server or be authorised to represent it, and have permission to
submit its artwork. Reviewers check hostname ownership, content and server details
before approving a listing. Passing automated checks does not guarantee acceptance.

The [example entry](spec/entry.example.json) and [JSON schema](spec/entry.schema.json)
are available for reference. To update or remove a listing, open a PR against its
existing folder.

## How listings appear

- **Community:** the default for approved submissions.
- **Partnered:** servers with a Teho partnership.
- **Sponsored:** clearly labelled promoted listings with a defined expiry.

Partnered servers appear first, followed by Sponsored and Community. Teho manages
these placements separately from submissions. Please do not include payment or
billing details in issues or pull requests.

## Check your submission

With Python 3.12 or newer, run these commands from the repository root:

```sh
python -m pip install -r tools/requirements.txt
python -m unittest discover -s tools/tests
python tools/build.py
```

These checks validate metadata and decode the artwork. They do not publish
anything or require credentials. Generated files go into the gitignored `dist/`
directory. Publication is handled by Teho after review.

## Repository layout

- `listings/`: reviewed server metadata and artwork.
- `spec/`: the entry schema and a documentation-only example.
- `tools/`: validation, publishing and tests.
- `guides/`: contribution instructions.
- `.github/`: GitHub workflows and the pull request template.
- `placements.json`: maintainer-controlled promotion and ordering.

## Acknowledgment

The community submission approach was inspired by
[Lunar Client's Server Mappings project](https://github.com/LunarClient/ServerMappings).
Thank you to the Lunar team for the inspiration. Teho Server Directory is
independently developed and is not affiliated with or endorsed by Lunar Client.

Server names and artwork belong to their respective owners. Submission does not
transfer ownership or give others a general licence to reuse the artwork.
