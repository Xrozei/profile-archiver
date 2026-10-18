# Profile Archiver

**English** | [Türkçe](#türkçe)

A small dark-themed desktop app for Windows. Paste a profile link, press **Download**, and the photos, videos, reels, stories and highlights are saved to a folder. Built on [Instaloader](https://instaloader.github.io/). The app has a built-in **TR / EN** language switch and a **?** help button.

> Not affiliated with Instagram or Meta.

## Features

- Paste a link, press Download. No commands.
- Posts, videos, reels, stories and highlights (stories and highlights need a login)
- Downloading the same profile again fetches **only new content**
- Built-in **?** help explains step by step how to get the login codes
- Your session stays on your computer only; **Delete session** removes it

## Install

1. Download the latest **ProfileArchiver.exe** from the **Releases** section on the right.
2. Double-click it. If Windows shows "Windows protected your PC", click **More info**, then **Run anyway**.
3. Click the **?** button in the window and follow the login steps.

Some antivirus programs wrongly flag executables built from Python. The full source is in this repository, so you can build it yourself.

## Why a login?

Stories and highlights need a login, and without one Instagram blocks requests much more often (HTTP 429). Your password is never asked for. The app uses the `sessionid` and `csrftoken` cookies of the login already open in your browser. The **?** button explains how to find them.

## Safety

- `sessionid` works like a password. Never share it, screenshot it or commit it to GitHub.
- The cookies are stored only on your computer and sent only to Instagram.
- If possible, use a secondary account instead of your main one.

## Disclaimer

- Automated downloading may violate Instagram's Terms of Use and can get your account restricted. You use this tool at your own risk.
- Other people's photos and videos are protected by copyright. Only download **your own content** or content you have **permission** to download, and do not redistribute it without permission.
- The software is provided "as is", without warranty.

## For developers

```bash
pip install -r requirements.txt
python ig_gui.py
```

To build the Windows .exe: on GitHub go to **Actions → Build Windows exe → Run workflow**.
To publish a release, push a tag such as `v1.0`; the .exe is attached to **Releases** automatically.

License: MIT

---

## Türkçe

Windows için küçük, koyu temalı bir masaüstü programı. Profil linkini yapıştır, **İndir**'e bas; fotoğraflar, videolar, reels, story ve highlights bir klasöre iner. [Instaloader](https://instaloader.github.io/) üzerine kuruludur. Programın içinde **TR / EN** dil seçeneği ve **?** yardım düğmesi vardır.

> Instagram veya Meta ile bağlantılı değildir.

### Özellikler

- Linki yapıştır, İndir'e bas. Komut yazmak yok.
- Gönderiler, videolar, reels, story ve highlights (story ve highlights için giriş gerekir)
- Aynı profili tekrar indirince **sadece yeniler** iner
- **?** yardım düğmesi giriş kodlarının nasıl bulunacağını adım adım anlatır
- Oturum yalnızca senin bilgisayarında kalır; **Oturumu sil** ile silinir

### Kurulum

1. Sağdaki **Releases** bölümünden en son **ProfileArchiver.exe** dosyasını indir.
2. Çift tıkla. Windows "bilgisayarınızı korudu" uyarısı çıkarsa **Ek bilgi**, sonra **Yine de çalıştır**'a tıkla.
3. Penceredeki **?** düğmesine bas ve giriş adımlarını izle.

Bazı antivirüs programları Python'dan üretilen .exe dosyalarını yanlışlıkla şüpheli bulabilir. Kaynak kodun tamamı bu depoda, istersen kendin derleyebilirsin.

### Giriş neden gerekiyor?

Story ve highlights için giriş gerekir; girişsiz kullanımda Instagram çok daha sık engeller (429 hatası). Şifren istenmez. Tarayıcında açık olan girişin `sessionid` ve `csrftoken` çerezleri kullanılır. Nasıl bulunacağını **?** düğmesi anlatır.

### Güvenlik

- `sessionid` bir şifre gibidir. Paylaşma, ekran görüntüsüne koyma, GitHub'a yükleme.
- Çerezler yalnızca bilgisayarında saklanır ve yalnızca Instagram'a gönderilir.
- Mümkünse ana hesabın yerine ikinci bir hesap kullan.

### Sorumluluk ve yasal uyarı

- Otomatik indirme Instagram'ın Kullanım Koşulları'na aykırı olabilir ve hesabının kısıtlanmasına yol açabilir. Kullanım senin sorumluluğundadır.
- Başkalarının fotoğraf ve videoları telif hakkıyla korunur. Yalnızca **kendi içeriğini** ya da **izin aldığın** içerikleri indir, izinsiz yeniden paylaşma.
- Yazılım "olduğu gibi" sunulur, garanti verilmez.
