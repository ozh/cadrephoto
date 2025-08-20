# 🔌🖼️ Cadrephoto
> An email-to-photo-frame for your Grandma, powered by Raspberry Pi and eink display<br/>

**Cadrephoto** (_french for "photo frame"_) is a project that allows you to send photos
on a digital photo frame **via email** : no app needed, no knowledge, perfect for users
of all ages and who may not be tech-savvy.

<img width="1280" height="640" alt="image" src="https://github.com/user-attachments/assets/a1295404-95e5-44e1-a95a-6fe6610597b7" />

## 📑 Table of Contents
- [💡 Features](#-features)
- [🖥️ Hardware](#-hardware)
- [⚙️ Installation](#-installation)
- [🧩 Setup the service](#-setup-the-service)
- [📸 Pictures](#-pictures)
- [📝 Inspiration & License](#-inspiration-and-license)
 
# 💡 Features

The principle is the following:

- Raspberry Pi runs a Python script displaying photos on an eink screen
- It checks at regular intervals for new emails on a given email account
- When a new email with a photo arrives, the photo is displayed on the screen
- Email sender and photo frame owner receive an email notification
- Only the most recent photos are kept, making things ephemeral and an incentive to send newer pics more often ;)
- Everything is fully configurable via a simple configuration file

The buttons on the frame are used to perform various actions:

- ⏺ **Button 1 (short press)** → display next photo (when Grandma wants something new)
- ⏺ **Button 2 (long press)** → delete current photo (if Grandma doesn’t like it)
- ⏺ **Button 3 (long press)** → debug screens with useful info (for curious Grandpa)
- ⏺ **Button 4 (long press)** → clean shutdown of the Raspberry Pi (when Grandma relocates the frame)

# 🖥️ Hardware

- A [Pimoroni Inky Impressions](https://shop.pimoroni.com/products/inky-impression-7-3) eink display (I used the 7.3")
- Any Raspberry Pi (built on a Raspberry Pi Zero 2 so any model should work)
- Obviously all the required stuff to run a Raspberry Pi (power supply, SD card, etc.)
- A case (I slightly hacked an Ikea 13 cm x 18 cm frame to house the screen ; there are also lots of 3D print templates available)

# ⚙️ Installation

1. You'll want to create a **dedicated email account**, on a server that supports IMAP
and SMTP (most email providers should work) to receive the photos, since the script
will delete all emails after processing them.
<br/>(The wow factor with Grandma and her grand kids from having an email such as `photoframe@your-domain.com` is neat ;)


2. Then, dependencies. You'll have to `pip install` the following Python packages:

* [`inky`](https://github.com/pimoroni/inky) (check [this guide](https://learn.pimoroni.com/article/getting-started-with-inky-impression) if you're new to this)
* `pillow`
* `pillow-heif`
* `lgpio` and `gpiod`
* `python-dotenv`
<br/>(as always, all packages must be installed in the virtual environment -- I sticked to the
one created by the Pimoroni Inky setup script)

3. Clone this repository, copy the [`.env-example`](https://github.com/ozh/cadrephoto/blob/master/.env-example) file to `.env`, and edit everything
to match your setup.


4. Test the script by running it : `python -u main.py` (in the appropriate virtual environment)<br/>
If everything is set up correctly, you can setup the service, see below.<br/>
If not, I included a few [tests](https://github.com/ozh/cadrephoto/blob/master/tests/) to help you troubleshoot things.


# 🧩 Setup the service

Once everything is working, you can setup the service, so the script runs automatically
at Raspberry boot, and restarts if it crashes.

1. Create a systemd service file 

```bash
$ sudo nano /etc/systemd/system/cadrephoto.service
```

2. Copy the following content into the file and modify it to match paths and user :
```ini
[Unit]
Description=Cadrephoto
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/home/ozh/.virtualenvs/pimoroni/bin/python /home/ozh/cadrephoto/app.py
WorkingDirectory=/home/ozh/cadrephoto
Restart=always
RestartSec=120
User=ozh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service :
```bash
$ sudo systemctl daemon-reload
$ sudo systemctl enable cadrephoto.service
$ sudo systemctl start cadrephoto.service
```

4. You can now :
```bash
# Check the status of the service:
$ sudo systemctl status cadrephoto.service

# Stop the service:
$ sudo systemctl stop cadrephoto.service

# View the logs in real-time:
$ journalctl -u cadrephoto.service -f
```

5. I think it's a good idea to install [`log2ram`](https://github.com/azlux/log2ram) to avoid writing constantly on the
SD card, which is not good for its longevity.

# 📷 Pictures

<details>
  <summary>Photo frame full shot</summary>
  
  ![20250818_183325](https://github.com/user-attachments/assets/45d28f79-7cd3-46d4-94b0-2435c51b2b06)
  
  Button A displays next photo. Button B deletes current photo.
</details>

<details>
  <summary>Debug screens</summary>

  Long Press on Button C displays a debug screen with various info, then another screen with the application log

  ![20250818_162448](https://github.com/user-attachments/assets/d0e69d0f-2d7c-48fb-bb32-1a7a159c9a07)
  
</details>

<details>
  <summary>Shutdown screen</summary>
  
  ![20250818_172115](https://github.com/user-attachments/assets/2e69535d-47e5-4088-8454-aea31b040409)
  
  (Customisable message like everything in the project)
</details>




# 📝 Inspiration and License

This was my first Raspberry Pi project and first Python project 🎉.

Special thanks to projects that inspired me:
* https://github.com/NotmoGit/AstroInky
* https://github.com/tymzd/InkMemories

Any crappy code is mine alone 😉

Project licensed under the WTF Public License. [![WTFPL](https://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-4.png)](http://www.wtfpl.net/about/)
Feel free to do whatever the hell you want with it.
