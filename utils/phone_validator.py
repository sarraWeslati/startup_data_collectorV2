import phonenumbers
from phonenumbers import region_code_for_number


AFRICAN_COUNTRY_CODES = {
    "DZ", "AO", "BJ", "BW", "BF", "BI",
    "CM", "CV", "CF", "TD", "KM", "CG",
    "CD", "CI", "DJ", "EG", "GQ", "ER",
    "SZ", "ET", "GA", "GM", "GH", "GN",
    "GW", "KE", "LS", "LR", "LY", "MG",
    "MW", "ML", "MR", "MU", "MA", "MZ",
    "NA", "NE", "NG", "RW", "ST", "SN",
    "SC", "SL", "SO", "ZA", "SS", "SD",
    "TZ", "TG", "TN", "UG", "ZM", "ZW"
}


def validate_african_phones(
    phones: list[str]
) -> list[str]:

    valid = []

    for phone in phones:

        try:

            number = phonenumbers.parse(
                phone,
                None
            )

            if not phonenumbers.is_valid_number(
                number
            ):
                continue

            country = region_code_for_number(
                number
            )

            if country not in AFRICAN_COUNTRY_CODES:
                continue

            formatted = phonenumbers.format_number(
                number,
                phonenumbers.PhoneNumberFormat.E164
            )

            if formatted not in valid:
                valid.append(formatted)

        except Exception:
            pass

    return valid