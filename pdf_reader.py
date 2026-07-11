"""
pdf_reader.py
--------------
Handles reading and extracting raw text from an uploaded PDF resume.

Uses pdfplumber to parse the PDF page by page. Includes error handling
for empty, corrupted, or password-protected PDF files.
"""

from typing import Optional, Tuple
import pdfplumber


def extract_text_from_pdf(uploaded_file) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract raw text from an uploaded PDF file object (e.g. from Streamlit's
    st.file_uploader).

    Args:
        uploaded_file: A file-like object pointing to a PDF (BytesIO/UploadedFile).

    Returns:
        A tuple of (extracted_text, error_message).
        - If extraction succeeds, extracted_text contains the text and
          error_message is None.
        - If extraction fails, extracted_text is None and error_message
          contains a human-readable explanation.
    """
    if uploaded_file is None:
        return None, "No file was uploaded. Please upload a PDF resume."

    try:
        # pdfplumber can raise various exceptions for corrupted or
        # password-protected files, so we wrap the whole read in try/except.
        with pdfplumber.open(uploaded_file) as pdf:
            if len(pdf.pages) == 0:
                return None, "The uploaded PDF has no pages. Please upload a valid resume."

            extracted_pages = []
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_pages.append(page_text)

            full_text = "\n".join(extracted_pages).strip()

            if not full_text:
                return None, (
                    "No readable text was found in this PDF. "
                    "It might be a scanned image or an empty document. "
                    "Please upload a text-based PDF resume."
                )

            return full_text, None

    except Exception as error:
        error_message = str(error).lower()

        # pdfplumber/pdfminer typically raises errors mentioning
        # 'password' or 'encrypt' for protected PDFs.
        if "password" in error_message or "encrypt" in error_message:
            return None, (
                "This PDF appears to be password-protected. "
                "Please upload an unprotected PDF resume."
            )

        return None, (
            "We couldn't read this PDF. It may be corrupted or in an "
            f"unsupported format. Details: {error}"
        )


def validate_pdf_file(uploaded_file, max_size_mb: int = 10) -> Optional[str]:
    """
    Perform basic validation on the uploaded file before attempting extraction.

    Args:
        uploaded_file: The uploaded file object from Streamlit.
        max_size_mb: Maximum allowed file size in megabytes.

    Returns:
        An error message string if validation fails, otherwise None.
    """
    if uploaded_file is None:
        return "Please upload a PDF file to continue."

    if not uploaded_file.name.lower().endswith(".pdf"):
        return "Invalid file type. Please upload a PDF file only."

    # Streamlit's UploadedFile exposes a .size attribute in bytes.
    file_size_mb = getattr(uploaded_file, "size", 0) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return f"File is too large ({file_size_mb:.1f} MB). Max allowed size is {max_size_mb} MB."

    return None
