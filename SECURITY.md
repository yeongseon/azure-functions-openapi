# Security Policy

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly:

### Preferred: GitHub Security Advisory

1. Go to the [Security Advisories page](https://github.com/yeongseon/azure-functions-openapi/security/advisories/new)
2. Click "Report a vulnerability"
3. Fill in the details about the vulnerability
4. Submit - this creates a private discussion with maintainers

### Alternative: Email

If you prefer email, contact: yeongseon.choe@gmail.com

### What to include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Initial response**: within 48 hours
- **Status update**: within 7 days
- **Fix release**: depends on severity

Please allow time for the issue to be addressed before public disclosure.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.7.x   | :white_check_mark: |
| 0.6.x   | :white_check_mark: |
| < 0.6   | :x:                |

## Security Updates

Security updates are released as:
- **Patch versions** for critical security fixes
- **Minor versions** for security improvements

Always update to the latest version to ensure you have the latest security fixes.

## Security Features

See [Security Guide](docs/SECURITY.md) for detailed information about:
- Content Security Policy (CSP)
- Security Headers
- Input Validation and Sanitization
- Error Handling
- Caching Security
