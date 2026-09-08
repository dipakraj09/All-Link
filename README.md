# Dipak Kumar — Links Site

## Files
- `index.html` — page structure
- `style.css` — design, glow buttons, light/dark theme
- `script.js` — links.json ko load/render karta hai
- `links.json` — **yahan naya link add karte rehna hai**

## Naya link kaise add karein
`links.json` file kholiye aur is format mein ek naya block `{ }` add kar dijiye (comma laga kar):

```json
{
  "title": "Naye link ka naam",
  "shortLink": "bit.ly/xxxxx",
  "destination": "https://asli-website-ka-link.com/"
}
```

Poori file kuch aisi dikhegi:

```json
[
  { "title": "...", "shortLink": "...", "destination": "..." },
  { "title": "...", "shortLink": "...", "destination": "..." },
  { "title": "Naya link ka naam", "shortLink": "bit.ly/xxxxx", "destination": "https://..." }
]
```

Bas save kariye — website apne aap naya link dikha degi, HTML/CSS/JS mein kuch badalne ki zaroorat nahi.

## Vercel pe live kaise karein
1. In sabhi files (`index.html`, `style.css`, `script.js`, `links.json`) ko ek GitHub repo mein daal dijiye (ya seedha folder ko Vercel dashboard mein drag-drop kar dijiye — "Add New Project" → "Deploy" mein).
2. Vercel par **New Project** banaiye, repo select kariye.
3. Framework preset: **Other** rakhiye (kyunki ye plain HTML/CSS/JS hai).
4. **Deploy** dabaiye — bas, live ho jayegi.
5. Baad mein jab bhi naya link add karna ho, sirf `links.json` update karke GitHub pe push kar dijiye — Vercel apne aap redeploy kar dega.
