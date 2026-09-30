#!/usr/bin/env python3
"""Generates the static jonzvi.com site into ../site from data.py."""
import html, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from data import PROJECTS, HOME
from icons import KEYBOARD, MOUSE, TOOLS, MONITOR, LINKEDIN, INSTAGRAM, MAIL

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DOMAIN = "https://jonzvi.com"
FONTS = ("https://fonts.googleapis.com/css2?family=Barlow:ital,wght@0,300;0,400;1,300"
         "&family=Barlow+Condensed:wght@500&family=Jost:wght@300&family=Varela+Round&display=swap")
manifest = {}  # local path -> source url

def e(s): return html.escape(s, quote=True)

def img(uri, w, prefix, alt="", cls="", width=None, height=None, lazy=True, fetch_hi=False):
    """Register an image for download and return an <img> tag."""
    h = re.match(r"[0-9a-f]+_([0-9a-f]{32})", uri).group(1)
    ext = uri.rsplit(".", 1)[1].lower()
    if ext == "gif":
        local = f"assets/img/{h}.gif"
        src = f"https://static.wixstatic.com/media/{uri}"
    else:
        local = f"assets/img/{h}-{w}.webp"
        src = f"https://static.wixstatic.com/media/{uri}/v1/fit/w_{w},h_{w*4},q_85/{h}.webp"
    manifest[local] = src
    a = [f'src="{prefix}{local}"', f'data-fallback="{src}"', f'alt="{e(alt)}"']
    if width and height: a += [f'width="{width}"', f'height="{height}"']
    if cls: a.append(f'class="{cls}"')
    a.append('loading="lazy" decoding="async"' if lazy else 'fetchpriority="high"' if fetch_hi else '')
    return "<img " + " ".join(x for x in a if x) + ">"

def head(title, desc, path, prefix, og_image=None, extra=""):
    url = DOMAIN + path
    og = f'\n  <meta property="og:image" content="{DOMAIN}/{og_image}">' if og_image else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc)}">
  <meta name="author" content="Jonathan Zvi Shmuely">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Jon Zvi">
  <meta property="og:title" content="{e(title)}">
  <meta property="og:description" content="{e(desc)}">
  <meta property="og:url" content="{url}">{og}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#4f4f4f">
  <link rel="icon" type="image/webp" href="{prefix}assets/img/favicon.webp">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="{FONTS}">
  <link rel="stylesheet" href="{prefix}assets/css/style.css">{extra}
</head>
"""

def header(prefix, active=None):
    home = prefix or "./"
    cur = ' aria-current="page"'
    subs = "\n".join(
        f'            <li><a href="{prefix}{p["slug"]}/"{cur if active == p["slug"] else ""}>{e(p.get("menu", p["title"]))}</a></li>'
        for p in PROJECTS)
    logo = img(HOME["logo"], 120, prefix, alt="Jon Zvi logo", width=53, height=37, lazy=False)
    return f"""<body>
  <a class="skip-link" href="#main">Skip to Main Content</a>
  <header class="site-header">
    <div class="inner">
      <a class="logo" href="{home}" aria-label="Jon Zvi — home">{logo}</a>
      <button class="menu-btn" aria-label="Menu" aria-expanded="false" aria-controls="site-nav"><span></span><span></span><span></span></button>
      <nav class="nav" id="site-nav" aria-label="Main">
        <ul>
          <li{' class="active"' if active == "home" else ""}><a href="{home}">Home</a></li>
          <li><a href="{prefix}#skills">Skills</a></li>
          <li class="has-sub{" active" if active not in (None, "home") else ""}">
            <button class="sub-toggle" aria-expanded="false" aria-haspopup="true">My Work</button>
            <ul class="submenu">
              <li><a href="{prefix}#work">All projects</a></li>
{subs}
            </ul>
          </li>
          <li><a href="{prefix}#about">About</a></li>
          <li><a href="{prefix}#contact">Contact</a></li>
        </ul>
      </nav>
    </div>
  </header>
"""

def footer(prefix):
    return f"""  <footer class="site-footer">
    <div class="social">
      <a href="https://www.linkedin.com/in/jzsdesign/" target="_blank" rel="noopener" aria-label="LinkedIn">{LINKEDIN}</a>
      <a href="https://www.instagram.com/shmuely/" target="_blank" rel="noopener" aria-label="Instagram">{INSTAGRAM}</a>
    </div>
    <p>© 2022 by Jonathan Zvi Shmuely.</p>
  </footer>
  <script src="{prefix}assets/js/script.js" defer></script>
</body>
</html>
"""

def paras(text):
    return "\n".join(f"          <p>{e(l.strip())}</p>" for l in text.split("\n") if l.strip())

# ------------------------------------------------------------------ home
def build_home():
    p = ""
    cards = []
    for i, pr in enumerate(PROJECTS):
        cards.append(f"""      <a class="work-card" href="{pr['slug']}/">
        {img(pr['thumb'], 1300, p, alt=pr['title'] + ' — ' + pr['sub'].split(chr(10))[0], width=638, height=358, lazy=i > 1)}
        <span class="overlay"><strong>{e(pr['title'])}</strong><span>{e(pr['sub'])}</span></span>
      </a>""")
    ld = {"@context": "https://schema.org", "@type": "Person", "name": "Jonathan Zvi Shmuely",
          "alternateName": "Jon Zvi", "jobTitle": "Industrial Designer", "url": DOMAIN + "/",
          "email": "mailto:jonzvis@gmail.com", "telephone": "+972548017178",
          "address": {"@type": "PostalAddress", "addressLocality": "Tel-Aviv", "addressCountry": "IL"},
          "alumniOf": "Shenkar College of Engineering and Design",
          "sameAs": ["https://www.linkedin.com/in/jonzvi/", "https://www.instagram.com/shmuely/"]}
    extra = '\n  <script type="application/ld+json">' + json.dumps(ld) + "</script>"
    hero_img = img(HOME["hero"], 2560, p, alt="A.O.K. outdoor kitchen grill and spork by Jon Zvi Shmuely", lazy=False, fetch_hi=True)
    manifest["assets/img/favicon.webp"] = f"https://static.wixstatic.com/media/{HOME['logo']}/v1/fit/w_64,h_64,q_90/favicon.webp"
    out = head("Jon Zvi Shmuely | Industrial Designer — Portfolio",
               "Product / Industrial Design portfolio of Jonathan Zvi Shmuely — industrial designer based in Tel-Aviv, Israel. 3D modeling, prototyping and 3D renders.",
               "/", p, og_image=f"assets/img/{re.search('_([0-9a-f]{32})', HOME['hero']).group(1)}-2560.webp", extra=extra)
    out += header(p, "home")
    out += f"""
  <main id="main">
    <section class="hero" aria-label="Intro">
      {hero_img}
      <div class="title">
        <h1>JON ZVI SHMUELY</h1>
        <p>INDUSTRIAL DESIGNER</p>
      </div>
    </section>

    <section class="section skills" id="skills">
      <h2 class="section-title">Design Skills</h2>
      <hr class="rule">
      <div class="skills-grid">
        <div class="skill">
          <div class="icon">{KEYBOARD.replace('<svg ', '<svg class="kb" ', 1)}{MOUSE.replace('<svg ', '<svg class="mouse" ', 1)}</div>
          <h3>3D MODELING</h3>
          <p>Solidworks, Rhino<br>&amp; Blender</p>
        </div>
        <div class="skill">
          <div class="icon">{TOOLS.replace('<svg ', '<svg class="tools" ', 1)}</div>
          <h3>PROTOTYPING</h3>
          <p>Mechanism development, 3D printing, ceramics mold design &amp; woodwork</p>
        </div>
        <div class="skill">
          <div class="icon">{MONITOR}</div>
          <h3>3D RENDERS</h3>
          <p>Keyshot, Blender, Photoshop &amp; AI tools (Open-AI, etc)</p>
        </div>
      </div>
    </section>

    <section class="section work" id="work">
      <h2 class="section-title">My Work</h2>
      <hr class="rule">
      <p class="lead">A collection of a few projects of mine</p>
      <div class="work-grid">
{chr(10).join(cards)}
      </div>
    </section>

    <section class="section about" id="about">
      <div class="card">
        <h2 class="section-title">About</h2>
        <hr class="rule">
        <div class="about-text">
          <p>I'm a 30-year-old Industrial / Product Designer, a graduate of Shenkar College of Engineering and Design (B.Des.), 2022.</p>
          <p>Born and raised in Tel-Aviv.</p>
          <p>-1year&nbsp; in a carpentry shop.</p>
          <p>-traveled around the world for 3 years, mostly hiking and camping.</p>
          <p>-1 year as a traveling security guard on organized tours throughout Israel.</p>
          <p>-3 years service in a combat unit that specialized in camouflage warfare.</p>
          <p>I am an internet <a href="https://www.macmillandictionary.com/dictionary/british/aficionado#aficionado__1" target="_blank" rel="noopener">aficionado</a> &amp; open source advocate.</p>
          <p class="quote">"Simplicity is the ultimate sophistication"<br>Leonardo da Vinci</p>
        </div>
        <div class="actions"><a class="btn" href="assets/files/Jon-Zvi-Shmuely-Resume.pdf" target="_blank" rel="noopener">View Resume</a></div>
      </div>
    </section>

    <div class="portrait">
      {img(HOME['portrait'], 1400, p, alt='Portrait of Jon Zvi Shmuely', width=662, height=450)}
    </div>

    <section class="section contact" id="contact">
      <div class="card">
        <h2 class="section-title">Contact Me</h2>
        <hr class="rule">
        <div class="contact-grid">
          <div class="socials">
            <h3>SOCIALS</h3>
            <ul>
              <li>{INSTAGRAM}<a href="https://www.instagram.com/shmuely/" target="_blank" rel="noopener">/shmuely/</a></li>
              <li>{LINKEDIN}<a href="https://www.linkedin.com/in/jonzvi/" target="_blank" rel="noopener">linkedin.com/in/jonzvi</a></li>
              <li>{MAIL}<a href="mailto:jonzvis@gmail.com">jonzvis@gmail.com</a></li>
            </ul>
            <div class="divider"></div>
            <address>Tel-Aviv, Israel<br><br><a href="tel:+972548017178">(+972)0548017178</a></address>
          </div>
          <form class="form" id="contact-form" action="https://api.web3forms.com/submit" method="POST">
            <input type="hidden" name="access_key" value="37b05d80-9bc0-4153-b39c-04d88c804dc6">
            <input type="hidden" name="from_name" value="jonzvi.com contact form">
            <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
            <div class="field"><label for="f-first">First Name</label><input id="f-first" name="first_name" type="text" autocomplete="given-name"></div>
            <div class="field"><label for="f-last">Last Name</label><input id="f-last" name="last_name" type="text" autocomplete="family-name"></div>
            <div class="field"><label for="f-email">Email *</label><input id="f-email" name="email" type="email" required autocomplete="email"></div>
            <div class="field"><label for="f-subject">Subject</label><input id="f-subject" name="subject" type="text"></div>
            <div class="field"><label for="f-msg">Message</label><textarea id="f-msg" name="message"></textarea></div>
            <button class="btn" type="submit">Submit</button>
            <p class="status" role="status" aria-live="polite"></p>
          </form>
        </div>
      </div>
      <a class="to-top" href="#main" aria-label="Back to top"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 15l7-7 7 7"/></svg></a>
    </section>
  </main>

"""
    out += footer(p)
    write("index.html", out)
    manifest["assets/files/Jon-Zvi-Shmuely-Resume.pdf"] = HOME["resume_src"]

# ------------------------------------------------------------------ projects
def build_project(i, pr):
    p = "../"
    narrow = pr["width"] <= 980
    maxw = 1920 if not narrow else 1600
    rows = []
    for row in pr["images"]:
        tags = [img(u, maxw if len(row) == 1 else 1200, p, alt=f"{pr['title']} — image {len(rows)+1}", width=w, height=h,
                    lazy=not (len(rows) == 0)) for (u, w, h) in row]
        rows.append('      <div class="row">' + "".join(tags) + "</div>")
    collage = ""
    if pr.get("collage"):
        figs = "".join(f'<figure class="c{k+1}">{img(u, 900, p, alt=t)}</figure>' for k, (u, t, w, h) in enumerate(pr["collage"]))
        collage = f'\n          <div class="collage" aria-label="Process images">{figs}</div>'
    prev_p = PROJECTS[i - 1]
    next_p = PROJECTS[(i + 1) % len(PROJECTS)]
    first_img = pr["images"][0][0][0]
    h = re.search("_([0-9a-f]{32})", first_img).group(1)
    og = f"assets/img/{h}-{maxw}.webp" if not first_img.endswith(".gif") else None
    out = head(f"{pr['title'].replace(chr(10), ' ')} | Jon Zvi Industrial Design", pr["meta_desc"], f"/{pr['slug']}/", p, og_image=og)
    out += header(p, pr["slug"])
    out += f"""
  <main id="main" class="project{' narrow' if narrow else ''}">
    <section class="project-head">
      <div class="left">
        <h1>{e(pr['title'])}</h1>
        <dl class="facts">
          <div><dt>For</dt><dd>{e(pr['for_'])}</dd></div>
          <div><dt>Location</dt><dd>{e(pr['loc'])}</dd></div>
          <div><dt>Year</dt><dd>{e(pr['year'])}</dd></div>
        </dl>{collage}
      </div>
      <div class="desc">
{paras(pr['text'])}
      </div>
    </section>
    <section class="gallery" aria-label="{e(pr['title'])} images">
{chr(10).join(rows)}
    </section>
    <nav class="project-nav" aria-label="More projects">
      <a href="../{prev_p['slug']}/">&larr; {e(prev_p.get('menu', prev_p['title']))}</a>
      <a href="../#work">All projects</a>
      <a href="../{next_p['slug']}/">{e(next_p.get('menu', next_p['title']))} &rarr;</a>
    </nav>
  </main>

"""
    out += footer(p)
    write(f"{pr['slug']}/index.html", out)

# ------------------------------------------------------------------ misc
def build_misc():
    redirects = {pr["old"]: "/" + pr["slug"] + "/" for pr in PROJECTS if pr["old"] != "/" + pr["slug"]}
    redirects.update({"/vélspresso": "/velspresso/"})
    out = head("Page not found | Jon Zvi", "The page you are looking for does not exist.", "/404.html", "/",
               extra="""
  <script>
    (function () {
      var map = """ + json.dumps(redirects, ensure_ascii=False) + """;
      var p = location.pathname.replace(/\\/$/, "");
      var d = map[p] || map[decodeURIComponent(p)] || map[p.toLowerCase()];
      if (!d && /^\\/[^\\/.]+$/.test(p)) d = p + "/";
      if (d && d !== location.pathname) location.replace(d + location.hash);
    })();
  </script>""")
    out += header("/", None)
    out += """
  <main id="main" class="notfound">
    <h1>404</h1>
    <p>Sorry, this page doesn't exist.</p>
    <p><a class="btn" href="/">Back to home</a></p>
  </main>

"""
    out += footer("/")
    write("404.html", out)
    write("CNAME", "jonzvi.com\n")
    write(".nojekyll", "")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n")
    urls = [DOMAIN + "/"] + [f"{DOMAIN}/{p['slug']}/" for p in PROJECTS]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    lines = [f"{k} {v}" for k, v in sorted(manifest.items())]
    write("assets/manifest.txt", "# local-path source-url  (used by .github/workflows/fetch-assets.yml)\n" + "\n".join(lines) + "\n")

def write(rel, content):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    build_home()
    for i, pr in enumerate(PROJECTS):
        build_project(i, pr)
    build_misc()
    print("pages:", 1 + len(PROJECTS), "assets:", len(manifest))
