[
  {
    "name": "mac1.local",
    "platform": "Mac",
    "identifiers": {
      "udid": "1CC1B9C7-0000-1111-2222-33333333333",
      "serial": "C00000000",
      "mac_addresses": [
        "77:77:77:77:77:77",
        "88:88:88:88:88:88"
      ]
    },
    "os_version": "10.11.6",
    "last_sync": "2016-12-30T21:31:47.407000+00:00",
    "sources": [
      "wirelesslogs",
      "jamf"
    ],
    "practices": {
      "f5": {
        "status": "ok",
        "last_updated": "2016-12-30T21:31:47.407000+00:00",
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
        "last_updated": "2016-12-30T21:31:47.407000+00:00",
        "description": "Firewalls control network traffic into and out of a system. Enabling the firewall\n    on your device can stop network-based attacks on your system.",
        "title": "Firewall",
        "value": true,
        "link": "#"
      },
      "encryption": {
        "status": "ok",
        "last_updated": "2016-12-30T21:31:47.407000+00:00",
        "description": "Full-disk encryption protects data at rest from being accessed by a party who\n    does not know the password or decryption key.  Systems containing Netflix internal data should\n    be encrypted.  It is every employee's responsibility to keep Netflix internal data safe.",
        "title": "Disk Encryption",
        "value": true,
        "link": "#",
        "details": "Untitled (Boot Partition): Encrypted (100%)"
      },
      "uptodate": {
        "status": "ok",
        "last_updated": "2016-12-30T21:31:47.407000+00:00",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date.",
        "title": "Up-to-date",
        "value": true,
        "link": "#",
        "details": "The recommended version of Mac OS X is 10.11.6."
      },
      "autoupdate": {
        "status": "nudge",
        "last_updated": "2016-12-30T21:31:47.407000+00:00",
        "description": "One of the most important things you can do to increase Netflix security is to\n    keep your own OS and software up to date. Enabling automatic updating helps ensure your machine\n    is up-to-date without you having to manually install updates.",
        "title": "Automatic Updates",
        "value": false,
        "link": "#",
        "details": "Disabled settings:\n    Install app updates\n    Install OS X updates"
      },
      "screenlock": {
        "status": "ok",
        "last_updated": "2016-12-30T21:31:47.407000+00:00",
        "description": "Screen locks, or screen saver locks, prevent unauthorized third-parties from\n      accessing your laptop when unattended.",
        "title": "Screen Lock",
        "value": true,
        "link": "#"
      },
      "sentinel": {
        "status": "nudge",
        "last_updated": "2016-12-30T21:31:47.407000+00:00",
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
        "last_updated": "2016-12-30T21:31:47.407000+00:00",
        "description": "Carbon Black is part of Netflix's approach to preventing and detecting malware\n    infections. Installing Carbon Black helps protect your system and helps Netflix detect when a\n    system has been compromised, and how, so we can respond quickly and effectively.",
        "title": "Carbon Black",
        "value": true,
        "link": "#"
      }
    },
    "model": "15-inch Retina MacBook Pro (Mid 2015)",
    "os": "Mac OS X",
    "serial": "C00000000",
    "manufacturer": "Apple"
  },
  {
    "identifiers": {
      "mac_addresses": [
        "99:99:99:99:99:99"
      ]
    },
    "last_sync": "2016-12-30T21:31:47.407000+00:00",
    "sources": [
      "wirelesslogs"
    ],
    "practices": {
    }
  }
  ]
