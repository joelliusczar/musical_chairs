"""
This type stub file was generated by pyright.
"""

from tinytag.tinytag import TinyTag, TinyTagException # type: ignore

def usage() -> None:
    ...

def pop_param(name: str, _default: str) -> str:
    ...

def pop_switch(name: str, _default: str) -> bool:
    ...

header_printed: bool = ...