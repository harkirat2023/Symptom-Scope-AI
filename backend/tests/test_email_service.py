
from services.email_service import EmailService


class TestEmailSigning:
    def setup_method(self):
        self.svc = EmailService()

    def test_signature_round_trip(self):
        link = self.svc._create_signed_action_link("rem1", "taken", "user1", 48)
        from urllib.parse import parse_qs, urlparse

        qs = parse_qs(urlparse(link).query)
        assert self.svc.verify_action_signature(
            "rem1", "taken", "user1", qs["expires"][0], qs["sig"][0]
        )

    def test_signature_rejects_tampered_action(self):
        link = self.svc._create_signed_action_link("rem1", "taken", "user1", 48)
        from urllib.parse import parse_qs, urlparse

        qs = parse_qs(urlparse(link).query)
        assert not self.svc.verify_action_signature(
            "rem1", "missed", "user1", qs["expires"][0], qs["sig"][0]
        )

    def test_signature_rejects_wrong_user(self):
        link = self.svc._create_signed_action_link("rem1", "taken", "user1", 48)
        from urllib.parse import parse_qs, urlparse

        qs = parse_qs(urlparse(link).query)
        assert not self.svc.verify_action_signature(
            "rem1", "taken", "other", qs["expires"][0], qs["sig"][0]
        )

    def test_signature_rejects_expired(self):
        link = self.svc._create_signed_action_link("rem1", "taken", "user1", -48)
        from urllib.parse import parse_qs, urlparse

        qs = parse_qs(urlparse(link).query)
        assert not self.svc.verify_action_signature(
            "rem1", "taken", "user1", qs["expires"][0], qs["sig"][0]
        )

    def test_link_points_to_backend_route(self):
        link = self.svc._create_signed_action_link("rem1", "taken", "user1", 48)
        assert "/api/v1/reminders/rem1/action" in link
        assert "action=taken" in link
        assert "sig=" in link

    def test_not_configured_when_no_smtp(self):
        assert self.svc.configured() is False