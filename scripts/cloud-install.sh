#!/bin/sh
# Rootless PHP setup for this Debian cloud environment. Keeps APT signature checks.
set -eu
R=/workspace/php-runtime
if [ -x "$R/bin/php" ] && "$R/bin/php" -r 'exit(extension_loaded("pdo_sqlite") && extension_loaded("mbstring") && extension_loaded("fileinfo") ? 0 : 1);'; then
  exit 0
fi
D=$(mktemp -d /tmp/sola-install.XXXXXX)
trap 'rm -rf "$D"' EXIT
mkdir -p "$D/lists/partial" "$D/cache/archives/partial" "$D/debs" "$R/bin"
printf '%s\n' 'deb https://deb.debian.org/debian trixie main' 'deb https://deb.debian.org/debian-security trixie-security main' > "$D/sources.list"
apt-get -o Dir::Etc::sourcelist="$D/sources.list" -o Dir::Etc::sourceparts=- -o Dir::State::lists="$D/lists" -o Dir::Cache="$D/cache" update
cd "$D/debs"
apt-get -o Dir::Etc::sourcelist="$D/sources.list" -o Dir::Etc::sourceparts=- -o Dir::State::lists="$D/lists" download php8.4-cli php8.4-common php8.4-sqlite3 php8.4-mbstring libxml2 libedit2 libsodium23 libargon2-1 libpcre2-8-0 libonig5
for package in ./*.deb; do dpkg-deb -x "$package" "$R"; done
cat > "$R/bin/php" <<'WRAPPER'
#!/bin/sh
R=/workspace/php-runtime
export LD_LIBRARY_PATH="$R/usr/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec "$R/usr/bin/php8.4" -n -d "extension_dir=$R/usr/lib/php/20240924" -d extension=pdo -d extension=pdo_sqlite -d extension=sqlite3 -d extension=mbstring -d extension=fileinfo "$@"
WRAPPER
chmod +x "$R/bin/php"
"$R/bin/php" -r 'exit(extension_loaded("pdo_sqlite") && extension_loaded("mbstring") && extension_loaded("fileinfo") ? 0 : 1);'
