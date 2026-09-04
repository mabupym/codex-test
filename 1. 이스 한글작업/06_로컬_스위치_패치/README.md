# Ys Celceta Switch Local Patch

This folder contains the locally generated LayeredFS patch.

## Current contents

- `romfs/text/item.tbb`: Korean item names and descriptions.
- The file keeps the Switch table structure: 32 fields and 1001 records.
- The source file was validated with a byte-for-byte TBB round-trip.

## Install on Atmosphere

Copy the contents of this folder to the SD card so the final path is:

```text
SD:/atmosphere/contents/0100D370219DA000/romfs/text/item.tbb
```

Do not copy PC `.itp`, `.itf`, or other PC image/font files into the Switch RomFS. Those formats are different and can produce corrupted multi-panel images.

Remove the `0100D370219DA000` content folder to disable the patch.
