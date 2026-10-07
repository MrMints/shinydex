# ShinyDex 1.1.2

## Release description
The routine Saved on Device message and indicator are removed; autosave and save-error feedback remain active. Pokémon with only the Standard form no longer show an unnecessary form dropdown. Multiple-form selectors remain available.

Desktop collections retain the version-2 format and existing profile. Save compatibility passed across all twelve directed pairs between 1.0.0, 1.1.0, 1.1.1 and 1.1.2 using all catalog IDs plus an unknown future ID. The actual renderer upgrade/rollback/re-upgrade checks, six desktop tests, living-dex verifier, visual review and packaged smoke passed.

**Export a backup from 1.1.0 or newer before rolling back to 1.0.0.** The 1.0.0 Export backup button omits newer form IDs, although its desktop disk autosaves preserve them and upgrading again restores them. Browser profiles are separate.

Testing used isolated release code and fixture saves. Real NSIS installation, public updater installation/restart and clean-machine behavior remain unverified. The exhaustive gameplay audit remains incomplete.

Download **ShinyDex.exe** for Windows x64. The installer is unsigned. **ShinyDex.exe.sha256** contains its SHA-256 checksum; latest.yml and the blockmap support automatic updates.

## Upload contents
ShinyDex.exe, latest.yml, ShinyDex.exe.blockmap, ShinyDex.exe.sha256.
