# Information Security Policy

**Effective Date:** January 1, 2026  
**Policy Owner:** Chief Information Security Officer (CISO)  
**Applies To:** All employees, contractors, vendors with system access, and third parties handling company data

---

## 1. Purpose

This policy protects the confidentiality, integrity, and availability of company and customer information. Every individual with access to company systems shares responsibility for safeguarding data. Non-compliance may result in access revocation, disciplinary action, contract termination, and legal liability.

---

## 2. Information Classification

All data must be handled according to its classification:

| Classification | Description | Examples | Handling |
|----------------|-------------|----------|----------|
| **Public** | Approved for public release | Marketing materials, job postings | No restrictions |
| **Internal** | Internal use; low sensitivity | Org charts, internal newsletters | Do not share externally without approval |
| **Confidential** | Business-sensitive | Financial reports, contracts, roadmaps | Need-to-know; encrypted in transit and at rest |
| **Restricted** | Highest sensitivity | PII, PHI, payment data, credentials, source code | Strict access controls; logging; encryption mandatory |

When uncertain, classify at the **higher** level and consult Security.

---

## 3. Access Management

### 3.1 Account Provisioning

- Access granted on **least privilege** principle via role-based access control (RBAC)
- Manager submits access request ticket; Security/IT provisions within **2 business days**
- Privileged access (admin, production database, root) requires additional approval from data owner and Security

### 3.2 Access Reviews

- Managers certify direct report access **quarterly**
- Privileged accounts reviewed **monthly** by Security
- Orphaned or unused accounts disabled after **90 days** of inactivity

### 3.3 Separation of Duties

No single individual may develop, approve, and deploy production changes without secondary review except during documented emergency break-glass procedures.

---

## 4. Password Standards and Rotation

### 4.1 Password Requirements

All company systems must enforce or comply with:

- Minimum **14 characters**
- Combination of uppercase, lowercase, numbers, and symbols
- No dictionary words, names, or reused personal passwords
- Unique passwords per system (password manager required)

### 4.2 Password Rotation

| Account Type | Rotation Frequency | Additional Controls |
|--------------|-------------------|---------------------|
| Standard user accounts | **90 days** (or upon suspected compromise) | MFA required |
| Privileged/admin accounts | **60 days** | MFA + hardware key (YubiKey) |
| Service accounts | **Annual** + automated rotation where supported | Vault-stored secrets only |
| Shared accounts | **Prohibited** except break-glass vault with logging | Security approval required |

Passwords must not be written on physical notes, stored in plain text files, or shared via email or chat.

### 4.3 Password Managers

Employees must use the company-approved password manager (1Password Business) for all work credentials. Personal password managers are permitted only if they meet Security's encryption standards and are documented in the onboarding checklist.

---

## 5. Multi-Factor Authentication (2FA/MFA)

### 5.1 Mandatory MFA

MFA is **required** for:

- Email and calendar (Microsoft 365)
- VPN and zero-trust network access (Zscaler)
- Cloud infrastructure (AWS, GCP, Azure)
- Source code repositories (GitHub Enterprise)
- HRIS, finance, and customer data systems
- Password manager vault

### 5.2 Approved MFA Methods (in order of preference)

1. **Hardware security keys** (FIDO2/WebAuthn) — required for admins and Security team
2. **Authenticator apps** (Microsoft Authenticator, Google Authenticator)
3. **Push notifications** via approved identity provider

**Prohibited:** SMS-only MFA for systems classified Confidential or above (SMS permitted only as backup factor where technically unavoidable).

### 5.3 MFA Enrollment Procedure

1. Complete MFA enrollment within **5 business days** of account creation
2. Register **two** factors minimum (primary + backup)
3. Store backup codes in password manager, not on desk or unencrypted device
4. Report lost hardware keys to IT within **1 hour**; keys revoked and reissued

### 5.4 MFA Exemptions

Exemptions require CISO written approval, time-limited (max 30 days), and compensating controls documented.

---

## 6. Data Handling and Transmission

### 6.1 Storage

- **Restricted data** must reside only in approved systems (listed in Data Inventory portal)
- Local storage of Restricted data on endpoints is prohibited except encrypted caches managed by approved applications
- USB drives: company-issued encrypted drives only; personal USB devices blocked by policy
- Cloud file sharing: OneDrive/SharePoint for Internal and Confidential; Restricted data requires dedicated secure repositories

### 6.2 Transmission

- Email Restricted data only via encrypted channels (TLS + sensitivity labels)
- Use **Secure File Transfer (SFTP)** or approved sharing links with expiration and password protection for external transfers
- Prohibit sending credentials, SSNs, or payment card data via email or Slack

### 6.3 Data Retention and Disposal

Follow Records Retention Schedule. Secure deletion required:

- Digital: NIST 800-88 compliant wiping or destruction
- Physical: cross-cut shredding (P-4 minimum) or certified destruction vendor
- Retired hardware returned to IT for certified wipe before disposal

### 6.4 Customer and Personal Data

Processing of personal data must comply with GDPR, CCPA, and applicable privacy laws. Privacy Impact Assessments required for new products handling personal data.

---

## 7. Clean Desk and Clear Screen

### 7.1 Clean Desk Rules

At the end of each workday or when leaving workspace unattended for **30+ minutes**:

- Lock confidential documents in drawers or cabinets
- Remove whiteboards with sensitive content
- Shred or secure documents marked Confidential or Restricted
- Do not leave badges, keys, or authentication devices visible or unattended
- Visitor areas must not display sensitive information

### 7.2 Clear Screen

- Activate screen lock (**Windows + L** or equivalent) when leaving desk
- Auto-lock timeout: **5 minutes** maximum
- Privacy screens encouraged in open office and public spaces
- Prohibit "remember me" on shared or kiosk machines

### 7.3 Printing

- Use secure print release (badge tap at printer)
- Retrieve printed materials immediately
- Shred misprints containing sensitive data

---

## 8. Endpoint and Network Security

- Company-managed devices required for accessing Confidential/Restricted data
- Antivirus/EDR (CrowdStrike) must remain active; tampering prohibited
- OS patches applied within **14 days** of release (critical patches within **72 hours**)
- Full-disk encryption (BitLocker/FileVault) mandatory
- Personal devices (BYOD) limited to email and calendar via MDM container; no Restricted data

**Home network:** WPA2/WPA3, firmware updated, default credentials changed. VPN required for internal resources.

---

## 9. Software Development Security

- Secrets never committed to source control; use vault and CI/CD secret injection
- Code review required for all production changes
- Dependency scanning (Snyk) must pass or have documented exception
- Production data must not be used in development without anonymization and Security approval

---

## 10. Incident Response

### 10.1 Reportable Events

Report immediately (within **1 hour**) to **security@company.com** or 24/7 hotline:

- Suspected phishing or credential compromise
- Lost/stolen device or badge
- Malware infection
- Unauthorized access or data exfiltration
- Misdirected email containing sensitive data

### 10.2 Employee Obligations During Incident

1. Do not delete evidence
2. Disconnect from network only if directed by Security
3. Preserve logs and screenshots
4. Cooperate with investigation
5. Maintain confidentiality of incident details

### 10.3 Breach Notification

Legal and Security coordinate regulatory and customer notification per Breach Response Playbook.

---

## 11. Security Awareness Training

- All personnel complete **annual** security training
- Phishing simulations conducted **quarterly**; repeated failures trigger remedial training
- Role-based training for engineers, finance, and HR handling Restricted data

---

## 12. Vendor and Third-Party Security

Vendors accessing company data must complete security questionnaire and sign DPA. High-risk vendors require annual SOC 2 review or equivalent.

---

## 13. Enforcement

Violations may result in suspension of access, termination, and civil or criminal prosecution where applicable. Exceptions require documented risk acceptance approved by CISO.

**Document Version:** 5.0  
**Last Reviewed:** December 2025  
**Next Review:** June 2026  
**Contact:** security@company.com
