from pydantic import BaseModel


# ============================================================
# USER SCHEMAS
# ============================================================
class UserCreate(BaseModel):
    username: str
    password: str
    parent_id: int | None = None


class UserLogin(BaseModel):
    username: str
    password: str


class XPUpdate(BaseModel):
    xp: int


class UserOut(BaseModel):
    id: int
    username: str
    xp: int
    parent_id: int | None

    class Config:
        from_attributes = True


# ============================================================
# BRAND PROFILE
# ============================================================
class BrandProfileOut(BaseModel):
    domain: str
    bank_name: str
    legal_name: str | None = None
    logo_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    address: str | None = None
    support_hours: str | None = None
    pof_header_text: str | None = None
    mortgage_header_text: str | None = None
    check_template: str | None = None

    class Config:
        from_attributes = True


# ============================================================
# USER VAULT
# ============================================================
class UserVaultOut(BaseModel):
    id: int
    user_id: int
    cash_balance: int
    crypto_balance: int
    reo_equity: int
    domain_value: int
    total_liabilities: int
    encrypted_ledger_blob: bytes | None = None

    class Config:
        from_attributes = True


# ============================================================
# MORTGAGE APPLICATION
# ============================================================
class MortgageApplicationCreate(BaseModel):
    full_name: str
    dob: str
    address: str
    employment_status: str

    base_income: int
    gig_income: int = 0
    referral_income: int = 0
    other_income: int = 0

    monthly_debt: int

    loan_purpose: str
    property_type: str
    property_value: int
    requested_loan_amount: int


class MortgageApplicationOut(BaseModel):
    id: int
    user_id: int
    dti: float
    capacity_balance: int
    total_monthly_income: int
    monthly_debt: int
    loan_purpose: str
    property_type: str
    property_value: int
    requested_loan_amount: int

    class Config:
        from_attributes = True


# ============================================================
# PROOF OF FUNDS
# ============================================================
class ProofOfFundsOut(BaseModel):
    user_id: int
    bank_name: str
    capacity_balance: int
    issued_at: str
    verification_id: str
    letter: str

    class Config:
        from_attributes = True


# ============================================================
# LOAN ESTIMATE
# ============================================================
class LoanEstimateCreate(BaseModel):
    interest_rate: float
    term_months: int


class LoanEstimateOut(BaseModel):
    id: int
    mortgage_application_id: int
    loan_amount: int
    interest_rate: float
    term_months: int
    estimated_closing_costs: int
    estimated_prepaids: int
    estimated_escrows: int
    lender_credits: int
    seller_credits: int
    estimated_cash_to_close: int

    class Config:
        from_attributes = True


# ============================================================
# CLOSING DISCLOSURE
# ============================================================
class ClosingDisclosureOut(BaseModel):
    id: int
    mortgage_application_id: int
    final_loan_amount: int
    final_interest_rate: float
    final_term_months: int
    total_closing_costs: int
    total_prepaids: int
    total_escrows: int
    lender_credits: int
    seller_credits: int
    cash_to_close: int

    class Config:
        from_attributes = True


# ============================================================
# DISBURSEMENT CHECKS
# ============================================================
class DisbursementCheckOut(BaseModel):
    id: int | None = None
    payee: str
    amount: int
    purpose: str
    funding_source: str

    class Config:
        from_attributes = True


# ============================================================
# DIGITAL ASSETS
# ============================================================
class DigitalAssetCreate(BaseModel):
    asset_type: str
    identifier: str
    metadata: str | None = None


class DigitalAssetOut(BaseModel):
    id: int
    asset_type: str
    identifier: str
    metadata: str | None
    estimated_value: int

    class Config:
        from_attributes = True
