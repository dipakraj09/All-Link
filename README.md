# Dipak Kumar — Links Site

## Sabse aasan tarika (GUI)
1. Folder ko unzip karo.
2. `START.bat` double-click karo (ya `python links_manager.py`).
3. Window me:
   - **▶ Start** dabao -> site browser me khul jayegi (phone ka address bhi dikhega)
   - **Quick paste** me bitly + URL ek saath paste karo -> dono khud alag ho jayenge
   - **Add link** dabao -> `links.json` apne aap save. Kuch aur karne ki zaroorat nahi.
   - List me double-click = edit, Delete = hatao, ▲▼ = order badlo
   - **Copy Bitly / Copy URL** se seedha copy

## Files kaun si kya karti hai
- `index.html` — page ka structure
- `style.css` — design (dark/light theme)
- `script.js` — links.json padhkar cards banata hai
- `links.json` — saare links (GUI isi ko edit karta hai)
- `links_manager.py` — ye GUI app
- `START.bat` — GUI ko double-click se chalane ke liye

## Haath se JSON likhna ho to
Sirf `bitly` aur `url` zaroori hain. `title` optional.
```json
{ "bitly": "bit.ly/xxxxx", "url": "https://example.com/" }
```
Bitly nahi hai to `bitly` hata do.

## Vercel par live
Poora folder GitHub par daalo ya Vercel me drag-drop karo (Framework: Other).
`links_manager.py` aur `START.bat` site ke liye zaroori nahi, rakhne me koi dikkat nahi.
