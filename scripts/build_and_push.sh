#!/usr/bin/env bash
# Build backend + frontend images for linux/amd64 and linux/arm64 and push them
# to the registry. Run this locally (this machine is amd64; arm64 is cross-built
# via QEMU through buildx).
#
# CI no longer builds/pushes images -- the Forgejo runner (a Raspberry Pi) was
# too flaky under QEMU cross-arch emulation (nondeterministic segfaults/hangs
# in uv and npm). CI now only lints; this script is the release step.
#
# Usage: ./scripts/build_and_push.sh
set -euo pipefail

cd "$(dirname "$0")/.."

REGISTRY="forgejo.home.liteapp.fr"
IMAGE_BASE="$REGISTRY/alexis/magev_planner"
SHA="$(git rev-parse HEAD)"
PLATFORMS="linux/amd64,linux/arm64"
BUILDER="magev-planner-builder"

if ! docker buildx inspect "$BUILDER" >/dev/null 2>&1; then
  echo "==> Creating buildx builder $BUILDER"
  docker buildx create --name "$BUILDER" --driver docker-container --bootstrap
fi

build() {
  local name="$1" target="$2"
  local image="${IMAGE_BASE}-${name}"
  echo "==> Building and pushing ${image} (${PLATFORMS})"
  docker buildx build \
    --builder "$BUILDER" \
    --platform "$PLATFORMS" \
    --target "$target" \
    -t "${image}:latest" \
    -t "${image}:${SHA}" \
    --provenance=false \
    --sbom=false \
    --push \
    .
}

build backend production
build frontend frontend-prod

echo "==> Done. Pushed :latest and :${SHA} for backend + frontend."
