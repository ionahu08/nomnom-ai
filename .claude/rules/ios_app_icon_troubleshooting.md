# iOS App Icon Not Displaying — Troubleshooting Checklist

**Symptom:** Icon preview looks correct in Xcode Asset Catalog, but home screen shows blank/generic icon.  
Clean build, delete app, restart all fail → almost certainly one of these two issues.

---

## Root Cause 1: Assets.xcassets Not Included in Copy Bundle Resources (Most Common)

**Why it happens:**  
Asset Catalog preview in the editor ≠ compiled into the .app bundle. Manually created catalogs or projects generated with XcodeGen/Tuist/SPM often lack this build phase, so icons never make it into the package.

**Check:**
```
Target (NomNom) → Build Phases → Look for "Copy Bundle Resources"
Expand it → verify "Assets.xcassets" is listed inside
```

**Fix:**
1. If the entire phase is missing: Click `+` (top left) → New Copy Bundle Resources Phase
2. Expand the new phase → click `+` inside → search "Assets" → add Assets.xcassets
3. Confirm it shows "Copy Bundle Resources (1 item)"
4. Clean (⇧⌘K) → delete app from device → reinstall (⌘R)

**Important:**  
If your project is generated from a manifest file (project.yml / Project.swift / Package.swift), manually added phases will be overwritten on next generation → you must add the resource configuration to the manifest itself.

---

## Root Cause 2: PNG Has Alpha Channel (hasAlpha = yes)

**Why it happens:**  
Home screen app icons do not support transparency. PNGs with alpha channels will render as blank.

**Requirements:**
- Square dimensions
- Exactly 1024×1024 pixels
- sRGB color space
- hasAlpha = no

**Check:**
```bash
sips -g pixelWidth -g pixelHeight -g hasAlpha -g space icon.png
```

**Fix (sips --setProperty often reports Error 13, so use JPEG intermediate to remove alpha):**
```bash
# Method: PNG → JPEG → PNG (removes alpha channel)
sips -s format jpeg icon.png --out /tmp/t.jpg
sips -s format png /tmp/t.jpg --out icon-fixed.png

# Note: JPEG doesn't support transparency. Transparent areas composite to white background
# (not black), which is safer for app icons.
```

**Verify:**
```bash
sips -g hasAlpha icon-fixed.png   # Should output: hasAlpha: no
```

---

## Universal Reset Procedure (After fixing either issue)

1. **On iPhone:** Long-press app → Remove App (complete uninstall)
2. **In Xcode:** Product → Clean Build Folder (⇧⌘K)
3. **If needed, delete cached data:**
   ```bash
   rm -rf ~/Library/Developer/Xcode/DerivedData
   ```
4. **Reinstall:** ⌘R. If icon cache is stubborn, restart the iPhone to refresh SpringBoard.

---

## NomNom Project Resolution

| Issue | Status |
|---|---|
| Copy Bundle Resources missing | ✅ Fixed (added build phase) |
| PNG hasAlpha = yes | ✅ Fixed (removed alpha channel) |
| Result | ✅ Icon displays correctly |

---

## References

- [Apple: App Icons - iOS App Programming Guide](https://developer.apple.com/ios/human-interface-guidelines/icons-and-images/app-icon/)
- `sips` manual: `man sips`
