from odoo import _, api, models
from odoo.exceptions import RedirectWarning


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
                        "title": _("Possible duplicate found"),
                        "message": _(
                            "%(reason)s\nExisting record: %(name)s (ID: %(id)s)"
                        )
                        % {"reason": reason, "name": duplicate.display_name, "id": duplicate.id},
                    }
                }

    def _normalize(self, value):
        return (value or "").strip().lower()

    def _normalize_stripped(self, value):
        return (value or "").strip()

    def _normalize_name_key(self, value):
        # Normalize case and repeated spaces so "Tatenda  Tembo" == "tatenda tembo"
        return " ".join((value or "").split()).casefold()

    def _is_feature_enabled(self, key, default="True"):
        return self.env["ir.config_parameter"].sudo().get_param(key, default) == "True"

    def _find_duplicate_candidate(self, data, current_id=False):
        domain_base = [("active", "in", [True, False])]
        if current_id:
            domain_base.append(("id", "!=", current_id))

        name_exact = self._normalize_stripped(data.get("name"))
        name_ci = self._normalize(data.get("name"))
        email = self._normalize(data.get("email"))
        phone = self._normalize(data.get("phone"))
        street = self._normalize(data.get("street"))
        city = self._normalize(data.get("city"))

        if name_exact and self._is_feature_enabled("disallow_duplicate_contacts.check_name_exact"):
            normalized_input_name = self._normalize_name_key(name_exact)
            candidates = self.search(domain_base + [("name", "=ilike", name_exact)], limit=20)
            dup = next((partner for partner in candidates if self._normalize_name_key(partner.name) == normalized_input_name), False)
            if dup:
                return dup, _("Duplicate contact found by exact Name match.")

        if email and self._is_feature_enabled("disallow_duplicate_contacts.check_email_only"):
            dup = self.search(domain_base + [("email", "=ilike", email)], limit=1)
            if dup:
                return dup, _("Duplicate contact found by Email only.")

        if name_ci and email and self._is_feature_enabled("disallow_duplicate_contacts.check_email_name"):
            dup = self.search(domain_base + [("name", "=ilike", name_ci), ("email", "=ilike", email)], limit=1)
            if dup:
                return dup, _("Duplicate contact found by Name + Email.")

        if phone and self._is_feature_enabled("disallow_duplicate_contacts.check_phone_only"):
            dup = self.search(domain_base + [("phone", "=ilike", phone)], limit=1)
            if dup:
                return dup, _("Duplicate contact found by Phone only.")

        if name_ci and phone and self._is_feature_enabled("disallow_duplicate_contacts.check_phone_name"):
            dup = self.search(domain_base + [("name", "=ilike", name_ci), ("phone", "=ilike", phone)], limit=1)
            if dup:
                return dup, _("Duplicate contact found by Name + Phone.")

        if name_ci and street and city and self._is_feature_enabled("disallow_duplicate_contacts.check_name_address"):
            dup = self.search(
                domain_base + [("name", "=ilike", name_ci), ("street", "=ilike", street), ("city", "=ilike", city)],
                limit=1,
            )
            if dup:
                return dup, _("Duplicate contact found by Name + Address.")
        return False, False

    def _raise_if_duplicate_for_values(self, data, current_id=False):
        duplicate, reason = self._find_duplicate_candidate(data, current_id=current_id)
        if duplicate:
            action = self.env.ref("disallow_duplicate_contacts.action_ddc_open_duplicate_partner")
            raise RedirectWarning(
                _("%(reason)s Existing record: %(name)s (ID: %(id)s).")
                % {"reason": reason, "name": duplicate.display_name, "id": duplicate.id},
                action.id,
                _("View Duplicate"),
                {"active_ids": [duplicate.id], "active_id": duplicate.id},
            )
