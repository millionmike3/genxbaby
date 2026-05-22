from datetime import datetime
import uuid
from io import BytesIO

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

from database import Base, engine, SessionLocal
from models import (
    User,
    BrandProfile,
    UserVault,
    MortgageApplication,
    LoanEstimate,
    ClosingDisclosure,
    DisbursementCheck,
    DigitalAsset,
)
from schemas import (
    UserCreate,
    XPUpdate,
    BrandProfileOut,
    UserVaultOut,
    MortgageApplicationCreate,
    MortgageApplicationOut,
    LoanEstimateCreate,
    LoanEstimateOut,
    ClosingDisclosureOut,
    DisbursementCheckOut,
    DigitalAssetOut,
    DigitalAssetCreate,
    ProofOfFundsOut,
)

# ============================================================
# APP INIT
# ============================================================
app = FastAPI(title="GenXBaby Finance Network")


# ============================================================
# DB DEPENDENCY
# ============================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================
# PDF BUILDER
# ============================================================
def build_simple_pdf(lines: list[str]) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    y = height - 72
    for line in lines:
        if y < 72:
            c.showPage()
            y = height - 72
        c.drawString(72, y, line)
        y -= 14

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# ============================================================
# BRAND LOADER
# ============================================================
def get_brand_for_request(request: Request, db: Session):
    host = request.headers.get("host", "")
    domain = host.split(":")[0].lower()

    brand = db.query(BrandProfile).filter(BrandProfile.domain == domain).first()

    if not brand:
        brand = db.query(BrandProfile).filter(BrandProfile.domain == "genxbaby.com").first()

    if not brand:
        brand = BrandProfile(
            domain="substantialfunding.com",
            bank_name="Substantial Funding",
            legal_name="Substantial Funding, Inc.",
            contact_email="helpdesk@substantialfunding.com",
            contact_phone="(914) 200-1566",
            address="(Update with official mailing address)",
            pof_header_text="Substantial Funding • PROOF OF FUNDS",
        )
        db.add(brand)
        db.commit()
        db.refresh(brand)

    return brand


# ============================================================
# ROOT
# ============================================================
@app.get("/")
def root():
    return {"message": "Hello World"}


# ============================================================
# BRAND PROFILE
# ============================================================
@app.get("/brand-profile", response_model=BrandProfileOut)
def read_brand_profile(request: Request, db: Session = Depends(get_db)):
    return get_brand_for_request(request, db)


# ============================================================
# USER CREATION
# ============================================================
@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username, password_hash=user.password, parent_id=user.parent_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# ============================================================
# VAULT CREATION (MUST COME BEFORE UPDATE)
# ============================================================
@app.post("/users/{user_id}/vault", response_model=UserVaultOut)
def create_vault(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(UserVault).filter(UserVault.user_id == user_id).first()
    if existing:
        return existing

    vault = UserVault(user_id=user_id)
    db.add(vault)
    db.commit()
    db.refresh(vault)
    return vault


# ============================================================
# VAULT UPDATE
# ============================================================
@app.post("/users/{user_id}/vault/update", response_model=UserVaultOut)
def update_vault(user_id: int, vault_data: UserVaultOut, db: Session = Depends(get_db)):
    vault = db.query(UserVault).filter(UserVault.user_id == user_id).first()
    if not vault:
        raise HTTPException(status_code=404, detail="Vault not found")

    vault.cash_balance = vault_data.cash_balance
    vault.crypto_balance = vault_data.crypto_balance
    vault.reo_equity = vault_data.reo_equity
    vault.domain_value = vault_data.domain_value
    vault.total_liabilities = vault_data.total_liabilities

    db.commit()
    db.refresh(vault)
    return vault


# ============================================================
# XP UPDATE
# ============================================================
@app.post("/users/{user_id}/xp")
def update_xp(user_id: int, xp_data: XPUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.xp += xp_data.xp
    db.commit()
    return {"message": "XP updated", "total_xp": user.xp}


# ============================================================
# LEADERBOARD
# ============================================================
@app.get("/leaderboard")
def leaderboard(db: Session = Depends(get_db)):
    return db.query(User).order_by(User.xp.desc()).all()


# ============================================================
# PROOF OF FUNDS (JSON)
# ============================================================
@app.get("/users/{user_id}/proof-of-funds", response_model=ProofOfFundsOut)
def proof_of_funds(user_id: int, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    brand = get_brand_for_request(request, db)
    vault = db.query(UserVault).filter(UserVault.user_id == user_id).first()

    if not vault:
        raise HTTPException(status_code=400, detail="Vault not initialized")

    capacity = (
        (vault.cash_balance or 0)
        + (vault.crypto_balance or 0)
        + (vault.reo_equity or 0)
        + (vault.domain_value or 0)
        - (vault.total_liabilities or 0)
    )

    issued_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    verification_id = uuid.uuid4().hex[:8].upper()

    header = brand.pof_header_text or f"{brand.bank_name} • PROOF OF FUNDS"

    letter = f"""
{header}

Date Issued: {issued_at}
Verification ID: {verification_id}

Borrower: {user.username}
User ID: {user.id}

Verified Capacity: ${capacity / 100:,.2f} USD

Contact:
{brand.contact_email}
{brand.contact_phone}
{brand.address}

Sincerely,
{brand.bank_name}
"""

    return ProofOfFundsOut(
        user_id=user.id,
        bank_name=brand.bank_name,
        capacity_balance=capacity,
        issued_at=issued_at,
        verification_id=verification_id,
        letter=letter.strip(),
    )


# ============================================================
# PROOF OF FUNDS (PDF)
# ============================================================
@app.get("/users/{user_id}/proof-of-funds.pdf")
def proof_of_funds_pdf(user_id: int, request: Request, db: Session = Depends(get_db)):
    data = proof_of_funds(user_id, request, db)
    pdf = build_simple_pdf(data.letter.split("\n"))
    return StreamingResponse(pdf, media_type="application/pdf")


# ============================================================
# DIGITAL ASSET VALUATION ENGINE
# ============================================================
def estimate_digital_asset_value(asset_type: str, identifier: str, metadata: str | None):
    if asset_type == "domain":
        base = 50000
        if identifier.endswith(".com"):
            base += 25000
        if len(identifier.split(".")[0]) <= 5:
            base += 50000
        return base

    if asset_type == "social":
        try:
            meta = eval(metadata) if metadata else {}
            return meta.get("followers", 0) * 2
        except:
            return 10000

    if asset_type == "website":
        try:
            meta = eval(metadata) if metadata else {}
            return meta.get("monthly_revenue", 0) * 24
        except:
            return 50000

    return 10000


# ============================================================
# DIGITAL ASSET CREATION
# ============================================================
@app.post("/users/{user_id}/digital-assets", response_model=DigitalAssetOut)
def add_digital_asset(user_id: int, data: DigitalAssetCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    value = estimate_digital_asset_value(data.asset_type, data.identifier, data.metadata)

    asset = DigitalAsset(
        user_id=user_id,
        asset_type=data.asset_type,
        identifier=data.identifier,
        metadata=data.metadata,
        estimated_value=value,
    )

    db.add(asset)
    db.commit()
    db.refresh(asset)

    vault = db.query(UserVault).filter(UserVault.user_id == user_id).first()
    if vault:
        vault.domain_value = sum(a.estimated_value for a in user.digital_assets)
        db.commit()

    return asset


# ============================================================
# DIGITAL ASSET REVALUATION
# ============================================================
@app.post("/users/{user_id}/digital-assets/revalue")
def revalue_digital_assets(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    total = 0
    for asset in user.digital_assets:
        asset.estimated_value = estimate_digital_asset_value(
            asset.asset_type, asset.identifier, asset.metadata
        )
        total += asset.estimated_value

    vault = db.query(UserVault).filter(UserVault.user_id == user_id).first()
    if vault:
        vault.domain_value = total
        db.commit()

    return {"message": "Assets revalued", "total_value": total}


# ============================================================
# FINAL DB INIT
# ============================================================
Base.metadata.create_all(bind=engine)
