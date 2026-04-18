import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.config import settings
from core.vector_store import VectorStoreManager

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Sample domain documents (embedded in-code so
# no heavy PDF parsing libs are needed at startup)
# ─────────────────────────────────────────────

HR_DOCUMENTS = [
    {
        "title": "Leave Policy",
        "content": """
        Leave Policy – Enterprise HR Manual

        1. Annual Leave: All full-time employees are entitled to 24 days of paid annual leave per year.
           Unused leave can be carried over up to a maximum of 10 days to the next calendar year.

        2. Sick Leave: Employees are entitled to 12 days of paid sick leave per year.
           A medical certificate is required for sick leave exceeding 3 consecutive days.

        3. Maternity Leave: Female employees are entitled to 26 weeks of paid maternity leave.
           This applies after completing 6 months of continuous service.

        4. Paternity Leave: Male employees are entitled to 5 working days of paid paternity leave
           within 6 months of the child's birth or adoption.

        5. Unpaid Leave: Employees may apply for unpaid leave of up to 90 days with manager approval.
           HR approval is required for any unpaid leave exceeding 30 days.

        6. Public Holidays: Employees are entitled to all declared national public holidays.
           If required to work on a public holiday, employees receive double pay or compensatory leave.
        """,
    },
    {
        "title": "Performance Review Process",
        "content": """
        Performance Review Process – Enterprise HR Manual

        Performance reviews are conducted bi-annually: in June and December.

        Review Cycle:
        - Self-assessment submitted by employee (Week 1)
        - Manager review and rating (Week 2–3)
        - HR calibration session (Week 4)
        - Final review meeting with employee (Week 5)

        Rating Scale:
        - 5 – Exceptional: Consistently exceeds all expectations
        - 4 – Exceeds Expectations: Frequently surpasses role requirements
        - 3 – Meets Expectations: Consistently meets role requirements
        - 2 – Needs Improvement: Partially meets expectations
        - 1 – Unsatisfactory: Does not meet basic role requirements

        Promotion Eligibility:
        Employees rated 4 or above for two consecutive cycles are eligible for promotion review.
        Salary increments are linked to performance ratings and approved during the December cycle.

        PIP (Performance Improvement Plan):
        Employees rated 2 or below receive a 90-day PIP with defined milestones and manager support.
        """,
    },
    {
        "title": "Code of Conduct",
        "content": """
        Code of Conduct – Enterprise HR Policy

        All employees are expected to uphold the highest standards of professional integrity.

        Key Principles:
        1. Respect and Inclusion: Treat all colleagues, clients, and partners with dignity and respect.
           Discrimination based on race, gender, religion, age, disability, or sexual orientation is prohibited.

        2. Confidentiality: Employees must protect confidential company and client information.
           Sharing proprietary data externally without written authorization is a serious violation.

        3. Conflict of Interest: Employees must disclose any personal or financial interest
           that could conflict with their professional responsibilities.

        4. Anti-Harassment: Any form of workplace harassment — verbal, physical, or digital — is strictly prohibited.
           Violations should be reported immediately to HR.

        5. Ethical Use of Company Resources: Company assets, including IT systems, must be used solely for
           business purposes. Personal use must be minimal and must not compromise security.

        Violations of the Code of Conduct may result in disciplinary action up to and including termination.
        """,
    },
    {
        "title": "Onboarding Process",
        "content": """
        Onboarding Process – Enterprise HR Manual

        New Employee Onboarding is a 30-day structured program.

        Week 1: Orientation
        - IT setup: laptop, email, system access provisioned within 24 hours of joining
        - HR orientation covering policies, benefits, and payroll enrollment
        - Introduction to team and reporting manager
        - Completion of mandatory compliance training modules

        Week 2–3: Role-Specific Training
        - Shadowing sessions with senior team members
        - Access to internal knowledge base and documentation
        - Assignment of onboarding buddy from the same department

        Week 4: Integration
        - First 1-on-1 with reporting manager to set 90-day goals
        - Introduction to cross-functional stakeholders
        - Feedback session with HR to address any onboarding concerns

        Probation Period:
        New employees are on a 90-day probation period. Confirmation of employment is based on
        a satisfactory performance review at the end of probation.
        """,
    },
]

FINANCE_DOCUMENTS = [
    {
        "title": "Expense Reimbursement Policy",
        "content": """
        Expense Reimbursement Policy – Finance Manual

        All business-related expenses incurred by employees must be submitted for reimbursement
        within 30 days of the expense date.

        Eligible Expenses:
        - Business travel (flights, hotels, ground transport)
        - Client meals and entertainment (up to INR 5,000 per person per event)
        - Office supplies purchased for business use
        - Professional development courses approved by manager

        Submission Process:
        1. Submit expense report via the Finance Portal with original receipts
        2. Manager approval required within 5 business days
        3. Finance review and processing within 10 business days of approval
        4. Reimbursement credited to salary account on the 25th of the month

        Travel Expense Limits:
        - Domestic flights: Economy class mandatory for flights under 4 hours
        - International flights: Business class permitted for flights over 8 hours
        - Hotel: Up to INR 8,000/night domestic, USD 200/night international

        Non-Reimbursable Expenses:
        - Personal entertainment, minibar charges, personal phone calls
        - Fines, penalties, or traffic violations
        - Spouse or family travel expenses unless pre-approved
        """,
    },
    {
        "title": "Budget Planning and Forecasting",
        "content": """
        Budget Planning and Forecasting – Finance Manual

        Annual Budget Cycle:
        - Q3 (July–September): Department heads submit budget proposals for the next fiscal year
        - October: Finance consolidates and reviews all submissions
        - November: Executive review and approval
        - December: Final budget locked and communicated to departments

        Budget Categories:
        1. CAPEX (Capital Expenditure): Assets with useful life > 1 year (hardware, infrastructure)
        2. OPEX (Operating Expenditure): Day-to-day operational expenses (salaries, utilities, SaaS)
        3. Headcount Budget: Approved headcount by department, including contractor positions

        Forecasting:
        - Rolling 4-quarter forecast updated monthly by department finance partners
        - Variance analysis: >10% variance from budget requires written justification
        - Mid-year budget revision allowed once, subject to CFO approval

        Cost Centers:
        Each department is assigned a cost center code. All POs and invoices must reference
        the correct cost center code. Incorrect coding delays payment processing.
        """,
    },
    {
        "title": "Accounts Payable Process",
        "content": """
        Accounts Payable Process – Finance Manual

        Invoice Processing:
        1. Vendor submits invoice to ap@company.com with PO number in the subject line
        2. System auto-creates a payable record and assigns to AP team
        3. 3-way match: Invoice vs PO vs Goods Receipt must match within 5% tolerance
        4. Approved invoices are processed for payment within agreed vendor payment terms

        Payment Terms:
        - Standard vendors: Net 30 days from invoice date
        - Strategic vendors: Net 45 or Net 60 as per contract
        - Early payment discount: 2/10 Net 30 (2% discount if paid within 10 days)

        Vendor Onboarding:
        - All new vendors must complete KYC documentation
        - Bank account verification required before first payment
        - Approved vendor list maintained by Procurement team

        Dispute Resolution:
        - Invoice disputes must be raised within 15 days of receipt
        - AP team has 5 business days to investigate and respond
        - Escalation to Finance Manager if unresolved within 10 business days
        """,
    },
    {
        "title": "Financial Compliance and Audit",
        "content": """
        Financial Compliance and Audit – Finance Manual

        Regulatory Compliance:
        The company adheres to Indian GAAP and IFRS standards for financial reporting.
        All financial statements are prepared on an accrual basis of accounting.

        Internal Audit:
        - Internal audit team conducts quarterly reviews of all major financial processes
        - Risk-based audit approach prioritizes high-value and high-risk transactions
        - Audit findings are reported to the Audit Committee within 15 days of fieldwork completion
        - Management responses to findings due within 30 days

        External Audit:
        - Statutory audit conducted annually by an independent CA firm
        - Audit period: April 1 to March 31 (Indian fiscal year)
        - Preliminary audit completed by May 31; final sign-off by September 30

        Controls Framework:
        - Segregation of duties: No single employee can initiate, approve, and record a transaction
        - Dual authorization required for payments exceeding INR 5 lakhs
        - All journal entries above INR 1 lakh require supporting documentation

        Data Retention:
        Financial records must be retained for a minimum of 8 years as per statutory requirements.
        Electronic records are acceptable if they maintain audit trail integrity.
        """,
    },
]


def chunk_document(text: str, title: str, domain: str) -> tuple[list[str], list[dict]]:
    """Split a document into chunks with metadata."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "],
    )
    chunks = splitter.split_text(text.strip())
    metadatas = [{"title": title, "domain": domain, "chunk_index": i} for i, _ in enumerate(chunks)]
    return chunks, metadatas


def ingest_domain(domain: str, documents: list[dict]):
    """Ingest all documents for a domain."""
    all_texts, all_metas = [], []
    for doc in documents:
        chunks, metas = chunk_document(doc["content"], doc["title"], domain)
        all_texts.extend(chunks)
        all_metas.extend(metas)
    VectorStoreManager.add_documents(domain, all_texts, all_metas)
    logger.info(f"Ingested {len(all_texts)} chunks for domain: {domain}")


def ingest_all_documents():
    """Ingest HR and Finance documents into their respective collections."""
    ingest_domain("hr", HR_DOCUMENTS)
    ingest_domain("finance", FINANCE_DOCUMENTS)