import pytest
from app.rag.chunking import chunk_document

SAMPLE_STATUTE = """THE NEGOTIABLE INSTRUMENTS ACT, 1881

Section 138. Dishonour of cheque for insufficiency, etc., of funds in the account.
Where any cheque drawn by a person on an account maintained by him with a banker for payment of any amount of money to another person from out of that account for the discharge, in whole or in part, of any debt or other liability, is returned by the bank unpaid, either because of the amount of money standing to the credit of that account is insufficient to honour the cheque or that it exceeds the amount arranged to be paid from that account by an agreement made with that bank, such person shall be deemed to have committed an offence and shall, without prejudice to any other provisions of this Act, be punished with imprisonment for a term which may be extended to two years, or with fine which may extend to twice the amount of the cheque, or with both:
Provided that nothing contained in this section shall apply unless—
(a) the cheque has been presented to the bank within a period of six months from the date on which it is drawn or within the period of its validity, whichever is earlier;
(b) the payee or the holder in due course of the cheque, as the case may be, makes a demand for the payment of the said amount of money by giving a notice in writing, to the drawer of the cheque, within thirty days of the receipt of information by him from the bank regarding the return of the cheque as unpaid; and
(c) the drawer of such cheque fails to make the payment of the said amount of money to the payee or, as the case may be, to the holder in due course of the cheque, within fifteen days of the receipt of the said notice.

Section 139. Presumption in favour of holder.
It shall be presumed, unless the contrary is proved, that the holder of a cheque received the cheque of the nature referred to in section 138 for the discharge, in whole or in part, of any debt or other liability.
"""

def test_chunking_statute_sections():
    meta = {
        "document_type": "statute",
        "act_name": "Negotiable Instruments Act, 1881",
        "source_file": "ni_act.txt"
    }
    chunks = chunk_document(SAMPLE_STATUTE, meta)
    assert len(chunks) >= 2
    
    sec_138_chunks = [c for c in chunks if c.metadata.get("section_or_article") == "138"]
    assert len(sec_138_chunks) >= 1
    # Check that proviso is preserved with the section
    assert "Provided that" in sec_138_chunks[0].text
    assert "Section 138" in sec_138_chunks[0].text

    sec_139_chunks = [c for c in chunks if c.metadata.get("section_or_article") == "139"]
    assert len(sec_139_chunks) >= 1
    assert "Presumption in favour of holder" in sec_139_chunks[0].text
