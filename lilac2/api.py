import logging
import shutil
from typing import Tuple

from .cmd import run_cmd, git_pull, git_push
from .pkgbuild import (
  add_into_array, add_depends, add_makedepends,
  edit_file,
)
from .typing import Floatlike

git_push, git_pull, add_into_array, add_depends, add_makedepends
edit_file

logger = logging.getLogger(__name__)

def vcs_update() -> None:
  # clean up the old source tree
  shutil.rmtree('src', ignore_errors=True)
  run_cmd(['makepkg', '-od'], use_pty=True)

def get_pkgver_and_pkgrel() -> Tuple[str, Floatlike]:
  pkgrel = None
  pkgver = None
  with open('PKGBUILD') as f:
    for l in f:
      if l.startswith('pkgrel='):
        pkgrel = float(l.rstrip().split('=', 1)[-1].strip('\'"'))
        if int(pkgrel) == pkgrel:
            pkgrel = int(pkgrel)
      elif l.startswith('pkgver='):
        pkgver = l.rstrip().split('=', 1)[-1]

  assert pkgver is not None and pkgrel is not None

  return pkgver, pkgrel

def update_pkgver_and_pkgrel(
  newver: str, *, updpkgsums: bool = True) -> None:

  pkgver, pkgrel = get_pkgver_and_pkgrel()

  for line in edit_file('PKGBUILD'):
    if line.startswith('pkgver=') and pkgver != newver:
        line = f'pkgver={newver}'
    elif line.startswith('pkgrel='):
      if pkgver != newver:
        line = 'pkgrel=1'
      else:
        line = f'pkgrel={int(pkgrel)+1}'

    print(line)

  if updpkgsums:
    run_cmd(["updpkgsums"])
