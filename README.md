# dxm-image-bridge

Temporary GitHub raw image bridge for product listing assets.

## Image Cache Policy

`dxm-image-bridge/images/` only keeps recent temporary publishing cache.

Long-term source files live in:

```text
pod_rug/products/{Design_ID}/listing_assets/
```

The bridge repository is not an asset library. `images/{Design_ID}/` directories can be removed after the raw URLs have been imported successfully.

Cache cleanup rule:

- Keep only the most recent 3 days of publishing cache.
- Delete only `images/{Design_ID}/` directories.
- Do not delete `IMAGE_URLS.json`.
- Do not delete anything under `pod_rug/`.

Run:

```bash
python scripts/cleanup_expired_images.py --days 3
```
