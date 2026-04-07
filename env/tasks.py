"""
Task definitions for the Email Triage environment.
Each task contains a dataset of emails, expected outputs, and a grader function.
"""

from typing import Any


# ---------------------------------------------------------------------------
# Task 1 – EASY: Obvious Spam
# ---------------------------------------------------------------------------

EASY_TASK = {
    "name": "easy_spam_detection",
    "description": "Classify a batch of obviously spam and legitimate emails.",
    "difficulty": "easy",
    "dataset": [
        {
            "email_id": "e001",
            "sender": "winner@lottery-claim-now.xyz",
            "subject": "YOU HAVE WON $5,000,000!!!",
            "email_text": (
                "Congratulations! You have been selected as our LUCKY WINNER! "
                "Click here immediately to claim your $5,000,000 prize. "
                "Send us your bank details and social security number to process the transfer."
            ),
            "urgency": "low",
            "expected_label": "spam",
            "expected_urgency_action": "ignore",
        },
        {
            "email_id": "e002",
            "sender": "noreply@viagraonline-deals.net",
            "subject": "Special offer just for you!!!",
            "email_text": (
                "Buy cheap medications online! No prescription needed. "
                "50% off Viagra, Cialis, and more! Limited time offer. "
                "Click now: http://bit.ly/totally-not-sketchy"
            ),
            "urgency": "low",
            "expected_label": "spam",
            "expected_urgency_action": "ignore",
        },
        {
            "email_id": "e003",
            "sender": "alice.chen@mycompany.com",
            "subject": "Q3 Budget Review – Action Required",
            "email_text": (
                "Hi team, please review the attached Q3 budget report before our meeting "
                "tomorrow at 10am. We need sign-off from all department heads. "
                "This is time-sensitive."
            ),
            "urgency": "high",
            "expected_label": "important",
            "expected_urgency_action": "respond",
        },
        {
            "email_id": "e004",
            "sender": "prince.nigerian@royalfamily.org",
            "subject": "Confidential Business Proposal",
            "email_text": (
                "Dear Friend, I am Prince Emmanuel of Nigeria. I need to transfer "
                "$20 million USD to a safe account. You will receive 30% commission. "
                "Please reply with your full name, address, and bank account number."
            ),
            "urgency": "low",
            "expected_label": "spam",
            "expected_urgency_action": "ignore",
        },
        {
            "email_id": "e005",
            "sender": "bob.smith@client-corp.com",
            "subject": "Contract renewal discussion",
            "email_text": (
                "Hello, I wanted to follow up on the contract renewal we discussed last week. "
                "Our legal team has reviewed the terms and we're ready to proceed. "
                "Can we schedule a call this week?"
            ),
            "urgency": "medium",
            "expected_label": "important",
            "expected_urgency_action": "respond",
        },
    ],
}


# ---------------------------------------------------------------------------
# Task 2 – MEDIUM: Promotion vs Important
# ---------------------------------------------------------------------------

MEDIUM_TASK = {
    "name": "medium_promo_vs_important",
    "description": "Distinguish between promotional emails and genuinely important ones.",
    "difficulty": "medium",
    "dataset": [
        {
            "email_id": "m001",
            "sender": "deals@amazon.com",
            "subject": "Your exclusive Prime Day deals are here!",
            "email_text": (
                "Hi valued customer, Prime Day is almost here! Enjoy up to 70% off "
                "thousands of items. Shop electronics, fashion, home goods and more. "
                "Deals start July 11 at midnight. Shop now!"
            ),
            "urgency": "low",
            "expected_label": "promotion",
            "expected_urgency_action": "ignore",
        },
        {
            "email_id": "m002",
            "sender": "hr@mycompany.com",
            "subject": "Annual performance review – please complete by Friday",
            "email_text": (
                "Dear employee, your annual performance self-review is due by Friday 5pm. "
                "Please log into the HR portal and complete all sections. "
                "Failure to submit on time may affect your promotion eligibility."
            ),
            "urgency": "high",
            "expected_label": "important",
            "expected_urgency_action": "respond",
        },
        {
            "email_id": "m003",
            "sender": "newsletter@techcrunch.com",
            "subject": "This week in tech: AI, funding rounds, and more",
            "email_text": (
                "Good morning! Here's your weekly digest. OpenAI raises $6B. "
                "Apple releases new MacBook Pro. Startups to watch in Q4. "
                "Read the full stories on TechCrunch."
            ),
            "urgency": "low",
            "expected_label": "promotion",
            "expected_urgency_action": "ignore",
        },
        {
            "email_id": "m004",
            "sender": "security@mybank.com",
            "subject": "Action required: Unusual login attempt detected",
            "email_text": (
                "We detected a login attempt to your account from an unrecognized device "
                "in a different country. If this was not you, please secure your account "
                "immediately by resetting your password and contacting support."
            ),
            "urgency": "high",
            "expected_label": "important",
            "expected_urgency_action": "respond",
        },
        {
            "email_id": "m005",
            "sender": "offers@spotify.com",
            "subject": "3 months of Premium for just $0.99!",
            "email_text": (
                "Switch to Spotify Premium today and get your first 3 months for just $0.99. "
                "Enjoy ad-free music, offline downloads, and unlimited skips. "
                "Offer valid until end of month."
            ),
            "urgency": "low",
            "expected_label": "promotion",
            "expected_urgency_action": "ignore",
        },
        {
            "email_id": "m006",
            "sender": "legal@partnerco.com",
            "subject": "NDA Amendment – signature required",
            "email_text": (
                "Please find attached the amended NDA for the partnership agreement. "
                "Our lawyers have updated Section 4.2 regarding data sharing. "
                "We need your countersignature before we can proceed with the integration."
            ),
            "urgency": "high",
            "expected_label": "important",
            "expected_urgency_action": "respond",
        },
    ],
}


# ---------------------------------------------------------------------------
# Task 3 – HARD: Ambiguous Emails
# ---------------------------------------------------------------------------

HARD_TASK = {
    "name": "hard_ambiguous_reasoning",
    "description": "Handle ambiguous emails where context and reasoning are required.",
    "difficulty": "hard",
    "dataset": [
        {
            "email_id": "h001",
            "sender": "newsletter@linkedin.com",
            "subject": "You appeared in 14 searches this week",
            "email_text": (
                "Your profile was viewed by 14 recruiters this week. "
                "One of them works at Google and another at Stripe. "
                "Upgrade to Premium to see who viewed your profile and reach out."
            ),
            "urgency": "low",
            "expected_label": "promotion",
            "expected_urgency_action": "ignore",
            "reasoning": "Looks important but it's a LinkedIn upsell/promotion.",
        },
        {
            "email_id": "h002",
            "sender": "do-not-reply@paypal.com",
            "subject": "You sent a payment of $499 to TechStore",
            "email_text": (
                "You've sent $499.00 to TechStore (techstore@example.com). "
                "If you did not authorize this transaction, please contact us immediately. "
                "Transaction ID: PP-8823-4421."
            ),
            "urgency": "high",
            "expected_label": "important",
            "expected_urgency_action": "respond",
            "reasoning": "Transaction confirmation that may indicate fraud – must act.",
        },
        {
            "email_id": "h003",
            "sender": "no-reply@github.com",
            "subject": "Action required: Your repository will be archived",
            "email_text": (
                "Your repository 'awesome-project' has had no activity for 12 months. "
                "It will be automatically archived in 30 days unless you push a commit. "
                "If you want to keep it active, please make a change before the deadline."
            ),
            "urgency": "medium",
            "expected_label": "important",
            "expected_urgency_action": "respond",
            "reasoning": "Automated but requires action to prevent data archival.",
        },
        {
            "email_id": "h004",
            "sender": "ceo@mycompany.com",
            "subject": "Quick favor",
            "email_text": (
                "Hey, I'm in a board meeting and can't talk. I need you to urgently "
                "buy 10 Amazon gift cards worth $100 each and send me the codes. "
                "Will reimburse you right away. Thanks!"
            ),
            "urgency": "high",
            "expected_label": "spam",
            "expected_urgency_action": "ignore",
            "reasoning": "Classic CEO gift card phishing scam despite appearing to be from CEO.",
        },
        {
            "email_id": "h005",
            "sender": "support@slack.com",
            "subject": "Your Slack workspace is approaching its storage limit",
            "email_text": (
                "Your workspace 'Acme Corp' has used 95% of its available file storage. "
                "To avoid disruptions, please upgrade your plan or delete old files. "
                "Current plan: Free. Storage used: 4.75 GB of 5 GB."
            ),
            "urgency": "medium",
            "expected_label": "important",
            "expected_urgency_action": "respond",
            "reasoning": "Operational alert – ignoring it will disrupt team communication.",
        },
        {
            "email_id": "h006",
            "sender": "offers@traveldeals.co",
            "subject": "Last-minute flights to Bali from $299",
            "email_text": (
                "Escape this winter! Flights to Bali from New York for just $299 round trip. "
                "Book in the next 2 hours for this flash sale price. Hotels from $49/night. "
                "Use code BALI2024 at checkout."
            ),
            "urgency": "low",
            "expected_label": "promotion",
            "expected_urgency_action": "ignore",
            "reasoning": "Artificial urgency tactic – it's a travel promotion.",
        },
        {
            "email_id": "h007",
            "sender": "ops-alerts@pagerduty.com",
            "subject": "[CRITICAL] Production database CPU at 98%",
            "email_text": (
                "ALERT: Your production PostgreSQL database (db-prod-01) has been at 98% CPU "
                "for the past 15 minutes. Active connections: 492/500. "
                "Incident ID: INC-20241107-0042. Acknowledge or escalate immediately."
            ),
            "urgency": "high",
            "expected_label": "important",
            "expected_urgency_action": "respond",
            "reasoning": "System-critical alert requiring immediate human response.",
        },
    ],
}

ALL_TASKS = {
    "easy": EASY_TASK,
    "medium": MEDIUM_TASK,
    "hard": HARD_TASK,
}


# ---------------------------------------------------------------------------
# Grader functions
# ---------------------------------------------------------------------------

def _score_response(action_response: str, expected_urgency_action: str) -> tuple[float, str]:
    """Score the optional_response field."""
    needs_response = expected_urgency_action == "respond"

    if not needs_response:
        # Email doesn't need a response; penalize a random/spam-like reply
        if action_response and len(action_response.strip()) > 10:
            return -0.1, "Unnecessary response on low-priority email."
        return 0.0, "No response needed – correctly omitted."

    # Email needs a response
    if not action_response or len(action_response.strip()) < 10:
        return 0.0, "Response required but missing or too short."

    # Check response quality: at least somewhat substantive
    words = action_response.strip().split()
    if len(words) >= 5:
        return 0.1, "Response provided and meets quality threshold."
    return 0.05, "Response provided but could be more detailed."


def grade_step(email: dict[str, Any], action: dict[str, Any]) -> dict[str, Any]:
    """
    Deterministic grader for a single email + action pair.
    Returns classification_score, urgency_score, response_score, total, feedback.

    The total is clamped strictly within (0.001, 0.999) so that any aggregated
    task score computed by the evaluator is always strictly within (0, 1).
    """
    label = action.get("label", "")
    response = action.get("optional_response") or ""
    expected_label = email["expected_label"]
    expected_urgency_action = email["expected_urgency_action"]

    # Classification score
    if label == expected_label:
        classification_score = 0.7
        class_feedback = f"Correct label '{label}'."
    else:
        classification_score = 0.0
        class_feedback = f"Wrong label '{label}', expected '{expected_label}'."

    # Urgency score: only awarded if classification is also correct
    if classification_score > 0 and email["urgency"] == "high" and expected_urgency_action == "respond":
        urgency_score = 0.2
        urgency_feedback = "Correctly identified high-urgency email."
    elif classification_score > 0 and email["urgency"] in ("low", "medium") and expected_urgency_action == "ignore":
        urgency_score = 0.2
        urgency_feedback = "Correctly handled low/medium urgency email."
    else:
        urgency_score = 0.0
        urgency_feedback = "Urgency not handled correctly."

    # Response score
    response_score, response_feedback = _score_response(response, expected_urgency_action)

    # Penalty for garbage responses combined with wrong classification
    if classification_score == 0.0 and response and len(response.split()) < 3:
        response_score = -0.2
        response_feedback = "Random/spam-like response with wrong classification."

    total = round(classification_score + urgency_score + response_score, 3)
    total = max(-0.2, min(1.0, total))  # clamp to valid reward range

    # Ensure the task-level score (average of step totals) is always strictly
    # within (0, 1).  We normalise the raw total into (0.001, 0.999) so that
    # ANY average of step scores is also in (0.001, 0.999) ⊂ (0, 1).
    # raw range is [-0.2, 1.0] → map to [0.001, 0.999]
    _lo, _hi = -0.2, 1.0
    _out_lo, _out_hi = 0.001, 0.999
    normalised = _out_lo + (_out_hi - _out_lo) * (total - _lo) / (_hi - _lo)
    normalised = round(max(_out_lo, min(_out_hi, normalised)), 4)

    feedback = f"{class_feedback} {urgency_feedback} {response_feedback}"

    return {
        "classification_score": classification_score,
        "urgency_score": urgency_score,
        "response_score": response_score,
        "total": normalised,
        "feedback": feedback.strip(),
    }


def grade_episode(task_name: str, actions: list[dict]) -> float:
    """
    Grade a full episode and return a score strictly within (0, 1).
    """
    task = ALL_TASKS[task_name]
    dataset = task["dataset"]
    if not dataset or not actions:
        return 0.001  # never return exactly 0.0

    total_score = 0.0
    max_possible = len(dataset) * 0.999  # max per step after normalisation

    for email, action in zip(dataset, actions):
        result = grade_step(email, action)
        total_score += max(0.001, result["total"])  # floor at 0.001 for episode scoring

    raw = total_score / max_possible
    # clamp strictly within (0, 1)
    return round(max(0.001, min(0.999, raw)), 4)