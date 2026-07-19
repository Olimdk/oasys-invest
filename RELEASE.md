# Release

## 0.1.0
- Initial release of OASYS Invest as a Tauri desktop app.
- Bundled FastAPI engine (live market data, skyrocket radar, trending, copy-trading,
  alerts, portfolio analyzer).
- Offline fallback snapshot when network is unavailable.
- Native Linux bundles: `.deb` and `.AppImage`.

## Building

    npm install
    npm run tauri build

Artifacts land in `src-tauri/target/release/bundle/`.
