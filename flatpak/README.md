# Development-only Flatpak manifest

The manifest \`com.goreecloud.youtubeplayer.Dev.yml\` is for isolated local
experiments, not distribution. GoreeCloud does not claim that this Flatpak has
been built, installed, reviewed or signed.

The independently branded AppStream and desktop files identify
\`com.goreecloud.youtubeplayer.Dev\`. The desktop bundle command uses
\`goreecloud-youtube-player\`, not the inherited NouTube executable.

## Prerequisites

The manifest currently targets Flatpak Freedesktop SDK 25.08,
\`org.electronjs.Electron2.BaseApp\`, and pinned upstream Electron/Bun archives.
Its dependency versions and checksums must be refreshed and verified before
first build. Local dependencies must already be installed in the source tree.

## Example development-only commands

\`\`\`sh
flatpak-builder --force-clean build-dir flatpak/com.goreecloud.youtubeplayer.Dev.yml
flatpak-builder --run build-dir flatpak/com.goreecloud.youtubeplayer.Dev.yml run.sh
\`\`\`

Do not upload, publish or represent development output as Stable. Real
compatibility, runtime, accessibility, media and privacy checks remain open in
GitHub Issue #2. Upstream author attribution and the source license remain in
\`UPSTREAM.md\` and \`LICENSE\`.
