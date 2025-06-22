#!/bin/sh

# 수동 key-value 형태 배열
reset_tag() {
  tag=$1
  commit=$2

  echo "🔁 Resetting tag: $tag → $commit"

  git tag -d "$tag" 2>/dev/null
  git push origin ":refs/tags/$tag"

  git tag -a "$tag" "$commit" -m "Release $tag"
  git push origin "$tag"

  echo "✅ Done: $tag"
}

# 각 태그별 커밋 지정
reset_tag v0.4.1 082958f
reset_tag v0.4.0 fb95c77
reset_tag v0.3.0 8578dc8
reset_tag v0.2.0 5727740

