# DigiRP – Discord Rich Presence Státusz Beállító

A **DigiRP** egy Pythonban írt, grafikus felületű (GUI) alkalmazás, amellyel egyszerűen beállíthatod a **Discord Rich Presence** státuszodat – hasonlóan a *Custom RP*-hez.

## ✨ Funkciók

* Saját ablakos alkalmazás (nem konzolos)
* Discord Rich Presence (Details + State)
* Státusz törlése egy kattintással
* Modern, letisztult kinézet
* Stabil, működő megoldás

## 🖥️ Követelmények

* **Windows** (Linuxon is működhet, de nem garantált)
* **Python 3.10 – 3.13 ajánlott**

  * ⚠️ Python 3.14 még instabil lehet a `pypresence`-hez
* Futó **Discord kliens** (nem böngészős)

## 📦 Telepítés

1. Klónozd a repót vagy töltsd le ZIP-ben:

```bash
git clone https://github.com/DigiFan/DigiRP.git
```

2. Lépj be a mappába:

```bash
cd DigiRP
```

3. Telepítsd a szükséges csomagot:

```bash
pip install pypresence
```

## 🔑 Discord App ID létrehozása

1. Nyisd meg: [https://discord.com/developers/applications](https://discord.com/developers/applications)
2. **New Application**
3. Adj nevet (pl. DigiRP)
4. Másold ki a **Client ID**-t
5. Illeszd be a `rp.py` fájlba

```python
CLIENT_ID = "IDE_A_SAJÁT_CLIENT_ID"
```

## ▶️ Futtatás

```bash
python rp.py
```

Ha a Discord fut, a státusz azonnal megjelenik.

## 🧠 Gyakori hibák

### ❌ InvalidID (4000)

* Rossz vagy nem létező Client ID
* Nem fut a Discord kliens

### ❌ Nem jelenik meg a státusz

* Ellenőrizd, hogy **Rich Presence**-t nézed, nem sima státuszt

## 🚀 Tervezett funkciók

* Ikonok (large / small image)
* Menthető presetek
* Automatikus frissítés (időzítő)
* Dark mode

## 📜 Licenc

MIT License – szabadon módosítható és terjeszthető.

---

**Készítette:** Digi Fan
