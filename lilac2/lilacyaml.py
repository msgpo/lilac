from __future__ import annotations

import pathlib
from typing import Dict, Any, Iterator, List
import importlib.resources

import yaml

from . import api

ALIASES: Dict[str, Any]
FUNCTIONS: List[str] = [
  'pre_build', 'post_build', 'post_build_always',
]

def _load_aliases() -> None:
  global ALIASES
  data = importlib.resources.read_text('lilac2', 'aliases.yaml')
  ALIASES = yaml.safe_load(data)

_load_aliases()

def iter_pkgdir(
  repodir: pathlib.Path,
) -> Iterator[pathlib.Path]:

  for x in repodir.iterdir():
    if x.name[0] == '.':
      continue

    # leftover files, e.g. __pycache__ stuff
    if not (x / 'lilac.yaml').is_file():
      continue

    yield x

def load_lilac_yaml(dir: pathlib.Path) -> Dict[str, Any]:
  with open(dir / 'lilac.yaml') as f:
    conf = yaml.safe_load(f)

  if conf is None:
    return {}

  update_on = conf.get('update_on')
  if update_on:
    for i, entry in enumerate(update_on):
      if isinstance(entry, str):
        update_on[i] = {entry: ''}

  depends = conf.get('repo_depends')
  if depends:
    for i, entry in enumerate(depends):
      if isinstance(entry, dict):
        depends[i] = next(iter(entry.items()))
      else:
        depends[i] = entry, entry

  for func in FUNCTIONS:
    name = conf.get(func)
    if name:
      funcvalue = getattr(api, name)
      conf[func] = funcvalue

  return conf
