import os
import sys

# Ensure knowledge_base directory exists
kb_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "knowledge_base")
os.makedirs(kb_dir, exist_ok=True)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    print("ReportLab is available. Generating PDFs...")
except ImportError:
    print("ReportLab is not installed yet. We will write text files and rename them as PDFs, or wait for installation.")
    # Fallback to write plain text files if reportlab is not found (though it will be installed)
    # We will define a minimal PDF generator in pure python if reportlab is missing, or just wait.
    # To be professional, let's write a pure-python text-to-pdf writer or wait.
    # Actually, we can write a simple python script that will use reportlab. Once reportlab is installed, we run it.
    pass

def create_pdf(filename, title, paragraphs):
    filepath = os.path.join(kb_dir, filename)
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        leading=28,
        spaceAfter=20
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=16,
        spaceAfter=12
    )
    
    story = [
        Paragraph(title, title_style),
        Spacer(1, 10)
    ]
    
    for p in paragraphs:
        story.append(Paragraph(p, body_style))
        story.append(Spacer(1, 6))
        
    doc.build(story)
    print(f"Created PDF: {filepath}")

# Contents
company_policy_content = [
    "<b>ABC Technologies — General Company Policies</b>",
    "This document outlines the standard customer policies for refunds, cancellations, and account management at ABC Technologies.",
    "<b>1. Refund Policy:</b> We offer a 30-day money-back guarantee. Customers can request a full refund within 30 days of their initial purchase. "
    "Refund requests made after 30 days of purchase are not eligible for refunds. All refunds are processed back to the original payment method. "
    "Refunds exceeding ₹5,000 require management escalation and human-in-the-loop validation.",
    "<b>2. Subscription Cancellations:</b> Users can cancel their subscription at any time via the billing portal. "
    "Upon cancellation, the subscription remains active until the end of the current billing cycle. No partial refunds or pro-rated credits are "
    "given for unused portions of the cancellation month.",
    "<b>3. Account Closures:</b> If a customer requests to permanently close or delete their account, the request must be processed by our "
    "User Security Team. Account closure is permanent and deletes all user data. To ensure security, account closures must be routed for human manager approval.",
    "<b>4. Compensation Policy:</b> In the event of a service outage or severe application bug, support agents are authorized to offer a token compensation. "
    "Agents may issue up to a maximum of ₹5,000 credit or 1 month of free Basic service. Any compensation requests exceeding ₹5,000 must be reviewed and approved by a supervisor."
]

pricing_guide_content = [
    "<b>ABC Technologies — Product Pricing and Feature Guide</b>",
    "Welcome to the official pricing guide for ABC Technologies SaaS Platform. We offer three flexible plans designed to scale with your business. "
    "All prices below are shown in INR.",
    "<b>1. Basic Plan (₹999/month):</b> designed for small teams and individuals. Includes up to 5 user accounts, 10GB of secure cloud storage, "
    "standard email support, and access to all core application features.",
    "<b>2. Pro Plan (₹2,999/month):</b> our most popular plan for growing businesses. Includes up to 25 user accounts, 100GB of secure cloud storage, "
    "priority support (response within 4 hours), advanced analytics, and custom integrations.",
    "<b>3. Enterprise Plan (₹8,999/month):</b> built for large organizations requiring scale and dedicated compliance. Includes unlimited user accounts, "
    "1TB of secure cloud storage, 24/7 dedicated support manager, custom SLA guarantees, SSO authentication, and infinite custom API integrations.",
    "<b>Note:</b> Annual billing options are available for all plans, offering a 15% discount. For custom plans or high-volume usage, "
    "please contact our Sales Department directly."
]

technical_manual_content = [
    "<b>ABC Technologies — Technical Manual and Troubleshooter</b>",
    "This manual provides technical specifications, upload rules, and troubleshooting instructions for the ABC Technologies application platform.",
    "<b>1. File Upload Specifications:</b> The application supports file uploads. The maximum allowed file size is 50MB. "
    "Supported file formats are PDF, PNG, JPEG, and ZIP. Uploading any other format or files exceeding 50MB will result in an upload error.",
    "<b>2. Troubleshooting Upload Crashes:</b> If the application crashes or freezes while uploading a file, follow these steps:<br/>"
    "Step 1: Check your network connection. A drop in network connectivity will interrupt upload streams.<br/>"
    "Step 2: Verify the file size does not exceed the 50MB limit.<br/>"
    "Step 3: Ensure the file extension is one of the supported formats (PDF, PNG, JPEG, ZIP).<br/>"
    "Step 4: Clear your browser cache and cookies, then reload the page.<br/>"
    "Step 5: If the crash persists, check the developer console for error headers. If you see a 500 Internal Server Error, please report it to our engineering team.",
    "<b>3. Password Requirements & Reset Procedure:</b> To maintain account security, all passwords must be at least 12 characters long "
    "and include at least one number, one uppercase letter, and one special character (e.g., !, @, #). "
    "If you forget your password, click the 'Forgot Password' link on the login screen. Enter your registered email to receive a password reset token."
]

faq_content = [
    "<b>ABC Technologies — Frequently Asked Questions (FAQ)</b>",
    "<b>Q: How do I reset my password?</b><br/>"
    "A: You can reset your password by clicking 'Forgot Password' on the login page. Make sure your new password meets our security requirements: "
    "minimum 12 characters, including one capital letter, one number, and one special character.",
    "<b>Q: What happens if I cancel my subscription?</b><br/>"
    "A: Your subscription will remain active until the end of your billing cycle. No pro-rated refunds are provided.",
    "<b>Q: Can I get a refund?</b><br/>"
    "A: We offer a full refund if requested within 30 days of purchase. Refund requests after 30 days are not accepted.",
    "<b>Q: Why does the app crash during upload?</b><br/>"
    "A: The most common causes are files exceeding 50MB or unsupported file formats. Make sure you upload a PDF, PNG, JPEG, or ZIP file below 50MB.",
    "<b>Q: What are the pricing plans?</b><br/>"
    "A: We offer the Basic Plan at ₹999/month (5 users, 10GB), Pro Plan at ₹2,999/month (25 users, 100GB), and Enterprise Plan at ₹8,999/month (unlimited users, 1TB)."
]

if __name__ == "__main__":
    try:
        create_pdf("company_policy.pdf", "Company Policy Manual", company_policy_content)
        create_pdf("pricing_guide.pdf", "Pricing Guide", pricing_guide_content)
        create_pdf("technical_manual.pdf", "Technical Manual", technical_manual_content)
        create_pdf("faq.pdf", "Frequently Asked Questions", faq_content)
        print("Successfully generated all knowledge base PDF files.")
    except Exception as e:
        print(f"Error generating PDFs: {e}")
        sys.exit(1)
