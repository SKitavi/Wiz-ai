import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from docx import Document
import cv2
import numpy as np
from pathlib import Path
from loguru import logger

class OCRService:
    @staticmethod
    def preprocess_image(image_path: str) -> np.ndarray:
        """Enhance image for better OCR"""
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Apply thresholding and noise reduction
        denoised = cv2.fastNlMeansDenoising(gray)
        thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        return thresh
    
    @staticmethod
    def extract_from_image(image_path: str) -> str:
        """Extract text from screenshot/image"""
        try:
            preprocessed = OCRService.preprocess_image(image_path)
            text = pytesseract.image_to_string(preprocessed, config='--psm 6')
            logger.info(f"Extracted {len(text)} chars from image")
            return text
        except Exception as e:
            logger.error(f"Image OCR failed: {e}")
            raise
    
    @staticmethod
    def extract_from_pdf(pdf_path: str) -> str:
        """Extract text from PDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            logger.info(f"Extracted {len(text)} chars from PDF")
            return text
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise
    
    @staticmethod
    def extract_from_docx(docx_path: str) -> str:
        """Extract text from Word document"""
        try:
            doc = Document(docx_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            logger.info(f"Extracted {len(text)} chars from DOCX")
            return text
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            raise

