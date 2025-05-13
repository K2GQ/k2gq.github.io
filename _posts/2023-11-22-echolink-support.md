---
layout: post
title: EchoLink Information
subtitle: How to Install EchoLink on your Smartphone
cover-img: /assets/img/FT-817.jpg
thumbnail-img: /assets/img/echolink.webp
share-img: /assets/img/echolink.webp
tags: [echolink,ios,android,iphone,ipad]
---

EchoLink is a popular system used by amateur radio operators to link radio repeaters to the internet, allowing radio communications to extend beyond the traditional range of radio signals.  Using EchoLink, an operator can access their local repeater from anywhere with an internet connection, effectively overcoming geographical limitations. This is especially useful in situations where direct radio contact with the repeater is not possible due to distance, obstructions, or reduced signal strength.  The EchoLink setup on KC2TXA/R assures the operator their signal will be "full quieting" into the repeater and enjoy Q5 copy during reception.

---

**EchoLink for iOS** is an edition of the EchoLink software that runs on an iPhone, iPad, or iPod touch. If you own one of these devices and are a validated EchoLink user, you can access the EchoLink system from nearly anywhere where WiFi networking is available. If you have an iPhone or cellular-capable iPad, you can also use it to access EchoLink over the cellular data network. EchoLink for iOS is available free of charge from Apple's App Store.

If you have used EchoLink before (for example, on Windows), enter the callsign and password you already have. Otherwise, choose and enter a password, and the app will walk you through the first part of the registration procedure.

If necessary, [request a password reset](https://www.echolink.org/validation/) from the Validation page on the EchoLink Web site.

**iOS Download:** [https://apps.apple.com/us/app/echolink/id350688562](https://apps.apple.com/us/app/echolink/id350688562)

---

**EchoLink for Android** is an edition of the EchoLink software that runs on an Android smartphone or tablet. If you own one of these devices and are a validated EchoLink user, you can access the EchoLink system from nearly anywhere where WiFi or cellular networking is available. EchoLink for Android is available free of charge from Google Play; tap the Google Play icon on your phone and search for EchoLink.

If you have used EchoLink before (for example, on Windows), enter the callsign and password you already have. Otherwise, choose and enter a password, and the app will walk you through the first part of the registration procedure.

If necessary, [request a password reset](https://www.echolink.org/validation/) from the Validation page on the EchoLink Web site.

**Android Download:** [https://play.google.com/store/search?q=echolink&c=apps](https://play.google.com/store/search?q=echolink&c=apps)

**Advanced Tips for Android**
Android Version 8.1 (**Inrico Network Radio**)
Allow EchoLink to remain connected while screen is off:
Settings > 3 vertical dots > Battery optimization > All apps > EchoLink > Set To "Don't optimize"

Help keep system from entering low-power states on USB (remain connected to EchoLink while charging):
note: for this function, we connect the Inrico to a linux computer and use the adb (Android Debug Bridge) package.
verify: adb shell settings get global stay_on_while_plugged_in
change: adb shell settings put global stay_on_while_plugged_in 3

| Decimal Value | Binary Flag | Power Source          | Behavior                                 |
| ------------- | ----------- | --------------------- | ---------------------------------------- |
| `0`           | `000`       | None                  | Screen sleeps normally                   |
| `1`           | `001`       | AC charger            | Stay awake when plugged into AC          |
| `2`           | `010`       | USB port              | Stay awake when connected to USB power   |
| `3`           | `011`       | AC + USB              | Stay awake on either AC or USB           |
| `4`           | `100`       | Wireless charger (Qi) | Stay awake when using wireless charging  |
| `5`           | `101`       | AC + Wireless         | Stay awake on AC or wireless             |
| `6`           | `110`       | USB + Wireless        | Stay awake on USB or wireless            |
| `7`           | `111`       | AC + USB + Wireless   | Stay awake regardless of charging method |


Android Version 15 (**modern smartphone**)
Allow EchoLink to remain connected while screen is off:
Press and hold EchoLink app icon > App info > App battery usage > Allow background usage (press this) > Unrestricted

