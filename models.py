from sqlalchemy import Column, Integer, String, ForeignKey, Float, LargeBinary
from sqlalchemy.orm import relationship
from database import Base


# ============================================================
# USER
# ============================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    parent_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    xp = Column(Integer, default=0)

    parent = relationship("User", remote_side=[id])
    vault = relationship("UserVault", back_populates="user", uselist=False)
    digital_assets = relationship("DigitalAsset", back_populates="user")
    applications = relationship("MortgageApplication", back_populates="user")


# ============================================================
# BRAND PROFILE
# ============================================================
class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id = Column(Integer, primary_key=True)
    domain = Column(String, unique=True, index=True)
    bank_name = Column(String)
    legal_name = Column(String)
    logo_url = Column(String)
    primary_color = Column(String)
    secondary_color = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    address = Column(String)
    support_hours = Column(String)
    pof_header_text = Column(String)
    mortgage_header_text = Column(String)
    check_template = Column(String)


# ============================================================
# USER VAULT
# ============================================================
class UserVault(Base):
    __tablename__ = "user_vaults"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    cash_balance = Column(Integer, default=0)
    crypto_balance = Column(Integer, default=0)
    reo_equity = Column(Integer, default=0)
    domain_value = Column(Integer, default=0)
    total_liabilities = Column(Integer, default=0)

    encrypted_ledger_blob = Column(LargeBinary, nullable=True)

    user = relationship("User", back_populates="vault")


# ============================================================
# MORTGAGE APPLICATION
# ============================================================
class MortgageApplication(Base):
    __tablename__ = "mortgage_applications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    full_name = Column(String)
    dob = Column(String)
    address = Column(String)
    employment_status = Column(String)

    base_income = Column(Integer)
    gig_income = Column(Integer, default=0)
    referral_income = Column(Integer, default=0)
    other_income = Column(Integer, default=0)

    monthly_debt = Column(Integer)

    loan_purpose = Column(String)
    property_type = Column(String)
    property_value = Column(Integer)
    requested_loan_amount = Column(Integer)

    user = relationship("User", back_populates="applications")
    loan_estimates = relationship("LoanEstimate", back_populates="application")
    closing_disclosures = relationship("ClosingDisclosure", back_populates="application")


# ============================================================
# LOAN ESTIMATE
# ============================================================
class LoanEstimate(Base):
    __tablename__ = "loan_estimates"

    id = Column(Integer, primary_key=True)
    mortgage_application_id = Column(Integer, ForeignKey("mortgage_applications.id"))

    loan_amount = Column(Integer)
    interest_rate = Column(Float)
    term_months = Column(Integer)

    estimated_closing_costs = Column(Integer)
    estimated_prepaids = Column(Integer)
    estimated_escrows = Column(Integer)
    lender_credits = Column(Integer)
    seller_credits = Column(Integer)
    estimated_cash_to_close = Column(Integer)

    application = relationship("MortgageApplication", back_populates="loan_estimates")


# ============================================================
# CLOSING DISCLOSURE
# ============================================================
class ClosingDisclosure(Base):
    __tablename__ = "closing_disclosures"

    id = Column(Integer, primary_key=True)
    mortgage_application_id = Column(Integer, ForeignKey("mortgage_applications.id"))

    final_loan_amount = Column(Integer)
    final_interest_rate = Column(Float)
    final_term_months = Column(Integer)

    total_closing_costs = Column(Integer)
    total_prepaids = Column(Integer)
    total_escrows = Column(Integer)
    lender_credits = Column(Integer)
    seller_credits = Column(Integer)
    cash_to_close = Column(Integer)

    application = relationship("MortgageApplication", back_populates="closing_disclosures")
    checks = relationship("DisbursementCheck", back_populates="closing_disclosure")


# ============================================================
# DISBURSEMENT CHECKS
# ============================================================
class DisbursementCheck(Base):
    __tablename__ = "disbursement_checks"

    id = Column(Integer, primary_key=True)
    closing_disclosure_id = Column(Integer, ForeignKey("closing_disclosures.id"))

    payee = Column(String)
    amount = Column(Integer)
    purpose = Column(String)
    funding_source = Column(String)

    closing_disclosure = relationship("ClosingDisclosure", back_populates="checks")


# ============================================================
# DIGITAL ASSETS
# ============================================================
class DigitalAsset(Base):
    __tablename__ = "digital_assets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    asset_type = Column(String)
    identifier = Column(String)
    metadata = Column(String)
    estimated_value = Column(Integer)

    user = relationship("User", back_populates="digital_assets")
