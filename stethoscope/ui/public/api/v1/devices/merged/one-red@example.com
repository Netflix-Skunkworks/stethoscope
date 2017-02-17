[
  {
    "name": "mb1.local",
    "os_version": "10.12.1",
    "identifiers": {
      "udid": "59ACE11D-1234-ABCD-0000-C020000000",
      "serial": "C020000000",
      "mac_addresses": [
        "00:00:00:00:00:CC"
      ]
    },
    "last_sync": "2016-12-21T08:00:08.736000+00:00",
    "sources": [
      "jamf"
    ],
    "practices": {
      "f5": {
        "status": "ok",
        "last_updated": "2016-12-21T08:00:08.736000+00:00",
        "description": "The BIG-IP Edge Client is software which enables your system to connect to\n    Netflix's VPN (virtual private network). Using the VPN prevents third parties from eavesdropping\n    on network connections and should be used while on untrusted networks. Connecting through the\n    VPN is also required for certain internal applications (e.g., the 360 review site).",
        "title": "BIG-IP Edge Client (F5)",
        "value": true,
        "link": "#",
        "details": "Version: 7131.2016.0602.1"
      },
      "firewall": {
        "status": "ok",
        "last_updated": "2016-12-21T08:00:08.736000+00:00",
        "description": "Firewalls control network traffic into and out of a system. Enabling the firewall\n    on your device can stop network-based attacks on your system.",
        "title": "Firewall",
        "value": true,
        "link": "#"
      },
      "encryption": {
        "status": "ok",
        "last_updated": "2016-12-21T08:00:08.736000+00:00",
        "description": "Full-disk encryption protects data at rest from being accessed by a party who\n    does not know the password or decryption key.  Systems containing Netflix internal data should\n    be encrypted.  It is every employee's responsibility to keep Netflix internal data safe.",
        "title": "Disk Encryption",
        "value": true,
        "link": "#",
        "details": "Macintosh HD (Boot Partition): Encrypted (100%)"
      },
      "uptodate": {
        "status": "ok",
        "last_updated": "2016-12-21T08:00:08.736000+00:00",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date.",
        "title": "Up-to-date",
        "value": true,
        "link": "#",
        "details": "The recommended version of Mac OS X is 10.11.6."
      },
      "sentinel": {
        "status": "ok",
        "last_updated": "2016-12-21T08:00:08.736000+00:00",
        "description": "SentinelOne is part of Netflix's approach to preventing and detecting malware\n    infections. Installing SentinelOne helps protect your system and helps Netflix detect when a\n    system has been compromised, and how, so we can respond quickly and effectively.",
        "title": "SentinelOne",
        "value": true,
        "link": "#",
        "details": "Version: 1.8.0.1998"
      },
      "screenlock": {
        "status": "ok",
        "last_updated": "2016-12-21T08:00:08.736000+00:00",
        "description": "Screen locks, or screen saver locks, prevent unauthorized third-parties from\n      accessing your laptop when unattended.",
        "title": "Screen Lock",
        "value": true,
        "link": "#"
      },
      "autoupdate": {
        "status": "ok",
        "last_updated": "2016-12-21T08:00:08.736000+00:00",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date. Enabling automatic updating helps ensure your machine\n    is up-to-date without you having to manually install updates.",
        "title": "Automatic Updates",
        "value": true,
        "link": "#"
      },
      "carbonblack": {
        "status": "ok",
        "last_updated": "2016-12-21T08:00:08.736000+00:00",
        "description": "Carbon Black is part of Netflix's approach to preventing and detecting malware\n    infections. Installing Carbon Black helps protect your system and helps Netflix detect when a\n    system has been compromised, and how, so we can respond quickly and effectively.",
        "title": "Carbon Black",
        "value": true,
        "link": "#"
      }
    },
    "platform": "Mac",
    "model": "MacBook (12-inch Retina Early 2016)",
    "os": "Mac OS X",
    "serial": "C020000000"
  },
  {
    "platform": "iOS",
    "os": "iOS",
    "identifiers": {},
    "last_sync": "2016-04-28T03:52:28.967000+00:00",
    "sources": [
      "google"
    ],
    "practices": {
      "jailed": {
        "status": "unknown",
        "last_updated": "2016-04-28T03:52:28.967000+00:00",
        "link": null,
        "description": "Jailbreaking a phone means replacing the default operating system, which can open up the\n    phone to additional security vulnerabilities.",
        "title": "Jailed"
      }
    },
    "user_agent": "Apple-iPad4C5/1305.233,gzip(gfe)",
    "serial": "unknown",
    "type": "Mobile Device",
    "model": "iPad Mini Retina"
  },
  {
    "platform": "Android",
    "os": "Android",
    "identifiers": {
      "imei": "01234567890123456789",
      "serial": "0abcdef01234",
      "mac_addresses": [
        "00:00:00:00:00:DD"
      ]
    },
    "os_version": "5.1.1",
    "last_sync": "2016-12-12T22:01:14.849000+00:00",
    "sources": [
      "google"
    ],
    "practices": {
      "uptodate": {
        "status": "warn",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date.",
        "link": "#",
        "details": "Android 5.1.1 is no longer supported. The recommended version of Android is 6.0.1.",
        "title": "Up-to-date"
      },
      "jailed": {
        "status": "ok",
        "last_updated": "2016-12-12T22:01:14.849000+00:00",
        "description": "Jailbreaking a phone means replacing the default operating system, which can open up the\n    phone to additional security vulnerabilities.",
        "title": "Jailed",
        "value": true,
        "link": null
      }
    },
    "user_agent": "Google Apps Device Policy 6.86",
    "serial": "0abcdef01234",
    "type": "Mobile Device",
    "model": "SAMSUNG-SM-G925A"
  },
  {
    "platform": "iOS",
    "os": "iOS",
    "identifiers": {
      "imei": "11 123456 123456 1",
      "serial": "XXXXXXXX",
      "mac_addresses": [
        "00:11:22:33:44:55"
      ]
    },
    "os_version": "9.3.1",
    "last_sync": "2016-05-31T09:11:50.149000+00:00",
    "sources": [
      "google"
    ],
    "practices": {
      "uptodate": {
        "status": "warn",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date.",
        "link": "#",
        "details": "iOS 9.3.1 is no longer supported. The recommended version of iOS is 9.3.5.",
        "title": "Up-to-date"
      },
      "jailed": {
        "status": "unknown",
        "last_updated": "2016-05-31T09:11:50.149000+00:00",
        "link": null,
        "description": "Jailbreaking a phone means replacing the default operating system, which can open up the\n    phone to additional security vulnerabilities.",
        "title": "Jailed"
      }
    },
    "serial": "XXXXXXXX",
    "type": "Mobile Device",
    "model": "iPhone 6s Plus"
  },
  {
    "platform": "iOS",
    "os": "iOS",
    "identifiers": {
      "imei": "12 345678 901234 5",
      "serial": "F000000000000A",
      "mac_addresses": [
        "AA:BB:CC:DD:11:22"
      ]
    },
    "os_version": "10.1",
    "last_sync": "2016-12-30T21:56:10.345000+00:00",
    "sources": [
      "google"
    ],
    "practices": {
      "uptodate": {
        "status": "ok",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date.",
        "link": "#",
        "details": "The recommended version of iOS is 9.3.5.",
        "title": "Up-to-date"
      },
      "jailed": {
        "status": "unknown",
        "last_updated": "2016-12-30T21:56:10.345000+00:00",
        "link": null,
        "description": "Jailbreaking a phone means replacing the default operating system, which can open up the\n    phone to additional security vulnerabilities.",
        "title": "Jailed"
      }
    },
    "serial": "F000000000000A",
    "type": "Mobile Device",
    "model": "iPhone9,4"
  },
  {
    "platform": "iOS",
    "os": "iOS",
    "identifiers": {},
    "last_sync": "2016-03-01T02:08:01.564000+00:00",
    "sources": [
      "google"
    ],
    "practices": {
      "jailed": {
        "status": "unknown",
        "last_updated": "2016-03-01T02:08:01.564000+00:00",
        "link": null,
        "description": "Jailbreaking a phone means replacing the default operating system, which can open up the\n    phone to additional security vulnerabilities.",
        "title": "Jailed"
      }
    },
    "user_agent": "Apple-iPhone7C1/1301.404,gzip(gfe)",
    "serial": "unknown",
    "type": "Mobile Device",
    "model": "iPhone 6 Plus"
  },
  {
    "platform": "Android",
    "os": "Android",
    "identifiers": {
      "serial": "8899000000000000000",
      "mac_addresses": [
        "02:00:00:00:00:00"
      ]
    },
    "os_version": "7.0",
    "last_sync": "2016-12-20T18:39:50.105000+00:00",
    "sources": [
      "google"
    ],
    "practices": {
      "uptodate": {
        "status": "ok",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date.",
        "link": "#",
        "details": "The recommended version of Android is 6.0.1.",
        "title": "Up-to-date"
      },
      "jailed": {
        "status": "ok",
        "last_updated": "2016-12-20T18:39:50.105000+00:00",
        "description": "Jailbreaking a phone means replacing the default operating system, which can open up the\n    phone to additional security vulnerabilities.",
        "title": "Jailed",
        "value": true,
        "link": null
      }
    },
    "user_agent": "Google Apps Device Policy 7.03",
    "serial": "8899000000000000000",
    "type": "Mobile Device",
    "model": "Nexus 6P"
  },
  {
    "platform": "iOS",
    "os": "iOS",
    "identifiers": {
      "imei": "35 999999 999999 3",
      "serial": "DLX000000000"
    },
    "os_version": "9.0",
    "last_sync": "2016-03-12T07:30:04.092000+00:00",
    "sources": [
      "google"
    ],
    "practices": {
      "uptodate": {
        "status": "warn",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date.",
        "link": "#",
        "details": "iOS 9.0 is no longer supported. The recommended version of iOS is 9.3.5.",
        "title": "Up-to-date"
      },
      "jailed": {
        "status": "unknown",
        "last_updated": "2016-03-12T07:30:04.092000+00:00",
        "link": null,
        "description": "Jailbreaking a phone means replacing the default operating system, which can open up the\n    phone to additional security vulnerabilities.",
        "title": "Jailed"
      }
    },
    "serial": "DLX000000000",
    "type": "Mobile Device",
    "model": "iPad Mini (2nd generation)"
  },
  {
    "platform": "iOS",
    "os": "iOS",
    "identifiers": {
      "imei": "35 000000 999999 5",
      "serial": "DMPN0000000",
      "mac_addresses": [
        "D0:D0:D0:D0:D0:D0"
      ]
    },
    "os_version": "9.3.2",
    "last_sync": "2016-06-14T07:32:33.239000+00:00",
    "sources": [
      "google"
    ],
    "practices": {
      "uptodate": {
        "status": "warn",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date.",
        "link": "#",
        "details": "iOS 9.3.2 is no longer supported. The recommended version of iOS is 9.3.5.",
        "title": "Up-to-date"
      },
      "jailed": {
        "status": "unknown",
        "last_updated": "2016-06-14T07:32:33.239000+00:00",
        "link": null,
        "description": "Jailbreaking a phone means replacing the default operating system, which can open up the\n    phone to additional security vulnerabilities.",
        "title": "Jailed"
      }
    },
    "serial": "DMPN0000000",
    "type": "Mobile Device",
    "model": "iPad Air 2"
  },
  {
    "platform": "iOS",
    "os": "iOS",
    "identifiers": {
      "imei": "35 666666 666666 6",
      "serial": "C39RF000000000",
      "mac_addresses": [
        "12:34:56:78:90:12"
      ]
    },
    "os_version": "10.0.1",
    "last_sync": "2016-09-23T17:54:03.868000+00:00",
    "sources": [
      "google"
    ],
    "practices": {
      "uptodate": {
        "status": "ok",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date.",
        "link": "#",
        "details": "The recommended version of iOS is 9.3.5.",
        "title": "Up-to-date"
      },
      "jailed": {
        "status": "unknown",
        "last_updated": "2016-09-23T17:54:03.868000+00:00",
        "link": null,
        "description": "Jailbreaking a phone means replacing the default operating system, which can open up the\n    phone to additional security vulnerabilities.",
        "title": "Jailed"
      }
    },
    "serial": "C39RF000000000",
    "type": "Mobile Device",
    "model": "iPhone 6s Plus"
  },
  {
    "platform": "iOS",
    "os": "iOS",
    "identifiers": {
      "imei": "35 888888 888888 8",
      "serial": "DLXQ8888888888",
      "mac_addresses": [
        "70:70:70:70:70:70"
      ]
    },
    "os_version": "10.1",
    "last_sync": "2016-12-30T17:51:38.853000+00:00",
    "sources": [
      "google"
    ],
    "practices": {
      "uptodate": {
        "status": "ok",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date.",
        "link": "#",
        "details": "The recommended version of iOS is 9.3.5.",
        "title": "Up-to-date"
      },
      "jailed": {
        "status": "unknown",
        "last_updated": "2016-12-30T17:51:38.853000+00:00",
        "link": null,
        "description": "Jailbreaking a phone means replacing the default operating system, which can open up the\n    phone to additional security vulnerabilities.",
        "title": "Jailed"
      }
    },
    "serial": "DLXQ8888888888",
    "type": "Mobile Device",
    "model": "iPad6,8"
  },
  {
    "platform": "iOS",
    "os": "iOS",
    "identifiers": {
      "imei": "35 999999 888888 7",
      "serial": "DMPR000000000",
      "mac_addresses": [
        "99:99:99:99:99:99"
      ]
    },
    "os_version": "10.1.1",
    "last_sync": "2016-12-30T17:51:52.433000+00:00",
    "sources": [
      "google"
    ],
    "practices": {
      "uptodate": {
        "status": "ok",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date.",
        "link": "#",
        "details": "The recommended version of iOS is 9.3.5.",
        "title": "Up-to-date"
      },
      "jailed": {
        "status": "unknown",
        "last_updated": "2016-12-30T17:51:52.433000+00:00",
        "link": null,
        "description": "Jailbreaking a phone means replacing the default operating system, which can open up the\n    phone to additional security vulnerabilities.",
        "title": "Jailed"
      }
    },
    "serial": "DMPR000000000",
    "type": "Mobile Device",
    "model": "iPad6,4"
  }
]
