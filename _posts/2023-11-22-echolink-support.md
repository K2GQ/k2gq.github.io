---
layout: post
title: EchoLink Information
subtitle: How to Install EchoLink on your Smartphone
cover-img: /assets/img/FT-817.jpg
thumbnail-img: /assets/img/echolink.webp
share-img: /assets/img/echolink.webp
tags: [echolink,ios,android,iphone,ipad,inrico,t320]
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

<br/>

---

<span id="advanced">

### 📱 Advanced Tips for Android

**Device:** Inrico Network Radio<br/>
**Android Version:** 8.1

### 🔄 Keep EchoLink Connected While Screen is Off

1. Open **Settings**
2. Tap the **⋮ (3-dot menu)**
3. Select **Battery optimization**
4. Choose **All apps**
5. Find and select **EchoLink**
6. Set to **“Don't optimize”**

### 🔌 Prevent Disconnects While Charging via USB

To keep the system from entering low-power states while connected to USB (e.g., charging while running EchoLink), you'll need to use the **ADB (Android Debug Bridge)** tool on a Linux machine.

#### ✅ Verify Current Setting

```bash
adb shell settings get global stay_on_while_plugged_in
```

#### ⚙️ Change the Setting

```bash
adb shell settings put global stay_on_while_plugged_in 3
```

**Note:**
This command tells Android to stay awake when plugged in via:

* USB
* AC power
* Wireless charging


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

<br/>

---

**Device:** Modern Smartphone<br/>
**Android Version:** 15

### 🔄 Keep EchoLink Connected While Screen is Off

1. **Press and hold** the **EchoLink** app icon
2. Tap **App info**
3. Go to **App battery usage**
4. Tap **Allow background usage**
5. Set to **Unrestricted**

