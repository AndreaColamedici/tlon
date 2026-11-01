# -*- coding: utf-8 -*-
"""Genera fabbricabellezza/index.html (La fabbrica della bellezza, Maura Gancitano, Rizzoli 2026).

Quarta versione, 1 novembre 2026 (dipinto e copertina dal PDF di stampa Rizzoli, sedi delle tappe come immagini). Terza versione: un solo mondo blu, la copertina a tutto schermo, le tavole del libro
come cinema legato allo scorrimento, Gloock per i titoli ed Epilogue per il testo. I token sono in
fabbricabellezza/MASTER.md. Le tappe sono nella lista TAPPE; i link .ics e le dimensioni delle immagini
sono calcolati qui. Uso: python3 tools/genera-fabbricabellezza.py (richiede ImageMagick per le dimensioni).
"""
import urllib.parse, html, datetime, pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent / "fabbricabellezza"
OUT = ROOT / "index.html"
SHOP = "https://shop.tlon.it/prodotto/la-fabbrica-della-bellezza-linvenzione-del-corpo-perfetto-dalla-fotografia-allintelligenza-artificiale-maura-gancitano-autografato/"
e = html.escape

def dims(name):
    out = subprocess.run(["identify", "-format", "%w %h", str(ROOT / "img" / name)], capture_output=True, text=True).stdout.split()
    return int(out[0]), int(out[1])

def img(base, alt, cls="", sizes="100vw", lazy=True, pos=None):
    big = next(f"{base}-{t}.webp" for t in ("1800", "1600", "1500", "1180", "900") if (ROOT / "img" / f"{base}-{t}.webp").exists())
    w, h = dims(big)
    small = next((f"{base}-{t}.webp" for t in ("900", "750", "700") if (ROOT / "img" / f"{base}-{t}.webp").exists()), None)
    srcset = f' srcset="img/{small} {dims(small)[0]}w, img/{big} {w}w" sizes="{sizes}"' if small and small != big else ""
    style = f' style="object-position:{pos}"' if pos else ""
    return (f'<img class="{cls}" src="img/{big}"{srcset} width="{w}" height="{h}" alt="{e(alt)}"'
            f'{" loading=\"lazy\"" if lazy else ' fetchpriority="high"'} decoding="async"{style}>')

# ---------- Le tappe ----------
TAPPE = [
    dict(key="milano", day="mercoledì", d="4", mon="novembre", time="18:30", city="Milano",
         venue="Libreria Rizzoli, Galleria Vittorio Emanuele II", with_="con Giulia Cavaliere",
         maps="Libreria Rizzoli Galleria Vittorio Emanuele II Milano", start="2026-11-04T18:30", end="2026-11-04T19:30",
         img="milano", alt="L’Ottagono della Galleria Vittorio Emanuele II, su cui si affaccia la Libreria Rizzoli"),
    dict(key="firenze", day="giovedì", d="5", mon="novembre", time="18:15", city="Firenze",
         venue="Libraccio, via de’ Cerretani", with_="con Alessia Dulbecco, a seguire firmacopie",
         maps="Libraccio via de' Cerretani Firenze", start="2026-11-05T18:15", end="2026-11-05T19:15",
         img="firenze", alt="Via de’ Cerretani, la strada del Libraccio, con la cupola del Duomo in fondo"),
    dict(key="prato", day="giovedì", d="5", mon="novembre", time="21:30", city="Prato",
         venue="Centro per l’arte contemporanea Luigi Pecci", with_="Pecci Books Festival",
         maps="Centro Pecci Prato", start="2026-11-05T21:30", end="2026-11-05T22:30",
         img="prato", alt="L’ingresso del Centro Pecci di Prato"),
    dict(key="pescara", day="venerdì", d="6", mon="novembre", time="17:30", city="Pescara",
         venue="FLA, Festival di Libri e altrecose", with_="il luogo è nel programma del festival",
         maps="FLA Festival di Libri e altrecose Pescara", start="2026-11-06T17:30", end="2026-11-06T18:30",
         img="pescara", alt="Il Ponte del Mare di Pescara"),
    dict(key="roma", day="domenica", d="8", mon="novembre", time="18:30", city="Roma",
         venue="Libreria Spazio Sette, via dei Barbieri 7", with_="con Sabina Minardi",
         maps="Libreria Spazio Sette via dei Barbieri 7 Roma", start="2026-11-08T18:30", end="2026-11-08T19:30",
         img="roma", alt="Largo di Torre Argentina, a pochi passi da via dei Barbieri"),
    dict(key="bologna", day="sabato", d="21", mon="novembre", time="16:45", city="Bologna",
         venue="L’Eredità delle Donne, Libreria Zanichelli", with_="nel programma del festival",
         maps="Libreria Zanichelli Bologna", start="2026-11-21T16:45", end="2026-11-21T17:30",
         img="bologna", alt="Piazza Galvani, su cui si affaccia la Libreria Zanichelli, con l’Archiginnasio"),
]

def ics(t):
    def z(s):
        dt = datetime.datetime.fromisoformat(s) - datetime.timedelta(hours=1)  # Roma in novembre: UTC+1
        return dt.strftime("%Y%m%dT%H%M%SZ")
    body = "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Tlon//La fabbrica della bellezza//IT", "BEGIN:VEVENT",
        f"UID:fabbricabellezza-{t['key']}@tlon.it", f"DTSTAMP:{z('2026-11-01T12:00')}",
        f"DTSTART:{z(t['start'])}", f"DTEND:{z(t['end'])}",
        f"SUMMARY:Maura Gancitano presenta La fabbrica della bellezza, {t['city']}",
        f"LOCATION:{t['venue']}, {t['city']}",
        "DESCRIPTION:Presentazione di La fabbrica della bellezza (Rizzoli). https://www.tlon.it/fabbricabellezza/",
        "URL:https://www.tlon.it/fabbricabellezza/", "END:VEVENT", "END:VCALENDAR"])
    return "data:text/calendar;charset=utf-8," + urllib.parse.quote(body)

def maps(q):
    return "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(q)

ROWS = "".join(f'''
    <li class="tappa posa" style="--i:{i%3}">
      <a class="tappa-foto" href="{maps(t['maps'])}" target="_blank" rel="noopener" aria-label="Indicazioni per {e(t['venue'])}, {t['city']}">{img(t['img'], t['alt'], sizes="(max-width:700px) 100vw, (max-width:1100px) 50vw, 33vw")}</a>
      <div class="tappa-testo">
        <p class="tappa-citta g">{e(t['city'])}</p>
        <p class="tappa-quando">{t['day'].capitalize()} {t['d']} {t['mon']}, ore {t['time']}</p>
        <p class="tappa-dove">{e(t['venue'])}</p>
        <p class="tappa-con">{e(t['with_'])}</p>
        <p class="tappa-azioni"><a class="link" href="{maps(t['maps'])}" target="_blank" rel="noopener">Indicazioni</a><a class="link" href="{ics(t)}" download="fabbrica-della-bellezza-{t['key']}.ics">Aggiungi al calendario</a></p>
      </div>
    </li>''' for i, t in enumerate(TAPPE))

# ---------- Le tavole ----------
def piena(base, alt, anno, cap, pos="50% 50%", sizes="100vw"):
    return (f'<figure class="piena"><div class="quadro">{img(base, alt, sizes=sizes, pos=pos)}</div>'
            f'<p class="anno g">{anno}</p><figcaption>{cap}</figcaption></figure>')

def tav(base, alt, cap, sizes="(max-width:900px) 100vw, 30vw"):
    return f'<figure class="tavola">{img(base, alt, sizes=sizes)}<figcaption>{cap}</figcaption></figure>'

def frase(testo, fonte):
    return f'<div class="citazione"><p class="dalibro">{testo}</p><p class="dalibro-fonte">{fonte}</p></div>'

NEL_LIBRO = ["Adobe Photoshop 1.0, 1990", "una cabina purikura a Tokyo", "il filtro Bold Glamour di TikTok",
    "Cindy Sherman, Untitled Film Still #21, 1978", "Francesca Woodman, Space², 1976", "Yoko Ono, Cut Piece, 1964",
    "Marina Abramović, Rhythm 0, 1974", "il New Look di Christian Dior, 1947", "ORLAN, Omniprésence, 1993",
    "la campagna Dove Real Beauty, 2004", "Trevor Paglen, Faces of ImageNet, 2022", "Shudu Gram, la prima top model digitale",
    "Lil Miquela", "Adam Harvey, CV Dazzle", "Zach Blas, Fag Face Mask, 2012", "il Dazzle Club a Soho, 2021",
    "Lygia Clark, Caminhando, 1963", "Marina Abramović, The Artist is Present, 2010", "Cézanne, La montagna Sainte-Victoire",
    "Pina Bausch, Kontakthof con donne e uomini over 65", "Steve Paxton e la Contact Improvisation",
    "una rudbeckia come la vede un’ape", "Silvia Giambrone, Mirror n.12"]
NEL_LIBRO_HTML = ", ".join(e(x) for x in NEL_LIBRO)

CREDITS = ('Le tavole fanno parte delle 169 immagini del libro e sono opere di dominio pubblico; la fotografia dello Spinario è del Metropolitan Museum of Art (CC0). '
           'Le fotografie delle città vengono da Wikimedia Commons: '
           '<a href="https://commons.wikimedia.org/wiki/File:Galleria_Vittorio_Emanuele_IIa.jpg">Galleria Vittorio Emanuele II</a> di Dave Cameron (<a href="https://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>), '
           '<a href="https://commons.wikimedia.org/wiki/File:Via_de%27_Cerretani_06.JPG">Via de’ Cerretani</a> di Freepenguin (<a href="https://creativecommons.org/licenses/by-sa/3.0">CC BY-SA 3.0</a>), '
           '<a href="https://commons.wikimedia.org/wiki/File:Pecci_ingresso.jpg">Centro Pecci</a> di Michela.osteri (<a href="https://creativecommons.org/licenses/by-sa/4.0">CC BY-SA 4.0</a>), '
           '<a href="https://commons.wikimedia.org/wiki/File:Ponte_del_Mare_di_Pescara_2011.jpg">Ponte del Mare</a> di Exephyo (<a href="https://creativecommons.org/licenses/by-sa/3.0">CC BY-SA 3.0</a>), '
           '<a href="https://commons.wikimedia.org/wiki/File:The_Largo_di_Torre_Argentina_is_a_historic_square_in_Rome.jpg">Largo di Torre Argentina</a> di Wilfredor (<a href="https://creativecommons.org/publicdomain/zero/1.0/deed.en">CC0</a>), '
           '<a href="https://commons.wikimedia.org/wiki/File:Piazza_galvani_bologna.JPG">Piazza Galvani</a> di Lorenzov79 (<a href="https://creativecommons.org/licenses/by-sa/4.0">CC BY-SA 4.0</a>). '
           'In copertina: Ewa Juszkiewicz, <em>Lady with a Mirror (after Elisabeth Vigée Le Brun)</em>, olio su tela, 170×120 cm, 2026; progetto grafico di Francesca Zucchi per Rizzoli. Caratteri Gloock ed Epilogue, licenza OFL.')

HTML = f'''<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>La fabbrica della bellezza, il libro di Maura Gancitano</title>
<meta name="description" content="La fabbrica della bellezza, il nuovo libro di Maura Gancitano (Rizzoli, dal 3 novembre 2026): l’invenzione del corpo perfetto dalla fotografia all’intelligenza artificiale, in 320 pagine e 169 immagini. Le presentazioni a Milano, Firenze, Prato, Pescara, Roma e Bologna.">
<link rel="canonical" href="https://www.tlon.it/fabbricabellezza/">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta name="theme-color" content="#15327a">
<meta property="og:type" content="book">
<meta property="og:site_name" content="Tlon">
<meta property="og:locale" content="it_IT">
<meta property="og:title" content="La fabbrica della bellezza, il libro di Maura Gancitano">
<meta property="og:description" content="L’invenzione del corpo perfetto dalla fotografia all’intelligenza artificiale. Rizzoli, in libreria dal 3 novembre 2026. Le presentazioni in sei città.">
<meta property="og:url" content="https://www.tlon.it/fabbricabellezza/">
<meta property="og:image" content="https://www.tlon.it/fabbricabellezza/img/og.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="La fabbrica della bellezza, il libro di Maura Gancitano">
<meta name="twitter:description" content="Rizzoli, dal 3 novembre 2026. Le presentazioni in sei città.">
<meta name="twitter:image" content="https://www.tlon.it/fabbricabellezza/img/og.jpg">
<link rel="preload" as="image" href="img/dipinto-1800.webp">
<link rel="preload" as="font" type="font/woff2" href="/assets/fonts/Gloock-400-normal-latin.woff2" crossorigin>
<link rel="stylesheet" href="/assets/fonts/fabbrica.css">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Book","name":"La fabbrica della bellezza. L'invenzione del corpo perfetto dalla fotografia all'intelligenza artificiale","author":{{"@type":"Person","name":"Maura Gancitano","url":"https://www.tlon.it/maura-gancitano/"}},"publisher":{{"@type":"Organization","name":"Rizzoli"}},"datePublished":"2026-11-03","isbn":"9788817197076","numberOfPages":320,"inLanguage":"it","image":"https://www.tlon.it/fabbricabellezza/img/copertina-1500.webp","url":"https://www.tlon.it/fabbricabellezza/"}}
</script>
<style>
/* Token: fabbricabellezza/MASTER.md */
:root{{
  --blu:#15327a; --blu-2:#0f2660; --blu-3:#1d3e92;
  --perla:#edece9; --perla-2:#c9c4d8; --arancio:#e2772c; --arancio-2:#c9651f; --inchiostro:#1a1612;
  --g:'Gloock',Didot,'Bodoni 72',Georgia,serif;
  --t:'Epilogue',-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;
  --pad:clamp(20px,4.5vw,72px);
  --s1:8px; --s2:16px; --s3:24px; --s4:40px; --s5:64px; --s6:96px; --s7:160px; --s8:240px;
  --posa:800ms; --breve:160ms; --expo:cubic-bezier(.16,1,.3,1);
}}
*,*::before,*::after{{box-sizing:border-box}}
html{{scroll-behavior:smooth;-webkit-text-size-adjust:100%;background:var(--blu)}}
body{{margin:0;background:var(--blu);color:var(--perla);font-family:var(--t);font-size:18px;line-height:1.55;font-weight:400}}
img{{display:block;max-width:100%;height:auto}}
a{{color:inherit}}
.g,h1,h2,h3{{font-family:var(--g);font-weight:400;letter-spacing:-.02em;margin:0;text-wrap:balance}}
p,figcaption{{margin:0;text-wrap:pretty}}
::selection{{background:var(--arancio);color:var(--inchiostro)}}
:focus-visible{{outline:3px solid var(--arancio);outline-offset:4px}}
[hidden]{{display:none!important}}
.skip{{position:absolute;left:-999px;top:8px;background:var(--perla);color:var(--blu);padding:8px 14px}}
.skip:focus{{left:8px;z-index:200}}
.pad{{padding-inline:var(--pad)}}

/* barra */
.barra{{display:flex;justify-content:space-between;align-items:baseline;padding:var(--s3) var(--pad) 0;position:absolute;left:0;right:0;top:0;z-index:5}}
.wordmark{{font-family:var(--g);font-size:32px;line-height:1;text-decoration:none}}
.barra nav{{display:flex;gap:var(--s3);font-size:16px}}
.barra nav a{{text-decoration:none}}
@media(hover:hover){{.barra nav a:hover{{text-decoration:underline;text-underline-offset:.3em}}}}

/* apertura: il dipinto a tutto schermo */
.apertura{{position:relative;height:100svh;min-height:640px;overflow:hidden;isolation:isolate}}
.apertura .quadro{{position:absolute;inset:0 42% 0 0;z-index:0;overflow:hidden}}
.apertura .quadro img{{width:100%;height:100%;object-fit:cover;object-position:50% 18%;transform-origin:50% 30%}}
.apertura .quadro::after{{content:"";position:absolute;inset:0 0 0 auto;width:28%;background:var(--blu);opacity:.0}}
.apertura .velo{{position:absolute;inset:auto 42% 0 0;height:58%;z-index:1;background:var(--blu);opacity:.72;mask-image:linear-gradient(to top,#000 40%,transparent)}} /* taste-skill-ignore: scrim neutro sotto il titolo */
.apertura .testo{{position:absolute;left:var(--pad);right:var(--pad);bottom:var(--s5);z-index:2}}
.apertura .autrice-nome{{font-size:20px;margin-bottom:var(--s2)}}
.apertura h1{{font-size:clamp(64px,12vw,173px);line-height:.86;letter-spacing:-.025em;max-width:10ch}}
.apertura .sotto{{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:var(--s3) var(--s5);margin-top:var(--s4)}}
.apertura .sottotitolo{{font-size:20px;line-height:1.3;max-width:34ch;color:var(--perla)}}
.apertura .sottotitolo strong{{font-weight:600}}
.button{{display:inline-block;background:var(--arancio);color:var(--inchiostro);text-decoration:none;font-weight:600;font-size:18px;padding:18px 28px;transition:background-color var(--breve) ease,transform var(--breve) var(--expo);white-space:nowrap}}
.button:active{{transform:scale(.97)}}
.button.perla{{background:var(--perla);color:var(--blu)}}
@media(hover:hover){{.button:hover{{background:var(--arancio-2)}}.button.perla:hover{{background:#fff}}}}
.link{{text-decoration:underline;text-underline-offset:.25em;text-decoration-thickness:.07em;text-decoration-color:rgba(243,236,223,.4);transition:text-decoration-color var(--breve) ease}}
@media(hover:hover){{.link:hover{{text-decoration-color:currentColor}}}}

/* la frase */
.frase{{padding:var(--s7) var(--pad);display:grid;grid-template-columns:minmax(0,7fr) minmax(0,5fr);gap:var(--s4) var(--s6);align-items:end}}
.frase .grande{{font-size:clamp(40px,7vw,96px);line-height:.92;max-width:16ch;grid-row:1/3}}
.frase .seguito{{font-family:var(--g);font-size:28px;line-height:1.15;max-width:30ch;margin:0;color:var(--perla)}}
.frase .fonte{{font-size:16px;color:var(--perla-2);margin:0}}

/* il libro */
.libro{{padding:0 var(--pad) var(--s8);display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:var(--s5) var(--s6);align-items:start}}
.libro h2{{grid-column:1/-1;font-size:clamp(48px,7vw,96px);line-height:.92}}
.cifre{{display:grid;gap:var(--s4);position:sticky;top:var(--s5)}}
.cifra .g{{font-size:clamp(72px,9vw,96px);line-height:.85;display:block}}
.cifra-lab{{margin:var(--s2) 0 0;max-width:30ch;color:var(--perla-2)}}
.quarta p{{max-width:60ch;margin-bottom:1.1em}}
.quarta p:first-child{{font-size:24px;line-height:1.35;font-weight:500}}
.quarta .button{{margin-top:var(--s3)}}

/* indice */
.indice{{padding:0 var(--pad) var(--s8)}}
.indice h2{{font-size:clamp(48px,7vw,96px);line-height:.92;margin-bottom:var(--s5)}}
.parte{{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:var(--s3) var(--s6);padding:var(--s5) 0}}
.parte+.parte{{padding-top:0}}
.parte h3{{font-size:32px;line-height:1.05;color:var(--perla-2);max-width:18ch}}
.parte ol{{list-style:none;margin:0;padding:0}}
.parte li{{padding:var(--s2) 0 var(--s3)}}
.parte li .g{{display:block;font-size:clamp(28px,3vw,40px);line-height:1;transition:transform 400ms var(--expo)}}
.parte li span:last-child{{display:block;margin-top:6px;color:var(--perla-2)}}
@media(hover:hover){{.parte li:hover .g{{transform:translateX(12px)}}}}

/* le tavole: cinema */
.tavole .testa{{padding:0 var(--pad);display:grid;grid-template-columns:minmax(0,7fr) minmax(0,5fr);gap:var(--s4) var(--s6);align-items:end;margin-bottom:var(--s6)}}
.tavole h2{{font-size:clamp(48px,7vw,96px);line-height:.92}}
.tavole .intro{{max-width:44ch;color:var(--perla-2);font-size:18px}}
.piena{{position:relative;margin:0;height:118svh;min-height:620px;overflow:hidden;isolation:isolate}}
.piena .quadro{{position:absolute;inset:0;overflow:hidden}}
.piena .quadro img{{width:100%;height:100%;object-fit:cover;transform-origin:50% 50%}}
.piena .anno{{position:absolute;left:calc(var(--pad) - .04em);bottom:.05em;font-size:clamp(120px,24vw,346px);line-height:.92;letter-spacing:-.045em;color:var(--perla);z-index:2}}
.piena figcaption{{position:absolute;right:var(--pad);bottom:var(--s4);max-width:34ch;font-size:16px;color:var(--perla);z-index:2;background:var(--blu);padding:14px 18px}}
.capitolo{{padding:var(--s7) var(--pad);display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:var(--s4) var(--s3);align-items:start}}
.dalibro{{font-family:var(--g);font-size:28px;line-height:1.15;letter-spacing:-.01em;max-width:30ch}}
.dalibro-fonte{{font-size:16px;color:var(--perla-2);margin-top:var(--s2)}}
.citazione{{display:grid;gap:0}}
.tavola{{margin:0}}
.tavola img{{width:100%;height:auto;background:var(--blu-2)}}
.tavola figcaption{{font-size:16px;color:var(--perla-2);margin-top:var(--s2);max-width:40ch}}
.c-1839 .t1{{grid-column:1/8}} .c-1839 .t2{{grid-column:8/13;margin-top:var(--s6)}} .c-1839 .t3{{grid-column:1/4}} .c-1839 .citazione{{grid-column:5/12;align-self:end}}
.c-1862 .t1{{grid-column:1/6}} .c-1862 .citazione{{grid-column:7/13;align-self:end}}
.c-1864 .t1{{grid-column:1/5}} .c-1864 .t2{{grid-column:5/9;margin-top:var(--s6)}} .c-1864 .t3{{grid-column:9/13;margin-top:var(--s4)}}
.c-1884 .t1{{grid-column:1/7}} .c-1884 .t2{{grid-column:7/10;margin-top:var(--s6)}} .c-1884 .t3{{grid-column:10/13;margin-top:var(--s3)}} .c-1884 .citazione{{grid-column:1/7;align-self:end}} .c-1884 .t4{{grid-column:7/13}}
.c-1893 .t1{{grid-column:1/4}} .c-1893 .t2{{grid-column:4/7;margin-top:var(--s6)}} .c-1893 .t3{{grid-column:7/13}} .c-1893 .citazione{{grid-column:1/7;align-self:end}} .c-1893 .t4{{grid-column:7/13}}
.c-1500 .t1{{grid-column:1/4}} .c-1500 .citazione{{grid-column:5/13;align-self:end}}
.nellibro{{padding:0 var(--pad) var(--s8);max-width:68ch}}
.nellibro h3{{font-size:32px;line-height:1.05;margin-bottom:var(--s3)}}
.nellibro p{{font-size:18px;line-height:1.5;color:var(--perla-2)}}
.nellibro p em{{color:var(--perla);font-style:normal}}

/* le tappe: le sedi come immagini, nel blu della pagina, a colori quando ci si posa sopra */
.tappe{{padding:0 var(--pad) var(--s8)}}
.tappe h2{{font-size:clamp(48px,7vw,96px);line-height:.92;margin-bottom:var(--s5)}}
.tappe-lista{{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:var(--s6) var(--s4);align-items:start}}
.tappa-foto{{display:block;aspect-ratio:3/2;overflow:hidden;background:var(--blu-2)}}
.tappa-foto img{{width:100%;height:100%;object-fit:cover;display:block;filter:grayscale(1) sepia(1) hue-rotate(190deg) saturate(1.3) brightness(.92);transition:filter 700ms var(--expo),transform 1200ms var(--expo)}}
.tappa-testo{{padding-top:var(--s3)}}
.tappa-testo p{{margin:0}}
.tappa-citta{{font-size:clamp(40px,4vw,56px);line-height:.9;transition:transform 400ms var(--expo)}}
.tappa-quando{{margin-top:var(--s3);font-size:18px;font-weight:600;line-height:1.3}}
.tappa-dove{{margin-top:var(--s2);font-size:18px}}
.tappa-con{{color:var(--perla-2);font-size:18px}}
.tappa-azioni{{margin-top:var(--s3);display:flex;flex-wrap:wrap;gap:var(--s2) var(--s3);font-size:18px}}
@media(hover:hover){{
  .tappa:hover .tappa-foto img{{filter:none;transform:scale(1.04)}}
  .tappa:hover .tappa-citta{{transform:translateX(12px)}}
}}
.tappa-extra{{grid-column:1/-1;max-width:60ch;padding-top:var(--s3);font-size:20px;line-height:1.45}}
.tappa-extra p{{margin:0}}
.tappe-nota{{margin-top:var(--s6);font-size:16px;color:var(--perla-2)}}

/* l'autrice */
.autrice{{padding:0 var(--pad) var(--s8);display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:var(--s5) var(--s6);align-items:end}}
.autrice figure{{margin:0;overflow:hidden}}
.autrice figure img{{width:100%;height:auto}}
.autrice h2{{font-size:clamp(48px,7vw,96px);line-height:.92;margin-bottom:var(--s4)}}
.autrice p{{max-width:54ch;margin-bottom:1.1em}}
.autrice p strong{{font-weight:600}}
.autrice blockquote{{margin:var(--s5) 0 0;font-family:var(--g);font-size:28px;line-height:1.15;max-width:34ch}}
.autrice .fonte{{font-size:16px;color:var(--perla-2);margin-top:var(--s2)}}

/* la chiusura */
.chiusura{{padding:var(--s7) var(--pad);background:var(--blu-2);display:grid;grid-template-columns:minmax(0,5fr) minmax(0,3fr) minmax(0,4fr);gap:var(--s5) var(--s6);align-items:end}}
.chiusura blockquote{{margin:0;font-family:var(--g);font-size:clamp(24px,2.2vw,32px);line-height:1.2;letter-spacing:-.01em;max-width:22ch}}
.chiusura .fonte{{margin-top:var(--s3);font-size:16px;color:var(--perla-2);max-width:48ch}}
.chiusura h2{{font-size:clamp(40px,3.9vw,56px);line-height:.95;margin-bottom:var(--s3)}}
.chiusura p{{max-width:38ch;margin-bottom:var(--s4)}}
.chiusura .oggetto{{margin:0}} .chiusura .oggetto img{{display:block;width:100%;height:auto;max-width:360px}}

/* piede */
footer{{padding:var(--s6) var(--pad) var(--s4);display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:var(--s5)}}
.menu{{list-style:none;margin:var(--s4) 0 0;padding:0}}
.menu li{{margin-bottom:var(--s2)}}
.menu a{{font-family:var(--g);font-size:32px;line-height:1;text-decoration:none;display:inline-block;transition:transform 300ms var(--expo),opacity 300ms ease}}
@media(hover:hover){{.menu:hover a{{opacity:.5}}.menu a:hover{{opacity:1;transform:translateX(10px)}}}}
.contatti{{display:grid;grid-template-columns:1fr 1fr;gap:var(--s3);margin-top:var(--s5);font-size:16px}}
.contatti p{{margin-bottom:6px}} .contatti a{{text-decoration:none}}
@media(hover:hover){{.contatti a:hover{{text-decoration:underline}}}}
.crediti{{font-size:16px;line-height:1.5;color:var(--perla-2);max-width:70ch}} .crediti a{{color:inherit}}
.legale{{font-size:16px;color:var(--perla-2);margin-top:var(--s3)}}

/* movimento: entrate una volta sola, cinema legato allo scorrimento */
.posa{{--dy:24px}}
.js .posa{{opacity:0;transform:translateY(var(--dy));transition:opacity var(--posa) var(--expo),transform var(--posa) var(--expo);transition-delay:calc(var(--i,0)*90ms)}}
.js .posa.in{{opacity:1;transform:none}}
@supports (animation-timeline: scroll()){{
  @media(prefers-reduced-motion:no-preference){{
    .apertura .quadro img{{animation:avvicina linear both;animation-timeline:scroll(root);animation-range:0 100svh}}
    @keyframes avvicina{{from{{transform:scale(1)}}to{{transform:scale(1.16)}}}}
    .piena .quadro img{{animation:assesta linear both;animation-timeline:view();animation-range:entry 0% cover 55%}}
    @keyframes assesta{{from{{transform:scale(1.14)}}to{{transform:scale(1)}}}}
    .piena .anno{{animation:sale linear both;animation-timeline:view();animation-range:entry 20% cover 50%}}
    @keyframes sale{{from{{transform:translateY(.35em)}}to{{transform:none}}}}
    .frase p{{animation:inchiostro linear both;animation-timeline:view();animation-range:entry 30% cover 45%}}
    @keyframes inchiostro{{from{{opacity:.28}}to{{opacity:1}}}}
    .capitolo .tavola{{animation:deriva linear both;animation-timeline:view();animation-range:entry 0% exit 100%}}
    .capitolo .t2{{--deriva:-56px}} .capitolo .t3{{--deriva:-28px}} .capitolo .t1,.capitolo .t4{{--deriva:0px}}
    @keyframes deriva{{from{{transform:translateY(calc(var(--deriva,0px)*-1))}}to{{transform:translateY(var(--deriva,0px))}}}}
  }}
}}
@media(prefers-reduced-motion:reduce){{
  .js .posa{{opacity:1;transform:none;transition:none}}
  *,*::before,*::after{{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}
}}

/* telefono e tablet */
@media(max-width:1100px){{
  .tappe-lista{{grid-template-columns:repeat(2,minmax(0,1fr))}}
}}
@media(max-width:900px){{
  .barra nav a:not(:last-child){{display:none}}
  .apertura{{min-height:0;height:100svh}}
  .apertura .quadro{{inset:0}}
  .apertura .velo{{inset:auto 0 0 0}}
  .apertura .quadro img{{object-position:50% 12%}}
  .apertura .velo{{height:70%}}
  .apertura .testo{{bottom:var(--s4)}}
  .apertura h1{{font-size:clamp(44px,12.5vw,72px);letter-spacing:-.03em}}
  .apertura .sottotitolo{{font-size:18px}}
  .frase{{padding:var(--s7) var(--pad) var(--s6)}}
  .frase{{grid-template-columns:1fr;padding:var(--s6) var(--pad)}}
  .frase .grande{{font-size:clamp(36px,10vw,48px);grid-row:auto}}
  .parte h3{{font-size:26px}}
  .frase .seguito{{font-size:22px}}
  .dalibro{{font-size:22px}}
  .libro,.autrice,.chiusura,footer,.parte{{grid-template-columns:1fr}}
  .libro,.indice,.tappe,.autrice,.nellibro{{padding-bottom:var(--s7)}}
  .cifre{{position:static;grid-template-columns:1fr 1fr}}
  .cifra .g{{font-size:72px}}
  .quarta p:first-child{{font-size:21px}}
  .piena{{height:78svh;min-height:420px}}
  .piena .anno{{font-size:clamp(96px,26vw,150px);left:var(--pad);bottom:0}}
  .piena figcaption{{left:var(--pad);right:var(--pad);top:var(--s3);bottom:auto;max-width:none}}
  .capitolo{{padding:var(--s6) var(--pad);display:flex;flex-direction:column;gap:var(--s5)}}
  .capitolo .tavola,.capitolo .citazione{{margin-top:0!important}}
  .tappe-lista{{grid-template-columns:1fr;gap:var(--s5)}}
  .tappa-citta{{font-size:40px}}
  .chiusura .oggetto img{{max-width:220px}}
  .tavole .testa{{grid-template-columns:1fr}}
  .tappe-nota{{margin-top:var(--s4)}}
  .chiusura{{padding:var(--s6) var(--pad)}}
  .chiusura>div:last-child{{order:-1}}
}}
@media print{{.barra{{display:none}}.piena{{height:auto}}}}
</style>
</head>
<body>
<a class="skip" href="#libro">Vai al contenuto</a>

<header class="apertura" id="inizio">
  <div class="barra"><a class="wordmark" href="https://www.tlon.it/">tlon</a><nav aria-label="Sezioni"><a href="#libro">Il libro</a><a href="#tavole">Le immagini</a><a href="#autrice">L’autrice</a><a href="#tappe">Le tappe</a><a href="{SHOP}">Prenota</a></nav></div>
  <div class="quadro">{img("dipinto", "Il dipinto della copertina, Lady with a Mirror di Ewa Juszkiewicz: una donna con turbante azzurro e fascia arancione sugli occhi, perle al collo, uno specchio in mano", lazy=False, sizes="100vw")}</div>
  <div class="velo" aria-hidden="true"></div>
  <div class="testo">
    <p class="autrice-nome posa" style="--i:0">Maura Gancitano</p>
    <h1 class="posa" style="--i:1">La fabbrica<br>della bellezza</h1>
    <div class="sotto">
      <p class="sottotitolo posa" style="--i:2">L’invenzione del corpo perfetto dalla fotografia all’intelligenza artificiale. <strong>Rizzoli, in libreria dal 3 novembre 2026.</strong></p>
      <a class="button posa" style="--i:3" href="{SHOP}">Prenota la copia autografata</a>
    </div>
  </div>
</header>

<section class="frase" aria-label="Dall’introduzione">
  <p class="g grande">La fotografia ha cambiato tutto,</p>
  <p class="seguito">e ciò che è venuto dopo la fotografia ha cambiato tutto ancora una volta.</p>
  <p class="fonte">Maura Gancitano, dall’introduzione <em>Quando abbiamo smesso di riconoscerci</em></p>
</section>

<section class="libro" id="libro">
  <h2 class="posa">Il libro</h2>
  <div class="cifre">
    <div class="cifra posa" style="--i:1"><p class="g">169</p><p class="cifra-lab">immagini, dal primo dagherrotipo del 1838 ai filtri e alle modelle generate dall’intelligenza artificiale</p></div>
    <div class="cifra posa" style="--i:2"><p class="g">12</p><p class="cifra-lab">capitoli in tre parti: come l’immagine è diventata più vera del corpo, perché sapere non basta, le bellezze che sfuggono</p></div>
    <div class="cifra posa" style="--i:3"><p class="g">320</p><p class="cifra-lab">pagine, Rizzoli, collana Saggi italiani, 25 euro</p></div>
  </div>
  <div class="quarta">
    <p class="posa" style="--i:1">Quasi duecento anni fa nessuno viveva così, perché nessuno aveva mai visto il proprio volto fissato dalla luce su una superficie, e dunque permanente, giudicabile e confrontabile con quello di chiunque altro.</p>
    <p class="posa" style="--i:2">Nessun essere umano nella storia è stato così tanto fotografato e costretto a vedersi, allo specchio, nei selfie, nei quadratini delle videocall, come accade a noi. «Ma io sono davvero questo insieme di elementi che vedo impressi in una foto?», ci chiediamo sempre prima e sempre più spesso. Questa frattura tra il nostro corpo e la sua rappresentazione è la condizione strutturale dell’esperienza moderna della bellezza.</p>
    <p class="posa" style="--i:3">Dall’invenzione della fotografia, che ha fissato i volti su una pellicola e li ha resi confrontabili, fino a oggi, l’immagine è diventata via via più vera del corpo, e ci ha fatto credere di doverci conformare a un certo ideale per corrispondere a una sua versione ogni volta più perfetta. La bellezza si è trasformata in un dispositivo di potere che ci sorveglia, ci misura, ci giudica secondo criteri che non abbiamo scelto, e questa sorveglianza si è installata in noi, come uno specchio che ci portiamo dentro.</p>
    <p class="posa" style="--i:4">Maura Gancitano racconta la storia del rapporto tra corpo e immagine dagli inizi dell’Ottocento a oggi, per comprendere il modo in cui la fotografia, la pubblicità, la moda, il cinema, la statistica, i social, i media digitali e in ultimo l’intelligenza artificiale ci abbiano cambiati, inventando corpi sempre più perfetti e sempre meno reali. Ma se è vero che non possiamo più vederci e vedere senza i filtri, possiamo però imparare a riconoscerli e a muoverci al loro interno, per liberarci dal mito della bellezza perfetta: cercando nuovi modi di apparire e di esistere in relazione con gli altri, abitando il corpo che abbiamo, sentendolo dall’interno, qui e ora, con tutto ciò che porta scritto su di sé.</p>
    <p class="posa" style="--i:5">Quattro anni dopo <em>Specchio delle mie brame</em>, Premio Rapallo, Maura Gancitano torna sulla bellezza e ne ricostruisce la fabbrica. <a class="button" href="{SHOP}">Prenota la copia autografata</a></p>
  </div>
</section>

<section class="indice" aria-labelledby="indice-titolo">
  <h2 id="indice-titolo" class="posa">Indice</h2>
  <div class="parte posa">
    <h3>Quando l’immagine diventò più vera del corpo</h3>
    <ol>
      <li><span class="g">Il terzo sguardo</span><span>La nascita della fotografia e l’oggettivazione del corpo</span></li>
      <li><span class="g">Misurare la bellezza</span><span>Normalizzazione statistica e controllo sociale</span></li>
      <li><span class="g">Tutti fotografabili</span><span>Democratizzazione, schedatura e controllo dell’immagine</span></li>
      <li><span class="g">Il corpo nell’epoca della riproducibilità</span><span>Fotografia di moda, pubblicità e la costruzione del perfetto impossibile</span></li>
    </ol>
  </div>
  <div class="parte posa">
    <h3>Perché sapere non basta</h3>
    <ol>
      <li><span class="g">Il corpo esposto</span><span>Televisione, diete e l’industria della magrezza</span></li>
      <li><span class="g">So che i filtri mentono (ma li uso lo stesso)</span><span>Il paradosso della consapevolezza</span></li>
      <li><span class="g">La tua immagine è più vera di te</span><span>Quando il corpo insegue l’immagine</span></li>
      <li><span class="g">Quando anche il rifiuto diventa un mercato</span><span>Corpi grassi, body positivity e modelle virtuali</span></li>
    </ol>
  </div>
  <div class="parte posa">
    <h3>Bellezze che sfuggono</h3>
    <ol>
      <li><span class="g">Corpi che si sottraggono</span><span>Riconoscimento facciale, maschere e diritto all’opacità</span></li>
      <li><span class="g">Ciò che non si lascia fotografare</span><span>La bellezza del gesto e del tempo vissuto</span></li>
      <li><span class="g">Abitare il corpo</span><span>Postura, danza e percezione del corpo dall’interno</span></li>
      <li><span class="g">Bellezze altre</span><span>Mondi animali, oltre l’Occidente, bellezze fuori norma</span></li>
    </ol>
  </div>
</section>

<section class="tavole" id="tavole">
  <div class="testa"><h2 class="posa">Le immagini<br>del libro</h2>
  <p class="intro posa" style="--i:1">Centosessantanove immagini accompagnano il racconto. Queste sono alcune di quelle ormai di dominio pubblico, nell’ordine in cui il libro le incontra.</p></div>

  {piena("boulevard-du-temple-1838", "Il Boulevard du Temple a Parigi fotografato da Daguerre: la strada appare deserta, due figure ferme in basso a sinistra", "1838", "Il primo dagherrotipo: Louis Daguerre, <em>Boulevard du Temple</em>, 1838.", pos="50% 40%")}
  <div class="capitolo c-1839">
    {frase("«Due sconosciuti dei quali non sapremo mai il nome, immortalati per caso perché erano rimasti fermi mentre il resto del mondo si muoveva, sono stati i primi esseri umani mai fotografati.»", "Dal primo capitolo, <em>Il terzo sguardo</em>")}
    <div class="t1">{tav("arago-1839", "Incisione: François Arago parla davanti all’Accademia delle scienze gremita", "François Arago annuncia la scoperta di Jacques Daguerre, 1839.")}</div>
    <div class="t2">{tav("daguerreotypomanie-1839", "Caricatura con folle che corrono a farsi fotografare, mongolfiere e cavalletti", "Théodore Maurisset, <em>La Daguerréotypomanie</em>, 1839.")}</div>
    <div class="t3">{tav("figurini-1839", "Tavola di moda con otto acconciature femminili dell’epoca", "Figurini di moda femminile, 1839.")}</div>
  </div>

  {piena("berthe-1862", "Sei pose della stessa donna in abito scuro accanto a una statua, su una lastra per carte de visite", "1862", "André-Adolphe-Eugène Disdéri, <em>Berthe</em>, 1862, carte de visite.", pos="50% 30%")}
  <div class="capitolo c-1862">
    <div class="t1">{tav("lobkowitz-1858", "Sei pose di un uomo in redingote, in piedi e seduto, sulla stessa lastra", "André-Adolphe-Eugène Disdéri, <em>Prince Lobkowitz</em>, 1858, carte de visite.", sizes="(max-width:900px) 100vw, 40vw")}</div>
    {frase("«Il proprio volto diventava qualcosa che si poteva tenere in mano, mostrare ad altri, conservare in un cassetto. Qualcosa da tirare fuori anni dopo e confrontare con la propria faccia ormai invecchiata.»", "Dall’introduzione")}
  </div>

  <div class="capitolo c-1864">
    <div class="t1">{tav("bernhardt-1864", "Ritratto fotografico di Sarah Bernhardt giovane, in abito bianco di pizzo", "Nadar, <em>Madame Sarah Bernhardt</em>, 1864 circa.")}</div>
    <div class="t2">{tav("karr-1877", "Ritratto di spalle di un uomo con mantello drappeggiato, il volto di profilo", "Samuel Adam-Salomon, <em>Alphonse Karr</em>, 1877 circa.")}</div>
    <div class="t3">{tav("isenring-1860", "Dagherrotipo ovale colorato a mano di un giovane uomo seduto", "Johann Baptist Isenring, dagherrotipo colorato a mano, 1860 circa.")}</div>
  </div>

  {piena("bertillon-orecchie-1894", "Tavola di orecchie fotografate e classificate per forma", "1894", "Sistema antropometrico di Bertillon: forme comparative dell’orecchio, 1894.", pos="50% 50%")}
  <div class="capitolo c-1884">
    <div class="t1">{tav("quetelet", "Diagramma a campana con la popolazione media, tra «nain» e «géant»", "Diagramma tratto da Adolphe Quetelet, <em>Anthropométrie</em>.", sizes="(max-width:900px) 100vw, 50vw")}</div>
    <div class="t2">{tav("galton-compositi", "Frontespizio con specimen di ritratti compositi: famiglia, salute, malattia, criminalità", "Francis Galton, ritratti compositi dal frontespizio di <em>Inquiries into Human Faculty</em>.", sizes="(max-width:900px) 100vw, 25vw")}</div>
    <div class="t3">{tav("galton-criminali", "Tavola di volti sovrapposti ottenuti da fotografie segnaletiche", "Francis Galton, ritratto composito da fotografie di criminali.", sizes="(max-width:900px) 100vw, 25vw")}</div>
    {frase("«Non sapeva niente dell’uomo medio di Quetelet, né dei ritratti compositi di Galton, né del fatto che la taglia dei suoi jeans discendeva da un corpo astratto mai esistito.»", "Dalle conclusioni")}
    <div class="t4">{tav("cartellino-segnaletico", "Cartellino segnaletico con due fotografie, di fronte e di profilo, e misure antropometriche", "Cartellino con fotografia segnaletica e dati antropometrici di un ricercato.", sizes="(max-width:900px) 100vw, 50vw")}</div>
  </div>

  {piena("grande-magazzino", "Illustrazione a colori dell’interno di un grande magazzino ottocentesco affollato di clienti", "1893", "Illustrazione a colori di uno dei primi grandi magazzini di New York.", pos="50% 50%")}
  <div class="capitolo c-1893">
    <div class="t1">{tav("kodak-1893", "Pubblicità Kodak: «The Camera that takes the World!»", "Pubblicità della Kodak su «The Illustrated London News», 16 settembre 1893.", sizes="(max-width:900px) 100vw, 25vw")}</div>
    <div class="t2">{tav("kodak-natale", "Illustrazione a colori: una famiglia apre una Kodak sotto l’albero di Natale", "Pubblicità natalizia della Kodak, illustrazione di Edward Penfield.", sizes="(max-width:900px) 100vw, 25vw")}</div>
    <div class="t3">{tav("cheret-jardin-de-paris", "Manifesto colorato di Jules Chéret per il Jardin de Paris, con una ballerina che danza", "Manifesto di Jules Chéret per il Jardin de Paris.", sizes="(max-width:900px) 100vw, 50vw")}</div>
    {frase("Tutti fotografabili, e tutti davanti a un modello: con la Kodak la macchina entra in casa, con i manifesti e i grandi magazzini il corpo da imitare entra per strada.", "I capitoli <em>Tutti fotografabili</em> e <em>Il corpo nell’epoca della riproducibilità</em>")}
  </div>

  {piena("bosch-superbia-1500", "Dettaglio della Superbia di Bosch: una donna di spalle si specchia in uno specchio retto da un demone", "1500", "Hieronymus Bosch, <em>Tavola dei sette peccati capitali</em>, dettaglio della Superbia, 1500 circa.", pos="50% 35%")}
  <div class="capitolo c-1500">
    <div class="t1">{tav("spinario", "Statuetta di bronzo di un ragazzo seduto che si toglie una spina dal piede", "Lo Spinario, fine XV secolo, New York, The Metropolitan Museum of Art.", sizes="(max-width:900px) 70vw, 25vw")}</div>
    {frase("L’ultima parte del libro va a cercare le bellezze che sfuggono: il gesto, il tempo vissuto, il corpo sentito dall’interno. Lo specchio della copertina è già in mano alla Superbia di Bosch, cinque secoli fa.", "La terza parte, <em>Bellezze che sfuggono</em>")}
  </div>

  <div class="nellibro posa">
    <h3>Nel libro, e non in questa pagina</h3>
    <p>Le immagini del Novecento e di oggi restano tra le pagine, per i diritti che le proteggono: <em>{NEL_LIBRO_HTML}</em>.</p>
  </div>
</section>

<section class="tappe" id="tappe">
  <h2 class="posa">Le tappe</h2>
  <ul class="tappe-lista">{ROWS}
    <li class="tappa-extra posa">
      <p>A Roma, in dicembre, un party letterario alla Libreria Teatro Tlon, a Ostiense, nei giorni di Più Libri Più Liberi, dal 4 all’8 dicembre. La data arriva qui appena è fissata.</p>
    </li>
  </ul>
  <p class="tappe-nota">La fotografia di ogni sede porta alle indicazioni stradali. Per informazioni sulle singole presentazioni: <a class="link" href="mailto:eventi@tlon.it">eventi@tlon.it</a></p>
</section>

<section class="autrice" id="autrice">
  <figure class="posa">{img("maura", "Maura Gancitano, ritratto", sizes="(max-width:900px) 100vw, 40vw")}</figure>
  <div>
    <h2 class="posa">L’autrice</h2>
    <p class="posa" style="--i:1"><strong>Maura Gancitano</strong> è filosofa, pedagogista e scrittrice. Nel 2015 ha fondato Tlon insieme ad Andrea Colamedici. È direttrice filosofica del Festival del Pensare Contemporaneo, insegna allo IED di Roma ed è editorialista di Vanity Fair.</p>
    <p class="posa" style="--i:2">I suoi libri sono tradotti in nove lingue. Con <em>Specchio delle mie brame. La prigione della bellezza</em> (Einaudi 2022) ha vinto il Premio Rapallo. Tra i più recenti: <em>Erotica dei sentimenti</em> (Einaudi 2024), <em>Animali narrativi</em> (Marsilio 2026) e, con Andrea Colamedici, <em>Botanica della meraviglia</em> (HarperCollins 2025). <a class="link" href="https://www.tlon.it/maura-gancitano/">La sua pagina su tlon.it</a>.</p>
    <blockquote class="posa" style="--i:3">«Io credo che la tenerezza che proviamo davanti alle fotografie del passato sia una delle esperienze più istruttive che possiamo regalarci, perché è la prova che lo sguardo cambia, che è già cambiato una volta e che tra dieci anni guarderemo la faccia di oggi con la stessa sorpresa.»</blockquote>
    <p class="fonte posa" style="--i:4">Dalle conclusioni</p>
  </div>
</section>

<section class="chiusura" id="prenota">
  <div>
    <blockquote class="posa">Con la bellezza davanti a me cammino, con la bellezza dietro di me cammino, con la bellezza sopra di me cammino, con la bellezza tutto intorno a me cammino.</blockquote>
    <p class="fonte posa" style="--i:1">La preghiera tradizionale dei diné, con cui si chiude il libro: una bellezza in cui si cammina, invece di una da fissare in un’immagine.</p>
  </div>
  <figure class="oggetto posa" style="--i:1">{img("copertina", "La copertina del libro: Maura Gancitano, La fabbrica della bellezza, Rizzoli", sizes="(max-width:900px) 60vw, 25vw")}</figure>
  <div>
    <h2 class="posa">In libreria dal 3 novembre</h2>
    <p class="posa" style="--i:1">Le copie ordinate dalla Libreria Tlon arrivano autografate da Maura e partono il giorno dell’uscita. Il libro è in tutte le librerie dallo stesso giorno.</p>
    <p class="posa" style="--i:2"><a class="button perla" href="{SHOP}">Prenota la copia autografata</a></p>
  </div>
</section>

<footer>
  <div>
    <a class="wordmark" href="https://www.tlon.it/">tlon</a>
    <ul class="menu">
      <li><a href="#libro">Il libro</a></li>
      <li><a href="#tavole">Le immagini</a></li>
      <li><a href="#tappe">Le tappe</a></li>
      <li><a href="#autrice">L’autrice</a></li>
      <li><a href="https://www.tlon.it/maura-gancitano/">Maura Gancitano</a></li>
      <li><a href="https://www.tlon.it/">Tlon</a></li>
    </ul>
    <div class="contatti">
      <div><p><a href="mailto:eventi@tlon.it">eventi@tlon.it</a></p><p><a href="mailto:info@tlon.it">info@tlon.it</a></p></div>
      <div><p><a href="https://www.instagram.com/tlon.it/">Instagram</a></p><p><a href="https://www.facebook.com/associazionetlon">Facebook</a></p><p><a href="https://www.youtube.com/c/AssociazioneTlon">YouTube</a></p></div>
    </div>
  </div>
  <div>
    <p class="crediti">{CREDITS}</p>
    <p class="legale">© 2026 Tlon Srl. Sede legale: Via Nicolò da Pistoia 12, 00154 Roma. P.IVA 13583341006</p>
  </div>
</footer>

<script>
document.documentElement.classList.add('js');
(function(){{
  var els=document.querySelectorAll('.posa');
  if('IntersectionObserver' in window){{
    var io=new IntersectionObserver(function(es){{
      es.forEach(function(x){{ if(x.isIntersecting){{ x.target.classList.add('in'); io.unobserve(x.target); }} }});
    }},{{rootMargin:'0px 0px 12% 0px',threshold:0.01}});
    els.forEach(function(el){{ io.observe(el); }});
  }} else {{ els.forEach(function(el){{ el.classList.add('in'); }}); }}
  setTimeout(function(){{ els.forEach(function(el){{ el.classList.add('in'); }}); }},6000);
}})();
</script>
</body>
</html>
'''
OUT.write_text(HTML, encoding="utf-8")
print("scritto", OUT, len(HTML), "byte")
