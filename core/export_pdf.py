# ─────────────────────────────────────────────
# core/export_pdf.py — Export PDF d'analyse
# ─────────────────────────────────────────────

from fpdf import FPDF
from datetime import datetime
import os
import re


def _clean(text: str) -> str:
    """Supprime les emojis et caractères non-latin pour le rendu PDF Helvetica."""
    return re.sub(r'[^\x00-\x7F\u00C0-\u024F]+', '', str(text)).strip()


class PronoFootPDF(FPDF):
    """PDF personnalisé avec header/footer PronoFoot."""

    def __init__(self, logo_path: str = "prono-foot.jpg"):
        super().__init__()
        self.logo_path = logo_path if os.path.exists(logo_path) else None

    def header(self):
        # Logo
        if self.logo_path:
            self.image(self.logo_path, 10, 8, 18)
        # Titre
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(59, 130, 246)  # Bleu accent
        self.cell(25)  # Décalage après logo
        self.cell(0, 12, "PronoFoot", align="L")
        self.ln(6)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(130, 130, 130)
        self.cell(25)
        self.cell(0, 6, f"Analyse generee le {datetime.now().strftime('%d/%m/%Y a %H:%M')}", align="L")
        self.ln(12)
        # Ligne séparatrice
        self.set_draw_color(59, 130, 246)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"PronoFoot · football-data.org · Page {self.page_no()}", align="C")

    def section_title(self, title: str):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(59, 130, 246)
        self.cell(0, 10, _clean(title), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(59, 130, 246)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(4)

    def match_info(self, equipe_dom: str, equipe_ext: str, ligue: str):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, _clean(f"{equipe_dom}  vs  {equipe_ext}"), align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(130, 130, 130)
        self.cell(0, 6, _clean(ligue), align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(6)

    def proba_row(self, label: str, proba: float, cote_algo: float):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        self.cell(70, 8, _clean(label))
        # Barre de probabilité
        bar_width = 80
        filled = bar_width * proba
        self.set_fill_color(59, 130, 246)
        self.rect(self.get_x(), self.get_y() + 1, filled, 5, style="F")
        self.set_fill_color(230, 230, 230)
        self.rect(self.get_x() + filled, self.get_y() + 1, bar_width - filled, 5, style="F")
        self.cell(bar_width, 8, "")
        self.set_font("Helvetica", "B", 10)
        self.cell(20, 8, f"{proba*100:.1f}%")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, f"cote {cote_algo}", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(60, 60, 60)

    def verdict_box(self, titre: str, valeur: str, detail: str, is_value: bool = False):
        y_start = self.get_y()
        if is_value:
            self.set_fill_color(22, 163, 74)  # Vert
            self.set_text_color(255, 255, 255)
        else:
            self.set_fill_color(240, 240, 240)
            self.set_text_color(60, 60, 60)
        self.rect(10, y_start, 190, 16, style="F")
        self.set_font("Helvetica", "B", 11)
        self.set_xy(14, y_start + 2)
        self.cell(60, 6, _clean(titre))
        self.set_font("Helvetica", "B", 12)
        self.cell(60, 6, _clean(valeur), align="C")
        self.set_font("Helvetica", "", 8)
        self.cell(60, 6, _clean(detail), align="R")
        self.set_xy(10, y_start + 18)
        self.set_text_color(60, 60, 60)

    def kelly_box(self, kelly: float, bankroll: float, cote_book: float, is_value: bool):
        if is_value and kelly > 0:
            mise = round(kelly * bankroll, 2)
            self.set_font("Helvetica", "B", 10)
            self.set_text_color(22, 163, 74)
            self.cell(0, 8, f"   VALUE BET  |  Kelly: {kelly*100:.1f}%  |  Mise: {mise:.2f}EUR sur {bankroll:.0f}EUR  |  Cote book: {cote_book}",
                      new_x="LMARGIN", new_y="NEXT")
        else:
            self.set_font("Helvetica", "", 9)
            self.set_text_color(150, 150, 150)
            self.cell(0, 8, "   Pas de value detectee sur ce marche", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(60, 60, 60)
        self.ln(2)


def generer_pdf_analyse(
    equipe_dom: str, equipe_ext: str, ligue: str,
    p1: float, pn: float, p2: float,
    p_over25: float, pbtts: float,
    score_h: int, score_a: int,
    kelly_1n2: float, kelly_over: float, kelly_btts: float,
    cote_book_1n2: float, cote_book_over: float, cote_book_btts: float,
    bankroll: float,
    seuil_value: float,
    res_1n2: str,
) -> bytes:
    """Génère un PDF d'analyse complet et retourne les bytes."""
    pdf = PronoFootPDF()
    pdf.add_page()

    # Match
    pdf.match_info(equipe_dom, equipe_ext, ligue)

    # Score probable
    pdf.section_title("Score le plus probable")
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 12, f"{score_h} - {score_a}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Probabilités
    pdf.section_title("Probabilites 1N2")
    cote_1 = round(1 / p1, 2) if p1 > 0 else 99
    cote_n = round(1 / pn, 2) if pn > 0 else 99
    cote_2 = round(1 / p2, 2) if p2 > 0 else 99
    pdf.proba_row(f"Victoire {_clean(equipe_dom)}", p1, cote_1)
    pdf.proba_row("Match Nul", pn, cote_n)
    pdf.proba_row(f"Victoire {_clean(equipe_ext)}", p2, cote_2)
    pdf.ln(4)

    pdf.section_title("Marches Speciaux")
    cote_o = round(1 / p_over25, 2) if p_over25 > 0 else 99
    cote_b = round(1 / pbtts, 2) if pbtts > 0 else 99
    pdf.proba_row("Over 2.5 buts", p_over25, cote_o)
    pdf.proba_row("BTTS (les 2 marquent)", pbtts, cote_b)
    pdf.ln(6)

    # Verdicts
    pdf.section_title("Verdicts & Value Bets")
    prob_f = max(p1, pn, p2)
    cote_1n2_algo = round(1 / prob_f, 2) if prob_f > 0 else 99
    is_val_1n2 = cote_book_1n2 > cote_1n2_algo + seuil_value
    pdf.verdict_box("Prono 1N2", res_1n2, f"Cote algo: {cote_1n2_algo}", is_val_1n2)
    pdf.kelly_box(kelly_1n2, bankroll, cote_book_1n2, is_val_1n2)

    is_val_over = cote_book_over > cote_o + seuil_value
    label_over = "OVER 2.5" if p_over25 > 0.52 else "UNDER 2.5"
    pdf.verdict_box("Over/Under", label_over, f"Cote algo: {cote_o}", is_val_over)
    pdf.kelly_box(kelly_over, bankroll, cote_book_over, is_val_over)

    is_val_btts = cote_book_btts > cote_b + seuil_value
    label_btts = "BTTS OUI" if pbtts > 0.50 else "BTTS NON"
    pdf.verdict_box("BTTS", label_btts, f"Cote algo: {cote_b}", is_val_btts)
    pdf.kelly_box(kelly_btts, bankroll, cote_book_btts, is_val_btts)

    # Bankroll
    pdf.ln(6)
    pdf.section_title("Bankroll")
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(59, 130, 246)
    pdf.cell(0, 10, f"Capital: {bankroll:,.0f} EUR", align="C", new_x="LMARGIN", new_y="NEXT")

    return bytes(pdf.output())
