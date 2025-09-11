#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_addons_index_plus.py
--------------------------
Genera addons.xml y addons.xml.md5 a partir de ./zips y añade utilidades:
  - --lint : revisa URLs del addon de repositorio
  - --fix  : imprime SUGERENCIAS de URLs correctas (no modifica zips)

Uso:
  python build_addons_index_plus.py [--repo-root RUTA] [--lint] [--fix]

Requisitos: Python 3 estándar.
"""

import os
import sys
import re
import zipfile
import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path

RAW_PREFIX = "https://raw.githubusercontent.com/"

def norm_version_tuple(v):
    parts = []
    for p in str(v).split("."):
        num = ''.join(ch for ch in p if ch.isdigit())
        parts.append(int(num) if num.isdigit() else 0)
    while len(parts) < 4:
        parts.append(0)
    return tuple(parts[:4])

def find_addon_xml_in_zip(zf: zipfile.ZipFile):
    candidates = [zi for zi in zf.infolist() if zi.filename.lower().endswith("addon.xml")]
    if not candidates:
        return None
    candidates.sort(key=lambda zi: zi.filename.count("/"))
    return candidates[0]

def detect_encoding_and_decode(data: bytes):
    head = data[:200].decode("utf-8", errors="ignore")
    enc = "utf-8"
    m = None
    if head.startswith("<?xml"):
        m = re.search(r'encoding=["\']([A-Za-z0-9_\-]+)["\']', head)
    if m:
        enc = m.group(1)
    try:
        return data.decode(enc, errors="replace")
    except Exception:
        return data.decode("utf-8", errors="replace")

def pretty_xml(elem: ET.Element, level=0):
    indent = "    "
    i = "\n" + level * indent
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + indent
        for e in elem:
            pretty_xml(e, level + 1)
            if not e.tail or not e.tail.strip():
                e.tail = i + indent
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def build_addons_xml(repo_root: Path):
    zips_dir = repo_root / "zips"
    if not zips_dir.exists():
        raise SystemExit(f"No existe la carpeta: {zips_dir}")

    addons_by_id = {}
    for root, _, files in os.walk(zips_dir):
        for fn in files:
            if not fn.lower().endswith(".zip"):
                continue
            zip_path = Path(root) / fn
            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zi = find_addon_xml_in_zip(zf)
                    if not zi:
                        print(f"[ADVERTENCIA] No se encontró addon.xml dentro de: {zip_path}")
                        continue
                    xml_text = detect_encoding_and_decode(zf.read(zi)).strip()
                    try:
                        root_el = ET.fromstring(xml_text)
                    except Exception as e:
                        print(f"[ADVERTENCIA] addon.xml inválido en {zip_path}: {e}")
                        continue

                    addon_node = root_el if root_el.tag == "addon" else root_el.find(".//addon")
                    if addon_node is None:
                        print(f"[ADVERTENCIA] No se encontró nodo <addon> en {zip_path}")
                        continue

                    addon_id = addon_node.attrib.get("id")
                    addon_ver = addon_node.attrib.get("version", "0.0.0")
                    if not addon_id:
                        print(f"[ADVERTENCIA] addon.xml sin id en {zip_path}")
                        continue

                    prev = addons_by_id.get(addon_id)
                    if prev is None or norm_version_tuple(addon_ver) > norm_version_tuple(prev[0]):
                        addons_by_id[addon_id] = (addon_ver, ET.fromstring(ET.tostring(addon_node, encoding="utf-8")))

            except zipfile.BadZipFile:
                print(f"[ADVERTENCIA] ZIP corrupto: {zip_path}")
                continue

    root_addons = ET.Element("addons")
    for addon_id in sorted(addons_by_id.keys()):
        _, addon_elem = addons_by_id[addon_id]
        root_addons.append(addon_elem)

    pretty_xml(root_addons)
    xml_decl = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    return (xml_decl.encode("utf-8") + ET.tostring(root_addons, encoding="utf-8"))

def write_md5_for(path: Path):
    data = path.read_bytes()
    md5 = hashlib.md5(data).hexdigest()
    (path.parent / (path.name + ".md5")).write_text(md5, encoding="ascii")
    return md5

def extract_owner_repo(url: str):
    """
    Devuelve (owner, repo) si la URL es raw.githubusercontent.com
    """
    m = re.match(r'^https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/', url or '')
    if m:
        return m.group(1), m.group(2)
    return None, None

def lint_and_fix_suggestions(repo_root: Path, suggest: bool):
    zips_dir = repo_root / "zips"
    issues = []
    suggestions = []

    for root, _, files in os.walk(zips_dir):
        for fn in files:
            if not fn.lower().endswith(".zip"):
                continue
            zip_path = Path(root) / fn
            try:
                with zipfile.ZipFile(zip_path, "r") as zf:
                    zi = find_addon_xml_in_zip(zf)
                    if not zi:
                        continue
                    xml_text = detect_encoding_and_decode(zf.read(zi)).strip()
                    try:
                        root_el = ET.fromstring(xml_text)
                    except Exception:
                        continue
                    addon_node = root_el if root_el.tag == "addon" else root_el.find(".//addon")
                    if addon_node is None:
                        continue

                    addon_id = addon_node.attrib.get("id", "<sin id>")

                    for ext in addon_node.findall("extension"):
                        if ext.attrib.get("point") == "xbmc.addon.repository":
                            dir_node = ext.find("dir")
                            if dir_node is None:
                                issues.append((zip_path, addon_id, "Falta <dir> dentro de la extension xbmc.addon.repository"))
                                continue

                            dn = dir_node.find("datadir")
                            info = dir_node.findtext("info", default="").strip()
                            checksum = dir_node.findtext("checksum", default="").strip()
                            datadir = dn.text.strip() if dn is not None and dn.text else ""
                            datadir_zip_true = (dn is not None and dn.attrib.get("zip") == "true")

                            # Reglas
                            def bad(cond, msg):
                                if cond:
                                    issues.append((zip_path, addon_id, msg))

                            bad(not info.startswith(RAW_PREFIX), "<info> no usa raw.githubusercontent.com")
                            bad("/refs/heads/" in info, "<info> no debe usar /refs/heads/, usa /main/")
                            bad(not info.endswith("/addons.xml"), "<info> debe terminar en /addons.xml")
                            bad("/main/" not in info, "<info> debería incluir /main/")

                            bad(not checksum.startswith(RAW_PREFIX), "<checksum> no usa raw.githubusercontent.com")
                            bad("/refs/heads/" in checksum, "<checksum> no debe usar /refs/heads/, usa /main/")
                            bad(not checksum.endswith("/addons.xml.md5"), "<checksum> debe terminar en /addons.xml.md5")
                            bad("/main/" not in checksum, "<checksum> debería incluir /main/")

                            bad(not datadir.startswith(RAW_PREFIX), "<datadir> no usa raw.githubusercontent.com")
                            bad("/refs/heads/" in datadir, "<datadir> no debe usar /refs/heads/, usa /main/")
                            bad("/main/" not in datadir, "<datadir> debería incluir /main/")
                            bad(not (datadir.endswith("/zips/") or datadir.endswith("/zips")), "<datadir> debería terminar en /zips/")
                            bad(not datadir_zip_true, '<datadir> debería tener atributo zip="true"')

                            if suggest:
                                # Deducir owner/repo de la mejor fuente disponible
                                owner, repo = extract_owner_repo(info)
                                if not owner:
                                    owner, repo = extract_owner_repo(checksum)
                                if not owner:
                                    owner, repo = extract_owner_repo(datadir)
                                if owner and repo:
                                    base = f"{RAW_PREFIX}{owner}/{repo}/main"
                                    suggestions.append((zip_path, addon_id, {
                                        "info":     f"{base}/addons.xml",
                                        "checksum": f"{base}/addons.xml.md5",
                                        "datadir":  f"{base}/zips/",
                                        "datadir_attr": ' zip="true" ' if not datadir_zip_true else ' zip="true" ',
                                    }))
                                else:
                                    suggestions.append((zip_path, addon_id, {
                                        "info":     "<pon_aqui_tu_URL_raw>/addons.xml",
                                        "checksum": "<pon_aqui_tu_URL_raw>/addons.xml.md5",
                                        "datadir":  "<pon_aqui_tu_URL_raw>/zips/",
                                        "datadir_attr": ' zip="true" ',
                                    }))

            except zipfile.BadZipFile:
                issues.append((zip_path, "<desconocido>", "ZIP corrupto"))

    if issues:
        print("=== LINT: Problemas detectados ===")
        for path, aid, msg in issues:
            print(f"- [{aid}] {path}: {msg}")
    else:
        print("=== LINT: Sin problemas de URLs en los repositorios ===")

    if suggest and suggestions:
        print("\n=== SUGERENCIAS (--fix) ===")
        for path, aid, sugg in suggestions:
            print(f"\n# [{aid}] {path}")
            print("Reemplaza el bloque <dir> por algo así:")
            print("  <dir>")
            print(f"    <info compressed=\"false\">{sugg['info']}</info>")
            print(f"    <checksum>{sugg['checksum']}</checksum>")
            print(f"    <datadir{sugg['datadir_attr'].strip()}>"+sugg['datadir']+"</datadir>")
            print("  </dir>")

def main():
    repo_root = Path(os.getcwd())
    args = sys.argv[1:]
    lint_mode = False
    fix_mode = False
    if "--repo-root" in args:
        i = args.index("--repo-root")
        try:
            repo_root = Path(args[i+1]).resolve()
        except Exception:
            print("Uso: python build_addons_index_plus.py [--repo-root RUTA] [--lint] [--fix]")
            sys.exit(2)
    if "--lint" in args:
        lint_mode = True
    if "--fix" in args:
        fix_mode = True

    print(f"[i] Repo root: {repo_root}")
    xml_out = build_addons_xml(repo_root)
    addons_xml_path = repo_root / "addons.xml"
    addons_xml_path.write_bytes(xml_out)
    md5 = write_md5_for(addons_xml_path)
    print(f"[✔] Generado: {addons_xml_path}")
    print(f"[✔] Generado: {addons_xml_path}.md5 (md5={md5})")

    if lint_mode or fix_mode:
        lint_and_fix_suggestions(repo_root, suggest=fix_mode)

if __name__ == "__main__":
    main()
