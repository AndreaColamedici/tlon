#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggiunge i dati strutturati alle pagine che ne sono prive.

Regola: nessun fatto nuovo. Nome e descrizione vengono dal <title> e dalla
meta description già presenti nella pagina; gli indirizzi delle librerie dal
markup della pagina stessa. Se una pagina ha già un blocco JSON-LD, viene
lasciata stare.
"""
import re, io, json, os, html

TIPO = {
    'il-progetto.html': 'AboutPage', 'il-progetto-en.html': 'AboutPage',
    'edizioni.html': 'CollectionPage', 'edizioni-en.html': 'CollectionPage',
    'librerie.html': 'CollectionPage', 'librerie-en.html': 'CollectionPage',
    'formazione.html': 'WebPage', 'formazione-en.html': 'WebPage',
    'eventi-festival.html': 'CollectionPage', 'eventi-festival-en.html': 'CollectionPage',
    'podcast.html': 'CollectionPage', 'podcast-en.html': 'CollectionPage',
    'ricerca.html': 'WebPage', 'ricerca-en.html': 'WebPage',
    'ilpod.html': 'WebPage', 'ilpod-en.html': 'WebPage',
    'ipnocrazia.html': 'WebPage', 'ipnocrazia-en.html': 'WebPage',
    'cimiterologia.html': 'WebPage', 'cimiterologia-en.html': 'WebPage',
    'contatti/index.html': 'ContactPage', 'contatti/en.html': 'ContactPage',
    'privacy.html': 'WebPage',
}

# Le librerie: dati letti dal markup di librerie.html. La Galleria Nazionale
# resta fuori finché non è confermata operativa (vedi nota nel README).
LIBRERIE = [
    {"name": "Libreria Teatro Tlon", "street": "Via Federico Nansen, 14",
     "postal": "00154", "city": "Roma", "email": "libreriateatro@tlon.it"},
    {"name": "Villa Medici", "street": "Viale della Trinità dei Monti, 1",
     "postal": "00187", "city": "Roma", "email": "michele.trionfera@tlon.it"},
    {"name": "Libreria Giovanni", "street": "Campo Santa Maria Formosa, 5252",
     "postal": "30122", "city": "Venezia", "email": "tlon@querinistampalia.org"},
]


def bookstore(b, i):
    return {"@type": "ListItem", "position": i + 1, "item": {
        "@type": "BookStore", "name": b["name"], "email": b["email"],
        "parentOrganization": {"@id": "https://www.tlon.it/#organization"},
        "address": {"@type": "PostalAddress", "streetAddress": b["street"],
                    "postalCode": b["postal"], "addressLocality": b["city"],
                    "addressCountry": "IT"}}}


def main():
    fatte = []
    for pagina, tipo in sorted(TIPO.items()):
        if not os.path.exists(pagina):
            continue
        s = io.open(pagina, encoding='utf-8').read()
        if 'application/ld+json' in s:
            continue
        titolo = re.search(r'<title>(.*?)</title>', s, re.S)
        desc = re.search(r'<meta name="description" content="([^"]*)"', s)
        canon = re.search(r'<link rel="canonical" href="([^"]*)"', s)
        if not (titolo and canon):
            print("  salto (manca title o canonical):", pagina); continue
        lingua = 'en' if re.search(r'<html lang="en"', s) else 'it'
        nodo = {
            "@context": "https://schema.org", "@type": tipo,
            "@id": canon.group(1), "url": canon.group(1),
            "name": html.unescape(titolo.group(1)).strip(),
            "inLanguage": lingua,
            "isPartOf": {"@id": "https://www.tlon.it/#website"},
            "publisher": {"@id": "https://www.tlon.it/#organization"},
            "about": {"@id": "https://www.tlon.it/#organization"},
        }
        if desc:
            nodo["description"] = html.unescape(desc.group(1)).strip()
        if pagina.startswith('librerie'):
            nodo["mainEntity"] = {"@type": "ItemList",
                                  "numberOfItems": len(LIBRERIE),
                                  "itemListElement": [bookstore(b, i) for i, b in enumerate(LIBRERIE)]}
        blocco = ('<script type="application/ld+json">%s</script>\n'
                  % json.dumps(nodo, ensure_ascii=False))
        s = s.replace('</head>', blocco + '</head>', 1)
        io.open(pagina, 'w', encoding='utf-8').write(s)
        fatte.append('%s (%s)' % (pagina, tipo))
    print("pagine con dati strutturati aggiunti:", len(fatte))
    for f in fatte:
        print("  ", f)


if __name__ == '__main__':
    main()
