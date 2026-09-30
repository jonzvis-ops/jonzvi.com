# jonzvi.com

Portfolio of Jonathan Zvi Shmuely, Industrial Designer. This is a plain HTML/CSS/JS site hosted for free on GitHub Pages. It was moved here from Wix.

## How it works
- `_src/data.py` holds every project's text and image list, `_src/build.py` builds the HTML pages from it, and `_src/icons.py` holds the icons.
- Changing anything in `_src/` starts the **Build site & copy images from Wix** workflow (Actions tab). It regenerates the pages (`index.html`, `<project>/index.html`, `404.html`, `sitemap.xml`, …), downloads any new images listed in `assets/manifest.txt`, and commits the result. The live site updates about a minute later.
- `assets/css/style.css` and `assets/js/script.js` are edited directly.
- `CNAME` sets the custom domain (jonzvi.com). `404.html` sends old Wix links (e.g. `/copy-of-go-pole`) to their new pages.

## Editing text
Open `_src/data.py` on GitHub, click the pencil icon, change the text, and click **Commit changes**.

## Contact form
The contact form uses [Web3Forms](https://web3forms.com) (free account under jonzvis@gmail.com); messages go to jonzvis@gmail.com.
