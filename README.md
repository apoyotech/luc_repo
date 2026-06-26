# luc_kodi

A front-end add-on for Kodi that organises movies and TV shows and connects to
**third-party services you configure with your own accounts**.

> **This add-on hosts no content and includes no links.** It is an interface to
> third-party debrid services and indexers that you set up with your own
> credentials. See [Terms of Use](TERMS.md) and
> [DMCA & Copyright Policy](DMCA.md).

## What it is

`luc_kodi` is a user interface. It uses public metadata (TMDB and similar) to
browse and organise titles, and it connects to the services **you** provide —
debrid accounts and torrent indexers — to locate and play sources. Without your
own accounts and configuration, it returns no playable sources.

## Features

- Browse and organise movies and TV shows using TMDB metadata and artwork
- Optional integration with tracking services you configure (Trakt, SIMKL, MDBList)
- Works with the debrid services you configure with your own accounts
  (Real-Debrid, AllDebrid, Premiumize, TorBox)
- Works with the torrent indexers you choose to enable
- Subtitle support via the providers you configure

## Installation

1. In Kodi, go to **Settings → File manager → Add source**.
2. Enter the repository URL `https://apoyotech.github.io/luc_repo` and give it a name.
3. Go to **Add-ons → Install from zip file** and install the repository zip.
4. Go to **Install from repository → (repo name) → Video add-ons → luc_kodi → Install**.

You can also install the add-on directly from its zip file if you prefer.

## Configuration

This add-on does nothing on its own. After installing, open the add-on settings
and add **your own** accounts and API keys for the services you want to use
(debrid, indexers, metadata, subtitles). All credentials stay in your own Kodi
installation.

## Legal

- This project hosts no content and includes no links — see [Terms of Use](TERMS.md).
- Copyright concerns — see [DMCA & Copyright Policy](DMCA.md).
- You are responsible for the sources you enable and for complying with the laws
  of your country.

## License

This add-on is free software, licensed under the **GNU General Public License
v3.0 or later** (`GPL-3.0-or-later`). See [LICENSE](LICENSE.md) for the full text.

## Support

If you find this project useful, you can support its development on
[Ko-fi](https://ko-fi.com/luc64234).
