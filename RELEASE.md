# Release

## 0.2.0
- Fix window not scaling on resize: content now reflows fluidly instead of being
  clipped/cut off at smaller widths.
  - Removed fixed `max-width:1180px` cap on the content area; it now fills available
    space and scrolls internally.
  - Made the Top 25 rank-row grid responsive (flexible minmax columns) so columns
    shrink instead of overflowing.
  - Added a 1024px breakpoint that collapses optional columns (sparkline, reasons,
    action) for the 860–1180px range that was previously broken.
  - Widened the existing mobile breakpoint and capped form/input widths at 100%.
- Lowered Tauri window minimum size to 640x480 so the window can shrink further
  without triggering the old cutoff.

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
