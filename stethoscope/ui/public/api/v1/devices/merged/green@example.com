[
  {
    "os_version": "10.2",
    "os": "iOS",
    "identifiers": {
      "imei": "35 000000 123456 8",
      "serial": "C0000000XL",
      "mac_addresses": [
        "00:11:22:33:44:55"
      ]
    },
    "last_sync": "2016-12-30T16:08:08.985000+00:00",
    "sources": [
      "wirelesslogs",
      "google"
    ],
    "practices": {
      "f5": {
        "status": "unknown",
        "link": "#",
        "description": "The BIG-IP Edge Client is software which enables your system to connect to\n    Netflix's VPN (virtual private network). Using the VPN prevents third parties from eavesdropping\n    on network connections and should be used while on untrusted networks. Connecting through the\n    VPN is also required for certain internal applications (e.g., the 360 review site).",
        "title": "BIG-IP Edge Client (F5)"
      },
      "duo": {
        "status": "na",
        "link": "#",
        "description": "Duo is the application Netflix uses for multi-factor authentication, which is\n    required when accessing sensitive systems and the VPN.",
        "title": "Duo"
      },
      "firewall": {
        "status": "na",
        "link": "#",
        "description": "Firewalls control network traffic into and out of a system. Enabling the firewall\n    on your device can stop network-based attacks on your system.",
        "title": "Firewall"
      },
      "encryption": {
        "status": "unknown",
        "link": "#",
        "description": "Full-disk encryption protects data at rest from being accessed by a party who\n    does not know the password or decryption key.  Systems containing Netflix internal data should\n    be encrypted.  It is every employee's responsibility to keep Netflix internal data safe.",
        "title": "Disk Encryption"
      },
      "uptodate": {
        "status": "ok",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date.",
        "link": "#",
        "details": "The recommended version of iOS is 9.3.5.",
        "title": "Up-to-date"
      },
      "autoupdate": {
        "status": "na",
        "link": "#",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date. Enabling automatic updating helps ensure your machine\n    is up-to-date without you having to manually install updates.",
        "title": "Automatic Updates"
      },
      "screenlock": {
        "status": "unknown",
        "link": "#",
        "description": "Screen locks, or screen saver locks, prevent unauthorized third-parties from\n      accessing your laptop when unattended.",
        "title": "Screen Lock"
      },
      "sentinel": {
        "status": "na",
        "link": "#",
        "description": "SentinelOne is part of Netflix's approach to preventing and detecting malware\n    infections. Installing SentinelOne helps protect your system and helps Netflix detect when a\n    system has been compromised, and how, so we can respond quickly and effectively.",
        "title": "SentinelOne",
        "display": false
      },
      "jailed": {
        "status": "unknown",
        "last_updated": "2016-12-30T16:08:08.985000+00:00",
        "link": null,
        "description": "Jailbreaking a phone means replacing the default operating system, which can open up the\n    phone to additional security vulnerabilities.",
        "title": "Jailed"
      },
      "carbonblack": {
        "status": "na",
        "link": "#",
        "description": "Carbon Black is part of Netflix's approach to preventing and detecting malware\n    infections. Installing Carbon Black helps protect your system and helps Netflix detect when a\n    system has been compromised, and how, so we can respond quickly and effectively.",
        "title": "Carbon Black"
      }
    },
    "platform": "iOS",
    "serial": "C0000000XL",
    "type": "Mobile Device",
    "model": "iPhone8,4",
    "manufacturer": null
  },
  {
    "name": "green-machine",
    "platform": "Mac",
    "identifiers": {
      "udid": "1B611101-0000-1234-ABCD-123456789ABC",
      "serial": "C02ABCDEFG",
      "mac_addresses": [
        "0:00:00:00:00:00",
        "0:00:00:00:00:01"
      ]
    },
    "os_version": "10.12.2",
    "last_sync": "2016-12-30T19:15:38.668000+00:00",
    "sources": [
      "wirelesslogs",
      "jamf"
    ],
    "practices": {
      "f5": {
        "status": "ok",
        "last_updated": "2016-12-30T19:15:38.668000+00:00",
        "description": "The BIG-IP Edge Client is software which enables your system to connect to\n    Netflix's VPN (virtual private network). Using the VPN prevents third parties from eavesdropping\n    on network connections and should be used while on untrusted networks. Connecting through the\n    VPN is also required for certain internal applications (e.g., the 360 review site).",
        "title": "BIG-IP Edge Client (F5)",
        "value": true,
        "link": "#",
        "details": "Version: 7131.2016.0602.1"
      },
      "duo": {
        "status": "na",
        "link": "#",
        "description": "Duo is the application Netflix uses for multi-factor authentication, which is\n    required when accessing sensitive systems and the VPN.",
        "title": "Duo"
      },
      "firewall": {
        "status": "ok",
        "last_updated": "2016-12-30T19:15:38.668000+00:00",
        "description": "Firewalls control network traffic into and out of a system. Enabling the firewall\n    on your device can stop network-based attacks on your system.",
        "title": "Firewall",
        "value": true,
        "link": "#"
      },
      "encryption": {
        "status": "ok",
        "last_updated": "2016-12-30T19:15:38.668000+00:00",
        "description": "Full-disk encryption protects data at rest from being accessed by a party who\n    does not know the password or decryption key.  Systems containing Netflix internal data should\n    be encrypted.  It is every employee's responsibility to keep Netflix internal data safe.",
        "title": "Disk Encryption",
        "value": true,
        "link": "#",
        "details": "Mac HD (Boot Partition): Encrypted (100%)"
      },
      "uptodate": {
        "status": "ok",
        "last_updated": "2016-12-30T19:15:38.668000+00:00",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date.",
        "title": "Up-to-date",
        "value": true,
        "link": "#",
        "details": "The recommended version of Mac OS X is 10.11.6."
      },
      "autoupdate": {
        "status": "ok",
        "last_updated": "2016-12-30T19:15:38.668000+00:00",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date. Enabling automatic updating helps ensure your machine\n    is up-to-date without you having to manually install updates.",
        "title": "Automatic Updates",
        "value": true,
        "link": "#"
      },
      "screenlock": {
        "status": "ok",
        "last_updated": "2016-12-30T19:15:38.668000+00:00",
        "description": "Screen locks, or screen saver locks, prevent unauthorized third-parties from\n      accessing your laptop when unattended.",
        "title": "Screen Lock",
        "value": true,
        "link": "#"
      },
      "sentinel": {
        "status": "nudge",
        "last_updated": "2016-12-30T19:15:38.668000+00:00",
        "description": "SentinelOne is part of Netflix's approach to preventing and detecting malware\n    infections. Installing SentinelOne helps protect your system and helps Netflix detect when a\n    system has been compromised, and how, so we can respond quickly and effectively.",
        "title": "SentinelOne",
        "value": false,
        "link": "#",
        "display": false
      },
      "jailed": {
        "status": "na",
        "link": null,
        "description": "Jailbreaking a phone means replacing the default operating system, which can open up the\n    phone to additional security vulnerabilities.",
        "title": "Jailed"
      },
      "carbonblack": {
        "status": "ok",
        "last_updated": "2016-12-30T19:15:38.668000+00:00",
        "description": "Carbon Black is part of Netflix's approach to preventing and detecting malware\n    infections. Installing Carbon Black helps protect your system and helps Netflix detect when a\n    system has been compromised, and how, so we can respond quickly and effectively.",
        "title": "Carbon Black",
        "value": true,
        "link": "#"
      }
    },
    "model": "13-inch MacBook Pro (Early 2015)",
    "os": "Mac OS X",
    "serial": "C02ABCDEFG",
    "manufacturer": null
  },
  {
    "os_version": "10.2",
    "os": "iOS",
    "identifiers": {
      "serial": "DMPRK00000000",
      "mac_addresses": [
        "00:00:00:00:00:AA"
      ]
    },
    "last_sync": "2016-12-30T16:13:41.614000+00:00",
    "sources": [
      "wirelesslogs",
      "google"
    ],
    "practices": {
      "f5": {
        "status": "unknown",
        "link": "#",
        "description": "The BIG-IP Edge Client is software which enables your system to connect to\n    Netflix's VPN (virtual private network). Using the VPN prevents third parties from eavesdropping\n    on network connections and should be used while on untrusted networks. Connecting through the\n    VPN is also required for certain internal applications (e.g., the 360 review site).",
        "title": "BIG-IP Edge Client (F5)"
      },
      "duo": {
        "status": "na",
        "link": "#",
        "description": "Duo is the application Netflix uses for multi-factor authentication, which is\n    required when accessing sensitive systems and the VPN.",
        "title": "Duo"
      },
      "firewall": {
        "status": "na",
        "link": "#",
        "description": "Firewalls control network traffic into and out of a system. Enabling the firewall\n    on your device can stop network-based attacks on your system.",
        "title": "Firewall"
      },
      "encryption": {
        "status": "unknown",
        "link": "#",
        "description": "Full-disk encryption protects data at rest from being accessed by a party who\n    does not know the password or decryption key.  Systems containing Netflix internal data should\n    be encrypted.  It is every employee's responsibility to keep Netflix internal data safe.",
        "title": "Disk Encryption"
      },
      "uptodate": {
        "status": "ok",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date.",
        "link": "#",
        "details": "The recommended version of iOS is 9.3.5.",
        "title": "Up-to-date"
      },
      "autoupdate": {
        "status": "na",
        "link": "#",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date. Enabling automatic updating helps ensure your machine\n    is up-to-date without you having to manually install updates.",
        "title": "Automatic Updates"
      },
      "screenlock": {
        "status": "unknown",
        "link": "#",
        "description": "Screen locks, or screen saver locks, prevent unauthorized third-parties from\n      accessing your laptop when unattended.",
        "title": "Screen Lock"
      },
      "sentinel": {
        "status": "na",
        "link": "#",
        "description": "SentinelOne is part of Netflix's approach to preventing and detecting malware\n    infections. Installing SentinelOne helps protect your system and helps Netflix detect when a\n    system has been compromised, and how, so we can respond quickly and effectively.",
        "title": "SentinelOne",
        "display": false
      },
      "jailed": {
        "status": "unknown",
        "last_updated": "2016-12-30T16:13:41.614000+00:00",
        "link": null,
        "description": "Jailbreaking a phone means replacing the default operating system, which can open up the\n    phone to additional security vulnerabilities.",
        "title": "Jailed"
      },
      "carbonblack": {
        "status": "na",
        "link": "#",
        "description": "Carbon Black is part of Netflix's approach to preventing and detecting malware\n    infections. Installing Carbon Black helps protect your system and helps Netflix detect when a\n    system has been compromised, and how, so we can respond quickly and effectively.",
        "title": "Carbon Black"
      }
    },
    "platform": "iOS",
    "serial": "DMPRK00000000",
    "type": "Mobile Device",
    "model": "iPad6,3",
    "manufacturer": null
  }
]
