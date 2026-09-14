from decimal import Decimal
import unittest

from seekerlab.modules.campaigns.domain import (
    Conflict, DomainError, clean_feedback, ensure_can_submit, validate_reward,
)


class CampaignRulesTest(unittest.TestCase):
    def test_positive_reward_accepts_exact_decimal(self):
        validate_reward(Decimal("0.000001"))
        validate_reward(Decimal("3.120000"))

    def test_invalid_rewards_rejected(self):
        for value in ("0", "-1", "100001", "NaN", "Infinity", "0.0000001"):
            with self.subTest(value=value), self.assertRaises(DomainError):
                validate_reward(Decimal(value))

    def test_available_campaign_accepts_submission(self):
        ensure_can_submit("open", 19, 20, False)

    def test_duplicate_submission_rejected(self):
        with self.assertRaises(Conflict):
            ensure_can_submit("open", 0, 20, True)

    def test_full_campaign_rejected(self):
        with self.assertRaises(Conflict):
            ensure_can_submit("open", 20, 20, False)

    def test_closed_campaign_rejected(self):
        with self.assertRaises(Conflict):
            ensure_can_submit("closed", 0, 20, False)

    def test_feedback_is_trimmed(self):
        self.assertEqual(clean_feedback("  A concrete observation about the application.  "),
                         "A concrete observation about the application.")

    def test_feedback_bounds_after_trimming(self):
        for value in (" " * 30, "too short", "x" * 5001):
            with self.subTest(length=len(value)), self.assertRaises(DomainError):
                clean_feedback(value)


if __name__ == "__main__":
    unittest.main()
