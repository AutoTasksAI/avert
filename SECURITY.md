# Security Policy

## Our Commitment

Avert is a privacy-first tool. We take security seriously and welcome responsible disclosure of any vulnerabilities.

## Reporting a Vulnerability

**Please DO NOT open public issues for security vulnerabilities.**

Instead, email us at: **security@getavert.app**

Include:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

## Response Timeline

- **24 hours:** We'll acknowledge receipt
- **7 days:** We'll provide an initial assessment
- **30 days:** We'll release a patch (if vulnerability confirmed)

## Security Researchers

We encourage security audits! Focus areas:

### High Priority
1. **Data exfiltration risks** - Does any data leave the machine?
2. **Memory safety** - Buffer overflows, memory leaks
3. **Privilege escalation** - Does Avert request unnecessary permissions?
4. **Code injection** - Can malicious actors modify behavior?

### Medium Priority
5. Denial of service attacks
6. Webcam access abuse
7. Privacy bypass techniques

## Scope

**In Scope:**
- Avert desktop application (Windows)
- Official website (getavert.app)
- Gumroad integration

**Out of Scope:**
- Third-party services (Gumroad, payment processors)
- Social engineering attacks
- Physical access attacks

## Known Limitations

We're transparent about current limitations:

1. **Windows-only webcam access** - macOS/Linux use different APIs
2. **Single webcam limitation** - Windows allows one app per webcam
3. **Lighting dependency** - Very dark environments reduce accuracy
4. **No remote attestation** - Offline-first design prevents cloud verification

## Security Best Practices for Users

1. ✅ Download only from [getavert.app](https://getavert.app)
2. ✅ Block Avert in Windows Firewall to confirm offline operation
3. ✅ Keep Windows updated
4. ✅ Use alongside other security tools (antivirus, VPN)

## Past Security Issues

None reported yet. We'll maintain a transparent log here.

## Hall of Fame

Security researchers who've helped make Avert more secure:

- *Your name could be here!*

---

**Thank you for keeping Avert users safe!**

Last updated: January 19, 2026
