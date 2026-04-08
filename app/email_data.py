from copy import deepcopy
from typing import Dict, List

from app.models import Category, Email, Priority


BASE_EMAIL_RECORDS: List[Dict[str, object]] = [
    {
        "subject": "Production API outage impacting enterprise tenants",
        "sender": "alerts@datadomeops.com",
        "body": (
            "Our monitoring started firing at 07:12 UTC and the production API is returning 503s for every region. "
            "Three enterprise tenants have already reported failed transactions and the on-call dashboard shows error rates above 85 percent. "
            "We rolled back the last config push but the incident is still active. "
            "Please coordinate an incident bridge immediately and post customer-safe updates."
        ),
        "timestamp": "2026-04-08T07:16:00Z",
        "has_attachment": True,
        "thread_id": "incident-prod-api",
        "ground_truth": {
            "priority": Priority.URGENT,
            "category": Category.TECHNICAL,
            "should_escalate": True,
            "key_phrases": ["production api", "incident bridge", "customer-safe updates"],
            "escalation_threshold": True,
        },
    },
    {
        "subject": "Repeated payment failures on renewal invoices",
        "sender": "revops@paymentsuite.io",
        "body": (
            "Our automated retry system has failed on 19 renewal invoices for customers renewing this morning. "
            "Finance is seeing card authorization errors even for accounts that usually pay on time. "
            "Several account managers are asking whether service access should be preserved while we investigate. "
            "We need someone to confirm the root cause and communicate next steps today."
        ),
        "timestamp": "2026-04-08T08:02:00Z",
        "has_attachment": False,
        "thread_id": "billing-renewal-failures",
        "ground_truth": {
            "priority": Priority.URGENT,
            "category": Category.BILLING,
            "should_escalate": True,
            "key_phrases": ["payment failures", "investigating", "next steps"],
            "escalation_threshold": True,
        },
    },
    {
        "subject": "Potential credential theft detected in customer workspace",
        "sender": "security@watchtowersec.net",
        "body": (
            "We observed a successful login from a new ASN followed by mass export activity in the Lyon workspace. "
            "The session was authenticated with a privileged support account and downloaded 11 customer reports. "
            "The customer is asking whether this is a confirmed breach and if tokens should be revoked. "
            "Please involve security leadership and prepare a containment plan right away."
        ),
        "timestamp": "2026-04-08T08:41:00Z",
        "has_attachment": True,
        "thread_id": "security-lyon-workspace",
        "ground_truth": {
            "priority": Priority.URGENT,
            "category": Category.TECHNICAL,
            "should_escalate": True,
            "key_phrases": ["containment plan", "tokens", "security leadership"],
            "escalation_threshold": True,
        },
    },
    {
        "subject": "This outage is unacceptable for our executive team",
        "sender": "cto@bigclient.io",
        "body": (
            "Your status page still says degraded performance while our executives have been blocked from sending proposals for two hours. "
            "We have a board meeting in under an hour and this failure is now visible to our leadership team. "
            "I need a real escalation path, an ETA, and a written explanation I can forward internally. "
            "Please do not send a generic support response."
        ),
        "timestamp": "2026-04-08T09:05:00Z",
        "has_attachment": False,
        "thread_id": "vip-outage-board-meeting",
        "ground_truth": {
            "priority": Priority.URGENT,
            "category": Category.CUSTOMER_SUPPORT,
            "should_escalate": True,
            "key_phrases": ["eta", "escalation path", "written explanation"],
            "escalation_threshold": True,
        },
    },
    {
        "subject": "Critical bug corrupting CSV imports",
        "sender": "john.smith@enterprise.com",
        "body": (
            "Every time our operations team uploads a CSV with more than 2,000 rows, the values in the status column are shifted by one cell. "
            "We reproduced it in production twice this morning and it is forcing us to manually repair records before invoicing. "
            "This is not a full outage, but it is blocking our finance close. "
            "Can engineering confirm if there is a hotfix timeline?"
        ),
        "timestamp": "2026-04-08T09:28:00Z",
        "has_attachment": True,
        "thread_id": "csv-import-corruption",
        "ground_truth": {
            "priority": Priority.HIGH,
            "category": Category.TECHNICAL,
            "should_escalate": True,
            "key_phrases": ["hotfix timeline", "csv", "blocking finance close"],
            "escalation_threshold": True,
        },
    },
    {
        "subject": "Dispute on duplicate annual billing charge",
        "sender": "ap@northstarhealth.org",
        "body": (
            "Our controller noticed two annual subscription charges posted within six minutes on the same card. "
            "We only authorized one renewal and the duplicate is already causing internal audit questions. "
            "Please review the invoice history and advise whether a refund is being processed. "
            "We would like confirmation before the end of business."
        ),
        "timestamp": "2026-04-08T10:11:00Z",
        "has_attachment": False,
        "thread_id": "duplicate-billing-charge",
        "ground_truth": {
            "priority": Priority.HIGH,
            "category": Category.BILLING,
            "should_escalate": True,
            "key_phrases": ["refund", "invoice history", "confirmation before end of business"],
            "escalation_threshold": True,
        },
    },
    {
        "subject": "Enterprise security questionnaire for pilot approval",
        "sender": "procurement@atlasventures.com",
        "body": (
            "We are ready to move your product into our pilot review queue, but procurement needs the security questionnaire completed first. "
            "The document is attached and our steering committee meets on Friday morning. "
            "If we receive answers today, we can keep the pilot on track for this quarter. "
            "Please route this to the right owner."
        ),
        "timestamp": "2026-04-08T10:34:00Z",
        "has_attachment": True,
        "thread_id": "atlas-pilot-security-review",
        "ground_truth": {
            "priority": Priority.HIGH,
            "category": Category.SALES,
            "should_escalate": True,
            "key_phrases": ["security questionnaire", "pilot", "right owner"],
            "escalation_threshold": True,
        },
    },
    {
        "subject": "Need pricing and SLA details for 900-seat rollout",
        "sender": "it-director@oakridgebank.com",
        "body": (
            "We are comparing your enterprise plan with two other vendors and need pricing, uptime commitments, and support coverage details. "
            "Our evaluation committee is shortlisting this week and the decision will affect a 900-seat rollout. "
            "Please let us know whether someone from your enterprise team can join a call tomorrow. "
            "A prompt reply would be appreciated."
        ),
        "timestamp": "2026-04-08T11:02:00Z",
        "has_attachment": False,
        "thread_id": "oakridge-eval",
        "ground_truth": {
            "priority": Priority.HIGH,
            "category": Category.SALES,
            "should_escalate": True,
            "key_phrases": ["pricing", "sla", "enterprise team"],
            "escalation_threshold": True,
        },
    },
    {
        "subject": "Intermittent login errors for EU users",
        "sender": "helpdesk@meridian-logistics.com",
        "body": (
            "Several employees in our Berlin office are seeing login loops when they attempt single sign-on. "
            "The issue started after lunch and affects about a dozen users, but some people can still get in after multiple tries. "
            "We attached browser console logs and screenshots. "
            "Please advise whether there is a known issue or workaround."
        ),
        "timestamp": "2026-04-08T11:27:00Z",
        "has_attachment": True,
        "thread_id": "eu-login-loops",
        "ground_truth": {
            "priority": Priority.HIGH,
            "category": Category.TECHNICAL,
            "should_escalate": False,
            "key_phrases": ["known issue", "workaround", "browser console logs"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Invoice tax ID needs correction before payment run",
        "sender": "finance@solsticemedia.co",
        "body": (
            "The legal entity name is correct on invoice INV-8821, but the tax registration number is not. "
            "Our accounts payable team cannot release payment until the corrected invoice is uploaded. "
            "This is holding up a standard monthly payment rather than a service emergency. "
            "Could you send a revised copy today?"
        ),
        "timestamp": "2026-04-08T11:49:00Z",
        "has_attachment": False,
        "thread_id": "invoice-tax-id-correction",
        "ground_truth": {
            "priority": Priority.MEDIUM,
            "category": Category.BILLING,
            "should_escalate": False,
            "key_phrases": ["revised copy", "invoice", "today"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "How do we export all closed tickets for Q1?",
        "sender": "ops.manager@clearwaterservices.com",
        "body": (
            "I could not find a way to export only closed tickets for the first quarter from the analytics tab. "
            "We are preparing a quarterly operations review and need the file in CSV format. "
            "If there is a filter or report template, a quick explanation would help. "
            "No immediate outage here, just trying to meet an internal deadline."
        ),
        "timestamp": "2026-04-08T12:06:00Z",
        "has_attachment": False,
        "thread_id": "q1-ticket-export",
        "ground_truth": {
            "priority": Priority.MEDIUM,
            "category": Category.CUSTOMER_SUPPORT,
            "should_escalate": False,
            "key_phrases": ["export", "csv", "filter or report template"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Feature request: approval workflow for vendor invoices",
        "sender": "productops@artisanfoods.com",
        "body": (
            "Our finance team loves the current invoice intake flow, but we still manage approvals in a separate tool. "
            "It would be helpful to have a basic approval workflow with two sign-off stages and audit timestamps. "
            "This is not urgent, though we are planning our second-half tooling roadmap. "
            "Happy to share examples if the request is useful."
        ),
        "timestamp": "2026-04-08T12:44:00Z",
        "has_attachment": False,
        "thread_id": "feature-approval-workflow",
        "ground_truth": {
            "priority": Priority.MEDIUM,
            "category": Category.CUSTOMER_SUPPORT,
            "should_escalate": False,
            "key_phrases": ["approval workflow", "audit timestamps", "share examples"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Interested in integration partnership discussion",
        "sender": "alliances@workflowforge.ai",
        "body": (
            "We build procurement automation software and several shared customers have asked whether our systems can connect. "
            "A lightweight integration partnership could be valuable for both teams, especially around invoice syncing. "
            "If someone from business development is available, we would love a short discovery call next week. "
            "Please let me know the appropriate contact."
        ),
        "timestamp": "2026-04-08T13:08:00Z",
        "has_attachment": False,
        "thread_id": "workflowforge-partnership",
        "ground_truth": {
            "priority": Priority.MEDIUM,
            "category": Category.SALES,
            "should_escalate": False,
            "key_phrases": ["integration partnership", "discovery call", "appropriate contact"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Customer asking where attachment previews are stored",
        "sender": "support@blueorbitdesign.com",
        "body": (
            "A client on our team asked whether uploaded attachment previews are stored in the same region as their primary data. "
            "I checked the docs but could not find a direct answer about preview caching. "
            "There is no active complaint or outage, just a data residency question from procurement. "
            "Could you clarify the behavior?"
        ),
        "timestamp": "2026-04-08T13:31:00Z",
        "has_attachment": False,
        "thread_id": "attachment-preview-storage",
        "ground_truth": {
            "priority": Priority.MEDIUM,
            "category": Category.CUSTOMER_SUPPORT,
            "should_escalate": False,
            "key_phrases": ["data residency", "preview caching", "clarify the behavior"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Question about custom SAML attribute mapping",
        "sender": "admin@peaklegalgroup.com",
        "body": (
            "We are turning on SAML next week and noticed that department values are not mapping cleanly in the staging tenant. "
            "It looks like your docs mention custom attributes, but the example is fairly short. "
            "Could support share a recommended attribute mapping format or example payload? "
            "We can continue testing while you respond."
        ),
        "timestamp": "2026-04-08T13:55:00Z",
        "has_attachment": False,
        "thread_id": "saml-attribute-mapping",
        "ground_truth": {
            "priority": Priority.MEDIUM,
            "category": Category.TECHNICAL,
            "should_escalate": False,
            "key_phrases": ["saml", "attribute mapping", "example payload"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Reminder: next week's support operations sync",
        "sender": "maria.fernandez@company.internal",
        "body": (
            "Sharing the agenda for our weekly support operations sync on Tuesday. "
            "We will review backlog aging, staffing for the holiday calendar, and the latest CSAT trends. "
            "No action is needed from you unless there is another topic to add. "
            "Thanks for staying aligned."
        ),
        "timestamp": "2026-04-08T14:12:00Z",
        "has_attachment": False,
        "thread_id": "internal-support-sync",
        "ground_truth": {
            "priority": Priority.LOW,
            "category": Category.INTERNAL,
            "should_escalate": False,
            "key_phrases": ["agenda", "weekly support operations sync", "no action needed"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "FYI: updated company travel and expense policy",
        "sender": "hr@company.internal",
        "body": (
            "HR published a revised travel and expense policy for domestic and international trips. "
            "The main changes are meal caps, receipt requirements, and pre-approval for hotel rates above policy. "
            "Please read it before your next trip, but there is no immediate acknowledgement required. "
            "The full PDF is attached for reference."
        ),
        "timestamp": "2026-04-08T14:27:00Z",
        "has_attachment": True,
        "thread_id": "travel-policy-update",
        "ground_truth": {
            "priority": Priority.LOW,
            "category": Category.INTERNAL,
            "should_escalate": False,
            "key_phrases": ["expense policy", "no immediate acknowledgement", "attached"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Subscribed to weekly release notes",
        "sender": "noreply@newsletter.com",
        "body": (
            "Thanks for subscribing to our weekly release notes digest. "
            "You will receive a summary every Friday with product updates, fixes, and upcoming webinars. "
            "If this was accidental, you can unsubscribe using the link at the bottom of the email."
        ),
        "timestamp": "2026-04-08T14:44:00Z",
        "has_attachment": False,
        "thread_id": "release-notes-subscription",
        "ground_truth": {
            "priority": Priority.LOW,
            "category": Category.CUSTOMER_SUPPORT,
            "should_escalate": False,
            "key_phrases": ["release notes", "unsubscribe", "weekly digest"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Quick check-in on last month's onboarding webinar",
        "sender": "community@saasguild.net",
        "body": (
            "We noticed your team attended the onboarding webinar in March and wanted to see if the recording was helpful. "
            "There is no sales push here, just looking for any feedback we can pass to the training team. "
            "If you have two minutes to reply, we would appreciate it. "
            "Otherwise, no worries."
        ),
        "timestamp": "2026-04-08T15:01:00Z",
        "has_attachment": False,
        "thread_id": "webinar-checkin",
        "ground_truth": {
            "priority": Priority.LOW,
            "category": Category.SALES,
            "should_escalate": False,
            "key_phrases": ["feedback", "training team", "no worries"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Urgent: verify your mailbox to avoid suspension",
        "sender": "security-update@micr0soft-mail.support",
        "body": (
            "Your mailbox will be suspended within 30 minutes unless you confirm your password immediately. "
            "Click the secure verification link below and enter your current credentials to keep access active. "
            "Failure to respond may result in permanent data loss. "
            "This message was sent automatically."
        ),
        "timestamp": "2026-04-08T15:19:00Z",
        "has_attachment": False,
        "thread_id": "phishing-mailbox-suspension",
        "ground_truth": {
            "priority": Priority.SPAM,
            "category": Category.SPAM,
            "should_escalate": False,
            "key_phrases": ["phishing", "do not click", "credentials"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "You have been selected for 10,000,000 USD transfer",
        "sender": "beneficiary@globaltrust-lottery.biz",
        "body": (
            "I am a senior director with a confidential banking opportunity for you. "
            "A dormant account worth 10,000,000 USD can be released if you share your private contact number and a copy of your ID. "
            "This is completely risk free and must remain secret. "
            "Respond today to claim your fortune."
        ),
        "timestamp": "2026-04-08T15:33:00Z",
        "has_attachment": False,
        "thread_id": "lottery-scam",
        "ground_truth": {
            "priority": Priority.SPAM,
            "category": Category.SPAM,
            "should_escalate": False,
            "key_phrases": ["scam", "do not respond", "id"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Mass mailing list purchase for crypto trading leads",
        "sender": "growth@blastmailers.co",
        "body": (
            "We can sell you 500,000 active crypto investor leads with 98 percent open rates. "
            "Our clients use these lists to blast offers and collect instant revenue. "
            "Buy before midnight to unlock a special bulk discount. "
            "Reply with your WhatsApp number for the package list."
        ),
        "timestamp": "2026-04-08T15:47:00Z",
        "has_attachment": False,
        "thread_id": "lead-list-spam",
        "ground_truth": {
            "priority": Priority.SPAM,
            "category": Category.SPAM,
            "should_escalate": False,
            "key_phrases": ["unsolicited", "bulk discount", "do not respond"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Request to reactivate suspended sandbox account",
        "sender": "devops@stellarforms.app",
        "body": (
            "Our sandbox tenant was paused after repeated failed login attempts from our QA team. "
            "We already rotated passwords and believe the lockout was accidental during load testing. "
            "Could someone help us reactivate the tenant or share the self-service steps? "
            "There is no production impact at the moment."
        ),
        "timestamp": "2026-04-08T16:03:00Z",
        "has_attachment": False,
        "thread_id": "sandbox-reactivation",
        "ground_truth": {
            "priority": Priority.MEDIUM,
            "category": Category.TECHNICAL,
            "should_escalate": False,
            "key_phrases": ["reactivate", "self-service steps", "sandbox"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Quarterly business review deck request",
        "sender": "csm@horizonfleet.com",
        "body": (
            "We have our quarterly business review next Wednesday and would like the latest adoption metrics and roadmap slide. "
            "Nothing is broken, but our executive sponsor expects a polished deck. "
            "If customer success already has a standard template, that would save us time. "
            "Please point us in the right direction."
        ),
        "timestamp": "2026-04-08T16:21:00Z",
        "has_attachment": False,
        "thread_id": "qbr-deck-request",
        "ground_truth": {
            "priority": Priority.MEDIUM,
            "category": Category.CUSTOMER_SUPPORT,
            "should_escalate": False,
            "key_phrases": ["adoption metrics", "roadmap slide", "standard template"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Escalation request from Fortune 100 prospect",
        "sender": "vp.procurement@grandvistaenergy.com",
        "body": (
            "We are in final negotiations for a multi-year deal and need written confirmation on your uptime credits and data retention terms. "
            "Our legal review closes tomorrow morning, so unanswered questions could delay signature. "
            "This is commercial rather than operational, but it needs executive attention quickly. "
            "Please involve the right enterprise contact."
        ),
        "timestamp": "2026-04-08T16:39:00Z",
        "has_attachment": False,
        "thread_id": "fortune100-prospect-escalation",
        "ground_truth": {
            "priority": Priority.HIGH,
            "category": Category.SALES,
            "should_escalate": True,
            "key_phrases": ["uptime credits", "data retention terms", "enterprise contact"],
            "escalation_threshold": True,
        },
    },
    {
        "subject": "Refund request after accidental self-serve upgrade",
        "sender": "owner@brightpine.io",
        "body": (
            "I intended to review the Pro plan, but the checkout flow completed before I realized the card on file would be charged immediately. "
            "We have not used any of the new features and would like to reverse the upgrade if possible. "
            "I understand mistakes happen and I am hoping support can help. "
            "Please let me know the refund policy."
        ),
        "timestamp": "2026-04-08T16:58:00Z",
        "has_attachment": False,
        "thread_id": "self-serve-upgrade-refund",
        "ground_truth": {
            "priority": Priority.MEDIUM,
            "category": Category.BILLING,
            "should_escalate": False,
            "key_phrases": ["refund policy", "reverse the upgrade", "support can help"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Security review follow-up for signed DPA",
        "sender": "privacy@northstreamlabs.com",
        "body": (
            "Thanks for sending the DPA last week. "
            "Our privacy counsel has one follow-up question about subprocessors that handle attachment scanning. "
            "We are still comfortable with the rollout timeline and do not need an emergency response. "
            "A written answer in the next day or two would be perfect."
        ),
        "timestamp": "2026-04-08T17:16:00Z",
        "has_attachment": False,
        "thread_id": "dpa-follow-up",
        "ground_truth": {
            "priority": Priority.MEDIUM,
            "category": Category.SALES,
            "should_escalate": False,
            "key_phrases": ["subprocessors", "written answer", "rollout timeline"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Customer reports missing notifications after mobile update",
        "sender": "supportlead@fieldroutepro.com",
        "body": (
            "Three dispatch supervisors say push notifications stopped appearing on iOS after yesterday's mobile update. "
            "The web app still shows the events, so work is continuing, but managers are missing time-sensitive alerts. "
            "We do not yet know if this affects all devices or a subset. "
            "Please investigate and let us know whether engineering needs logs."
        ),
        "timestamp": "2026-04-08T17:39:00Z",
        "has_attachment": False,
        "thread_id": "ios-notification-regression",
        "ground_truth": {
            "priority": Priority.HIGH,
            "category": Category.TECHNICAL,
            "should_escalate": False,
            "key_phrases": ["investigate", "logs", "mobile update"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Please confirm if support can attend customer workshop",
        "sender": "ae@cloudnorth.com",
        "body": (
            "We are hosting a paid workshop with a strategic customer next Thursday and they want a support specialist present for the admin Q&A block. "
            "It is not an urgent incident, but the workshop is important to renewal sentiment. "
            "Could you confirm whether someone from support leadership should be looped in? "
            "I can share the agenda if helpful."
        ),
        "timestamp": "2026-04-08T17:56:00Z",
        "has_attachment": False,
        "thread_id": "customer-workshop-support",
        "ground_truth": {
            "priority": Priority.MEDIUM,
            "category": Category.INTERNAL,
            "should_escalate": False,
            "key_phrases": ["support specialist", "renewal sentiment", "agenda"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Automatic out-of-office reply",
        "sender": "nina@lakesidepartners.com",
        "body": (
            "I am out of the office until Monday and will have limited access to email. "
            "If you need immediate assistance, please contact our shared support desk. "
            "Otherwise I will reply when I return."
        ),
        "timestamp": "2026-04-08T18:14:00Z",
        "has_attachment": False,
        "thread_id": "ooo-nina",
        "ground_truth": {
            "priority": Priority.LOW,
            "category": Category.CUSTOMER_SUPPORT,
            "should_escalate": False,
            "key_phrases": ["out of the office", "limited access", "shared support desk"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Re: can we extend trial by one week?",
        "sender": "founder@tinyatlas.dev",
        "body": (
            "Our engineering team lost two days of testing because a contractor VPN issue blocked staging access. "
            "Would it be possible to extend the trial by one week so we can finish a fair evaluation? "
            "We are a small team and this would help, but it is not a major escalation. "
            "Thanks for considering it."
        ),
        "timestamp": "2026-04-08T18:28:00Z",
        "has_attachment": False,
        "thread_id": "trial-extension-request",
        "ground_truth": {
            "priority": Priority.MEDIUM,
            "category": Category.SALES,
            "should_escalate": False,
            "key_phrases": ["extend the trial", "fair evaluation", "thanks for considering"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Internal note: marketing campaign launch timings",
        "sender": "marketing@company.internal",
        "body": (
            "Tomorrow's launch emails will go out in three waves based on region. "
            "Support may see a temporary rise in inbound questions during the first two hours. "
            "No action is required right now, but we wanted the team to have context. "
            "Please share with any new responders on shift."
        ),
        "timestamp": "2026-04-08T18:41:00Z",
        "has_attachment": False,
        "thread_id": "marketing-launch-fyi",
        "ground_truth": {
            "priority": Priority.LOW,
            "category": Category.INTERNAL,
            "should_escalate": False,
            "key_phrases": ["launch emails", "no action is required", "context"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Patch deployment failed on customer-managed instance",
        "sender": "infra@globalpharma.com",
        "body": (
            "The patch package completed download on our customer-managed instance, but the final migration step failed and left the service in maintenance mode. "
            "Our teams in New York and Singapore are both affected and users cannot access case records right now. "
            "We need immediate guidance on rollback or a supported recovery path. "
            "Please escalate to the deployment engineering team."
        ),
        "timestamp": "2026-04-08T19:03:00Z",
        "has_attachment": True,
        "thread_id": "patch-failed-maintenance-mode",
        "ground_truth": {
            "priority": Priority.URGENT,
            "category": Category.TECHNICAL,
            "should_escalate": True,
            "key_phrases": ["rollback", "recovery path", "deployment engineering"],
            "escalation_threshold": True,
        },
    },
    {
        "subject": "Potential chargeback from dissatisfied SMB customer",
        "sender": "collections@finbridgepay.com",
        "body": (
            "A small business customer is threatening a chargeback after saying they could not cancel before renewal. "
            "They are upset but still engaging, and we have a few days before the payment network deadline. "
            "Could billing support review the timeline and suggest the best next response? "
            "This needs care, though it is not an executive emergency."
        ),
        "timestamp": "2026-04-08T19:20:00Z",
        "has_attachment": False,
        "thread_id": "potential-chargeback",
        "ground_truth": {
            "priority": Priority.HIGH,
            "category": Category.BILLING,
            "should_escalate": False,
            "key_phrases": ["chargeback", "review the timeline", "best next response"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Can support share documentation for audit logs?",
        "sender": "compliance@westbridgecapital.com",
        "body": (
            "Our auditors want a brief explanation of which events are captured in your audit logs and how long they are retained. "
            "I found the admin guide, but it does not clearly spell out retention windows. "
            "A documentation link or concise written answer would be enough. "
            "This is part of a normal review cycle."
        ),
        "timestamp": "2026-04-08T19:42:00Z",
        "has_attachment": False,
        "thread_id": "audit-log-docs",
        "ground_truth": {
            "priority": Priority.MEDIUM,
            "category": Category.CUSTOMER_SUPPORT,
            "should_escalate": False,
            "key_phrases": ["audit logs", "retention windows", "documentation link"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Exclusive SEO backlinks package for SaaS founders",
        "sender": "sales@rankblaze-mailers.info",
        "body": (
            "We guarantee page one search rankings by placing your domain on our private backlink network. "
            "Our agency works with over 12,000 founders and can start your campaign today with no contract. "
            "Reply now for a hidden founder discount and limited-time bonus domains. "
            "This offer expires tonight."
        ),
        "timestamp": "2026-04-08T20:01:00Z",
        "has_attachment": False,
        "thread_id": "seo-spam",
        "ground_truth": {
            "priority": Priority.SPAM,
            "category": Category.SPAM,
            "should_escalate": False,
            "key_phrases": ["spam", "discount", "backlink network"],
            "escalation_threshold": False,
        },
    },
    {
        "subject": "Need a formal incident summary for today's data sync delay",
        "sender": "ops-lead@pinnacleinsure.com",
        "body": (
            "The sync delay this morning appears to be resolved, but our compliance team needs a short incident summary for their records. "
            "Please include impact window, affected records, and whether any manual remediation is still required. "
            "This is important to us, though operations are currently back to normal. "
            "A same-day response would help."
        ),
        "timestamp": "2026-04-08T20:18:00Z",
        "has_attachment": False,
        "thread_id": "incident-summary-request",
        "ground_truth": {
            "priority": Priority.HIGH,
            "category": Category.CUSTOMER_SUPPORT,
            "should_escalate": True,
            "key_phrases": ["incident summary", "impact window", "same-day response"],
            "escalation_threshold": True,
        },
    },
]


TASK_EMAIL_SELECTIONS = {
    "task_1": list(range(0, 10)),
    "task_2": list(range(4, 19)),
    "task_3": list(range(0, 20)),
}


def get_task_email_records(task_id: str) -> List[Dict[str, object]]:
    if task_id not in TASK_EMAIL_SELECTIONS:
        raise KeyError(f"Unknown task_id: {task_id}")

    selected_records: List[Dict[str, object]] = []
    for index, base_index in enumerate(TASK_EMAIL_SELECTIONS[task_id]):
        record = deepcopy(BASE_EMAIL_RECORDS[base_index])
        record["email"] = Email(
            id=f"email_{task_id}_{index}",
            subject=record.pop("subject"),
            sender=record.pop("sender"),
            body=record.pop("body"),
            timestamp=record.pop("timestamp"),
            has_attachment=record.pop("has_attachment", False),
            thread_id=record.pop("thread_id", None),
        )
        selected_records.append(record)
    return selected_records


def get_dataset_size() -> int:
    return len(BASE_EMAIL_RECORDS)
