from odoo import _, api, models
from odoo.exceptions import UserError, RedirectWarning


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model_create_multi
    def create(self, vals_list):
        if self.env["no.duplicate.license.manager"]._is_license_valid():
            for vals in vals_list:
                self._raise_if_duplicate_for_values(vals)
        return super().create(vals_list)

    def write(self, vals):
        if self.env["no.duplicate.license.manager"]._is_license_valid():
            for partner in self:
                merged_vals = {
                    "name": vals.get("name", partner.name),
                    "email": vals.get("email", partner.email),
                    "phone": vals.get("phone", partner.phone),
                    "street": vals.get("street", partner.street),
                    "city": vals.get("city", partner.city),
                }
                self._raise_if_duplicate_for_values(merged_vals, current_id=partner.id)
        return super().write(vals)

    @api.model
    def name_create(self, name):
        if self.env["no.duplicate.license.manager"]._is_license_valid():
            self._raise_if_duplicate_for_values({"name": name})
        return super().name_create(name)

    @api.onchange("name", "email", "phone", "street", "city")
    def _onchange_duplicate_preview(self):
        """Show a silent banner warning on the form without blocking save."""
        if not self.env["no.duplicate.license.manager"]._is_license_valid():
            return
        for partner in self:
            duplicate, reason = partner._find_duplicate_candidate(
                {
                    "name": partner.name,
                    "email": partner.email,
                    "phone": partner.phone,
                    "street": partner.street,
                    "city": partner.city,
                },
                current_id=partner.id,
            )
            if duplicate:
                return {
                    "warning": {
                        "title": _("⚠️ Possible Duplicate Found"),
                        "message": _(
                            "%(reason)s\n\n"
                            "Existing contact: %(name)s (ID: %(id)s)\n\n"
                            "Please review the existing contact before saving."
                        )
                        % {
                            "reason": reason,
                            "name": duplicate.display_name,
                            "id": duplicate.id,
                        },
                    }
                }

    # ============================================================
    # Normalization Helpers
    # ============================================================

    def _normalize(self, value):
        """Normalize to lowercase and strip whitespace."""
        return (value or "").strip().lower()

    def _normalize_stripped(self, value):
        """Strip whitespace only (case-sensitive)."""
        return (value or "").strip()

    def _normalize_name_key(self, value):
        """Normalize case and collapse repeated spaces so 'Tatenda  Tembo' == 'tatenda tembo'."""
        return " ".join((value or "").split()).casefold()

    # ============================================================
    # Feature Flag Check
    # ============================================================

    def _is_feature_enabled(self, key, default="True"):
        """Check if a detection rule is enabled in system parameters."""
        return self.env["ir.config_parameter"].sudo().get_param(key, default) == "True"

    # ============================================================
    # Duplicate Detection Logic
    # ============================================================

    def _find_duplicate_candidate(self, data, current_id=False):
        """
        Check for duplicate contacts based on enabled detection rules.
        
        Returns:
            tuple: (duplicate_record, reason_string) or (False, False)
        """
        domain_base = [("active", "in", [True, False])]
        if current_id:
            domain_base.append(("id", "!=", current_id))

        name_exact = self._normalize_stripped(data.get("name"))
        name_ci = self._normalize(data.get("name"))
        email = self._normalize(data.get("email"))
        phone = self._normalize(data.get("phone"))
        street = self._normalize(data.get("street"))
        city = self._normalize(data.get("city"))

        # 1. Exact Name Match
        if name_exact and self._is_feature_enabled("disallow_duplicate_contacts.check_name_exact"):
            normalized_input_name = self._normalize_name_key(name_exact)
            candidates = self.search(
                domain_base + [("name", "=ilike", name_exact)], limit=20
            )
            dup = next(
                (
                    partner
                    for partner in candidates
                    if self._normalize_name_key(partner.name) == normalized_input_name
                ),
                False,
            )
            if dup:
                return dup, _("Duplicate contact found by exact Name match.")

        # 2. Email Only
        if email and self._is_feature_enabled("disallow_duplicate_contacts.check_email_only"):
            dup = self.search(domain_base + [("email", "=ilike", email)], limit=1)
            if dup:
                return dup, _("Duplicate contact found by Email only.")

        # 3. Name + Email
        if name_ci and email and self._is_feature_enabled("disallow_duplicate_contacts.check_email_name"):
            dup = self.search(
                domain_base + [("name", "=ilike", name_ci), ("email", "=ilike", email)],
                limit=1,
            )
            if dup:
                return dup, _("Duplicate contact found by Name + Email.")

        # 4. Phone Only
        if phone and self._is_feature_enabled("disallow_duplicate_contacts.check_phone_only"):
            dup = self.search(domain_base + [("phone", "=ilike", phone)], limit=1)
            if dup:
                return dup, _("Duplicate contact found by Phone only.")

        # 5. Name + Phone
        if name_ci and phone and self._is_feature_enabled("disallow_duplicate_contacts.check_phone_name"):
            dup = self.search(
                domain_base + [("name", "=ilike", name_ci), ("phone", "=ilike", phone)],
                limit=1,
            )
            if dup:
                return dup, _("Duplicate contact found by Name + Phone.")

        # 6. Name + Street + City
        if name_ci and street and city and self._is_feature_enabled("disallow_duplicate_contacts.check_name_address"):
            dup = self.search(
                domain_base
                + [
                    ("name", "=ilike", name_ci),
                    ("street", "=ilike", street),
                    ("city", "=ilike", city),
                ],
                limit=1,
            )
            if dup:
                return dup, _("Duplicate contact found by Name + Address.")

        return False, False

    # ============================================================
    # Raise Error on Duplicate (Create/Write/Name Create)
    # ============================================================

    def _raise_if_duplicate_for_values(self, data, current_id=False):
        """
        Raise a RedirectWarning when a duplicate is detected.
        This shows Odoo's native dialog with a 'View Duplicate' button.
        """
        duplicate, reason = self._find_duplicate_candidate(data, current_id=current_id)
        if duplicate:
            action = self.env.ref(
                "disallow_duplicate_contacts.action_ddc_open_duplicate_partner"
            )
            raise RedirectWarning(
                _(
                    "⚠️ Duplicate Contact Detected!\n\n"
                    "%(reason)s\n\n"
                    "Existing contact: %(name)s (ID: %(id)s)\n\n"
                    "Click 'View Duplicate' to review the existing contact, "
                    "or go back and modify your entry."
                )
                % {
                    "reason": reason,
                    "name": duplicate.display_name,
                    "id": duplicate.id,
                },
                action.id,
                _("View Duplicate"),
                {"active_ids": [duplicate.id], "active_id": duplicate.id},
            )