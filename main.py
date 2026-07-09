
import tkinter as tk
from tkinter import messagebox

# ---------- Hilfen: Parsing & Broadcasting ----------

def parse_number_list(text: str) -> list[float]:
    """
    Wandelt z.B. '12, 11.5; 13  14,2' in [12.0, 11.5, 13.0, 14.2] um.
    Erlaubte Trenner: Komma, Semikolon, Leerraum.
    Erlaubt Dezimal-Komma (wird in '.' umgewandelt).
    """
    if text is None:
        return []
    t = text.strip().replace(",", ".").replace(";", " ")
    parts = [p for p in t.split() if p]
    out = []
    for p in parts:
        try:
            out.append(float(p))
        except ValueError:
            raise ValueError(f"Ungültiger Zahlenwert: '{p}'")
    return out

def broadcast_to_len(values: list[float], n: int, name: str) -> list[float]:
    """
    [] -> Fehler; [x] -> n-mal x; Länge==n bleibt; andere Längen -> Fehler.
    """
    if len(values) == 0:
        raise ValueError(f"Für '{name}' wurde kein Wert angegeben.")
    if len(values) == 1:
        return values * n
    if len(values) != n:
        raise ValueError(
            f"Uneinheitliche Listenlängen: '{name}' hat {len(values)}, erwartet {n}."
        )
    return values

def clear_content():
    """Alle Kinder im content_container entfernen (aktiven View schließen)."""
    for child in content_container.winfo_children():
        child.destroy()

def show_header():
    """Nur den Header anzeigen (oben), Inhalt leeren."""
    clear_content()
    # Header explizit vor dem Content platzieren, falls er mal versteckt war:
    header_frame.pack(fill="x", side="top", before=content_container)
    header_visible.set(True)
    root.title("Tauchgangsplanungsmanagement")

def hide_header():
    """Header ausblenden (für Programme)."""
    header_frame.pack_forget()
    header_visible.set(False)

# ---------- App-Grundgerüst (Header + Container) ----------

root = tk.Tk()
root.title("Tauchgangsplanungsmanagement")
root.geometry("900x600")

header_visible = tk.BooleanVar(value=True)

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Dropdown „Programme“
view_menu = tk.Menu(menu_bar, tearoff=0)

# Einziger „Start“-Menüpunkt
menu_bar.add_command(label="Start", command=show_header)

menu_bar.add_cascade(label="Programme", menu=view_menu)

# Header (immer oben)
header_frame = tk.Frame(root)
tk.Label(header_frame, text="Willkommen zum Tauchgangsplanungsmanagement!",
         font=("Arial", 16, "bold")).pack(pady=(20, 5))
tk.Label(header_frame, text="Dieses Programm kann Fehler beinhalten. Alle Werte sind zu überprüfen!",
         font=("Arial", 12), fg="#b00000").pack(pady=(0, 10))
header_frame.pack(fill="x", side="top")

# Container für wechselnde Inhalte (unter dem Header)
content_container = tk.Frame(root)
content_container.pack(fill="both", expand=True)

# ---------- SAC-View mit Formel pro Index ----------

def show_sac_rate():
    """
    Felder:
      - verwendeter Druck [bar]
      - Flaschenvolumen [L]
      - Tiefe [m]
      - Zeit [min]
    Formel pro Eintrag i:
      result_i = ((Druck_i * Volumen_i) / (Tiefe_i + 10) / 10) / Zeit_i
               = (Druck_i * Volumen_i) / ((Tiefe_i + 10) * 10 * Zeit_i)
    """
    root.title("SAC-Rate")
    hide_header()
    clear_content()

    form = tk.Frame(content_container, padx=16, pady=16)
    form.pack(fill="both", expand=True)

    form.columnconfigure(0, weight=0)
    form.columnconfigure(1, weight=1)
    form.rowconfigure(5, weight=1)  # Ergebnis-Text wächst

    labels = [
        "verwendeter Druck [bar]",
        "Flaschenvolumen [L]",
        "Tiefe [m]",
        "Zeit [min]"
    ]
    defaults = [
        "68, 67, 99, 130, 150, 160, 120, 110, 150, 140, 130, 180, 140, 130, 100, 150, 140, 130, 160, 160, 60, 40, 127, 162, 115, 111, 80, 143, 157, 135",  # Beispiel-Liste: Druck
        "12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12, 12",      # Skalar: Volumen
        "3.8; 2,5; 5.1; 12.3; 11.1; 11.6; 8.5; 10.9; 12.5; 13.4; 19.9; 16.6; 12.4; 13; 9.3; 11.3; 9.2; 12; 10.4; 9.6; 2.7; 2.7; 5.3; 12.6; 9.2; 5; 5.1; 4.2; 5.3; 5.3",    # Liste: Tiefe
        "37, 46, 59, 72, 71, 59, 67, 72, 72, 54, 53, 58, 78, 62, 54, 61, 76, 61, 63, 53, 29, 20, 65, 61, 53, 67, 50, 72, 82, 73"     # Liste: Zeit
    ]

    vars_ = [tk.StringVar(value=d) for d in defaults]

    for r, (text, var) in enumerate(zip(labels, vars_)):
        tk.Label(form, text=text).grid(row=r, column=0, sticky="e", padx=(0, 8), pady=6)
        tk.Entry(form, textvariable=var).grid(row=r, column=1, sticky="we", pady=6)

    # Ergebnis-Feld
    result = tk.Text(form, height=12, state="disabled")
    result.grid(row=len(labels)+1, column=0, columnspan=2, sticky="nsew", pady=(12,0))

    def set_result(msg: str):
        result.configure(state="normal")
        result.delete("1.0", "end")
        result.insert("1.0", msg)
        result.configure(state="disabled")

    def berechnen():
        try:
            # 1) Texte parsen -> Listen
            druck = parse_number_list(vars_[0].get())
            vol   = parse_number_list(vars_[1].get())
            tiefe = parse_number_list(vars_[2].get())
            zeit  = parse_number_list(vars_[3].get())

            # 2) Länge bestimmen & Einzelwerte broadcasten
            n = max(len(druck), len(vol), len(tiefe), len(zeit))
            if n == 0:
                raise ValueError("Bitte mindestens einen Wert eingeben.")
            druck = broadcast_to_len(druck, n, "verwendeter Druck")
            vol   = broadcast_to_len(vol,   n, "Flaschenvolumen")
            tiefe = broadcast_to_len(tiefe, n, "Tiefe")
            zeit  = broadcast_to_len(zeit,  n, "Zeit")

            # 3) Plausibilitätschecks
            for i in range(n):
                if zeit[i] <= 0:
                    raise ValueError(f"Zeit muss > 0 sein (Eintrag {i+1}).")
                if vol[i] <= 0:
                    raise ValueError(f"Flaschenvolumen muss > 0 sein (Eintrag {i+1}).")
                if tiefe[i] < 0:
                    raise ValueError(f"Tiefe darf nicht negativ sein (Eintrag {i+1}).")
                # Druck darf 0 sein? Du entscheidest; hier erlauben wir >= 0:
                if druck[i] < 0:
                    raise ValueError(f"Verwendeter Druck darf nicht negativ sein (Eintrag {i+1}).")

            # 4) Berechnung pro Index i
            lines = []
            results = []
            for i in range(n):
                denom = (tiefe[i] + 10.0) / 10.0
                frac = (druck[i] * vol[i]) / denom
                value = frac / zeit[i]
                results.append(value)
                lines.append(
                    f"{i+1:>2}: Druck={druck[i]:.3f} bar, Vol={vol[i]:.3f} L, "
                    f"Tiefe={tiefe[i]:.3f} m, Zeit={zeit[i]:.3f} min → "
                    f"Ergebnis={value:.4f}"
                )

            # Optional: Mittelwert
            avg = sum(results) / len(results)
            lines.append("-" * 72)
            lines.append(f"Mittelwert: {avg:.4f}   (n={n})")

            set_result("\n".join(lines))

        except ValueError as e:
            messagebox.showerror("Eingabefehler", str(e))

    # Buttons
    btns = tk.Frame(form)
    btns.grid(row=len(labels), column=0, columnspan=2, sticky="e", pady=(8,0))
    tk.Button(btns, text="Berechnen", command=berechnen).pack(side="right")

view_menu.add_command(label="SAC-Rate", command=show_sac_rate)

# Gasverbrauch
def show_gasverbrauch():
    root.title("Gasverbrauch")
    hide_header()
    clear_content()

    form = tk.Frame(content_container, padx=16, pady=16)
    form.pack(fill="both", expand=True)

    form.columnconfigure(0, weight=0)
    form.columnconfigure(1, weight=1)
    form.rowconfigure(5, weight=1)  # Ergebnis-Text wächst

    labels = [
        "SAC-Rate [L/min]",
        "Zeit [min]",
        "Tiefe [m]"
    ]

    vars_ = [tk.StringVar(), tk.StringVar(), tk.StringVar()]

    for r, (text, var) in enumerate(zip(labels, vars_)):
        tk.Label(form, text=text).grid(row=r, column=0, sticky="e", padx=(0, 8), pady=6)
        tk.Entry(form, textvariable=var).grid(row=r, column=1, sticky="we", pady=6)

    # Ergebnis-Feld
    result = tk.Text(form, height=12, state="disabled")
    result.grid(row=len(labels)+1, column=0, columnspan=2, sticky="nsew", pady=(12,0))

    def set_result(msg: str):
        result.configure(state="normal")
        result.delete("1.0", "end")
        result.insert("1.0", msg)
        result.configure(state="disabled")

    def berechnen():
        try:
            # 1) Texte parsen -> Listen
            sac = parse_number_list(vars_[0].get())
            zeit   = parse_number_list(vars_[1].get())
            tiefe = parse_number_list(vars_[2].get())

            # 2) Länge bestimmen & Einzelwerte broadcasten
            n = max(len(sac), len(zeit), len(tiefe))
            if n == 0:
                raise ValueError("Bitte mindestens einen Wert eingeben.")
            sac = broadcast_to_len(sac, n, "SAC-Rate")
            zeit   = broadcast_to_len(zeit,   n, "Zeit")
            tiefe = broadcast_to_len(tiefe, n, "Tiefe")
            # 3) Plausibilitätschecks
            for i in range(n):
                if sac[i] <= 3:
                    raise ValueError(f"SAC-Rate muss > 3 sein (Eintrag {i+1}).")
                if zeit[i] <= 0:
                    raise ValueError(f"Zeit muss > 0 sein (Eintrag {i+1}).")
                if tiefe[i] < 0:
                    raise ValueError(f"Tiefe darf nicht negativ sein (Eintrag {i+1}).")

            # 4) Berechnung pro Index i
            lines = []
            results = []
            for i in range(n):
                value = (sac[i] * zeit[i]) * ((tiefe[i] + 10.0) / 10.0)
                results.append(value)
                lines.append(
                    f"{i+1:>2}: SAC-Rate={sac[i]:.3f} L/min, Zeit={zeit[i]:.3f} min, "
                    f"Tiefe={tiefe[i]:.3f} m → "
                    f"Ergebnis={value:.4f}"
                )

            set_result("\n".join(lines))

        except ValueError as e:
            messagebox.showerror("Eingabefehler", str(e))

    # Buttons
    btns = tk.Frame(form)
    btns.grid(row=len(labels), column=0, columnspan=2, sticky="e", pady=(8,0))
    tk.Button(btns, text="Berechnen", command=berechnen).pack(side="right")

view_menu.add_command(label="Gasverbrauch", command=show_gasverbrauch)

# Reserveplanung (Einfach)
def show_reserveplanung():
    root.title("Reserveplanung")
    hide_header()
    clear_content()

    form = tk.Frame(content_container, padx=16, pady=16)
    form.pack(fill="both", expand=True)

    form.columnconfigure(0, weight=0)
    form.columnconfigure(1, weight=1)
    form.rowconfigure(5, weight=1)  # Ergebnis-Text wächst

    labels = [
        "Gasverbrauch [L]"
    ]

    vars_ = [tk.StringVar()]

    for r, (text, var) in enumerate(zip(labels, vars_)):
        tk.Label(form, text=text).grid(row=r, column=0, sticky="e", padx=(0, 8), pady=6)
        tk.Entry(form, textvariable=var).grid(row=r, column=1, sticky="we", pady=6)

    # Ergebnis-Feld
    result = tk.Text(form, height=12, state="disabled")
    result.grid(row=len(labels)+1, column=0, columnspan=2, sticky="nsew", pady=(12,0))

    def set_result(msg: str):
        result.configure(state="normal")
        result.delete("1.0", "end")
        result.insert("1.0", msg)
        result.configure(state="disabled")

    def berechnen():
        try:
            # 1) Texte parsen -> Listen
            gasverbrauch = parse_number_list(vars_[0].get())

            # 2) Länge bestimmen & Einzelwerte broadcasten
            n = len(gasverbrauch)
            if n == 0:
                raise ValueError("Bitte mindestens einen Wert eingeben.")
            gasverbrauch = broadcast_to_len(gasverbrauch, n, "Gasverbrauch")
            # 3) Plausibilitätschecks
            for i in range(n):
                if gasverbrauch[i] <= 0:
                    raise ValueError(f"Gasverbrauch muss > 0 sein (Eintrag {i+1}).")

            # 4) Berechnung pro Index i
            lines = []
            results = []
            for i in range(n):
                value = (gasverbrauch[i] * 1.5)
                results.append(value)
                lines.append(
                    f"{i+1:>2}: Gasverbrauch={gasverbrauch[i]:.3f} L → "
                    f"Ergebnis={value:.4f}"
                )

            set_result("\n".join(lines))

        except ValueError as e:
            messagebox.showerror("Eingabefehler", str(e))

    # Buttons
    btns = tk.Frame(form)
    btns.grid(row=len(labels), column=0, columnspan=2, sticky="e", pady=(8,0))
    tk.Button(btns, text="Berechnen", command=berechnen).pack(side="right")

view_menu.add_command(label="Reserveplanung", command=show_reserveplanung)

# Flaschendruck oder Flaschengröße
def show_flaschenplanung():
    root.title("Flaschenplanung")
    hide_header()
    clear_content()

    form = tk.Frame(content_container, padx=16, pady=16)
    form.pack(fill="both", expand=True)

    form.columnconfigure(0, weight=0)
    form.columnconfigure(1, weight=1)

    # --- Modus-Auswahl ---
    mode = tk.StringVar(value="size")  # "size" (Flaschengröße) oder "pressure" (Mindestdruck)

    mode_frame = tk.Frame(form)
    mode_frame.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))
    tk.Label(mode_frame, text="Berechnungsmodus:").pack(side="left", padx=(0, 8))
    tk.Radiobutton(mode_frame, text="Flaschengröße berechnen",
                   value="size", variable=mode, command=lambda: render_inputs()).pack(side="left")
    tk.Radiobutton(mode_frame, text="Mindestdruck berechnen",
                   value="pressure", variable=mode, command=lambda: render_inputs()).pack(side="left", padx=(8, 0))

    # --- Eingabefelder (2 Zeilen, Labels dynamisch je Modus) ---
    labels_by_mode = {
        "size": (
            "Gasbedarf (Gasverbrauch + Reserve) [L]",
            "Maximaler Betriebsdruck [bar]"
        ),
        "pressure": (
            "Gasbedarf (Gasverbrauch + Reserve) [L]",
            "Flaschengröße [L]"
        ),
    }
    vars_ = [tk.StringVar(), tk.StringVar()]
    label_widgets = []
    entry_widgets = []

    # Eingabezeilen ab Row 1 und 2
    for r in range(2):
        lbl = tk.Label(form, text="")
        lbl.grid(row=1 + r, column=0, sticky="e", padx=(0, 8), pady=6)
        ent = tk.Entry(form, textvariable=vars_[r])
        ent.grid(row=1 + r, column=1, sticky="we", pady=6)
        label_widgets.append(lbl)
        entry_widgets.append(ent)

    def render_inputs():
        a, b = labels_by_mode[mode.get()]
        label_widgets[0].configure(text=a)
        label_widgets[1].configure(text=b)

    render_inputs()  # initial setzen

    # --- Buttons ---
    btns = tk.Frame(form)
    btns.grid(row=3, column=0, columnspan=2, sticky="e", pady=(8, 0))
    tk.Button(btns, text="Berechnen", command=lambda: berechnen()).pack(side="right")

    # --- Ergebnis-Feld ---
    result_row = 4
    result = tk.Text(form, height=12, state="disabled")
    result.grid(row=result_row, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
    form.rowconfigure(result_row, weight=1)  # Ergebnis wächst

    def set_result(msg: str):
        result.configure(state="normal")
        result.delete("1.0", "end")
        result.insert("1.0", msg)
        result.configure(state="disabled")

    # --- Berechnung ---
    def berechnen():
        try:
            # 1) Eingaben parsen -> Listen
            vals1 = parse_number_list(vars_[0].get())  # Gasbedarf [L]
            vals2 = parse_number_list(vars_[1].get())  # Druck [bar] ODER Flaschengröße [L]

            # 2) Länge bestimmen & broadcasten
            n = max(len(vals1), len(vals2))
            if n == 0:
                raise ValueError("Bitte mindestens einen Wert eingeben.")

            label1, label2 = labels_by_mode[mode.get()]
            vals1 = broadcast_to_len(vals1, n, label1)
            vals2 = broadcast_to_len(vals2, n, label2)

            # 3) Plausibilitätschecks und Berechnung
            lines = []
            if mode.get() == "size":
                # Flaschengröße = Gasbedarf / Max. Betriebsdruck
                for i in range(n):
                    gasbedarf = vals1[i]
                    druck = vals2[i]
                    if gasbedarf <= 0:
                        raise ValueError(f"Gasbedarf muss > 0 sein (Eintrag {i+1}).")
                    if druck <= 0:
                        raise ValueError(f"Maximaler Betriebsdruck muss > 0 sein (Eintrag {i+1}).")
                    flaschenvol = gasbedarf / druck
                    lines.append(
                        f"{i+1:>2}: Gasbedarf={gasbedarf:.3f} L, Druck={druck:.3f} bar → "
                        f"Ergebnis (benötigte Flaschengröße) = {flaschenvol:.3f} L"
                    )
            else:
                # Mindestdruck = Gasbedarf / Flaschengröße
                for i in range(n):
                    gasbedarf = vals1[i]
                    flaschenvol = vals2[i]
                    if gasbedarf <= 0:
                        raise ValueError(f"Gasbedarf muss > 0 sein (Eintrag {i+1}).")
                    if flaschenvol <= 0:
                        raise ValueError(f"Flaschengröße muss > 0 sein (Eintrag {i+1}).")
                    mindestdruck = gasbedarf / flaschenvol
                    lines.append(
                        f"{i+1:>2}: Gasbedarf={gasbedarf:.3f} L, Flaschengröße={flaschenvol:.3f} L → "
                        f"Ergebnis (Mindestdruck) = {mindestdruck:.3f} bar"
                    )

            set_result("\n".join(lines))

        except ValueError as e:
            messagebox.showerror("Eingabefehler", str(e))

view_menu.add_command(label="Flaschenplanung", command=show_flaschenplanung)

# MOD-Berechnung
def show_mod():
    root.title("MOD berechnen")
    hide_header()
    clear_content()

    form = tk.Frame(content_container, padx=16, pady=16)
    form.pack(fill="both", expand=True)

    form.columnconfigure(0, weight=0)
    form.columnconfigure(1, weight=1)

    # Kopfzeile (mit Zeilenumbruchbreite, optional)
    header = tk.Label(
        form,
        text="Maximale Partialdrücke: ppN₂ = 3,6bar; ppO₂ = 1,2bar [Arbeitsdruck], ppO₂ = 1,4bar [Dekodruck]"
    )
    header.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

    labels = [
        "Sauerstoff [fO₂]",
        "Stickstoff [fN₂]",
        "Helium [fHe]"  # falls du Helium als Fraktion benennst; sonst "Helium [He]"
    ]
    vars_ = [tk.StringVar(), tk.StringVar(), tk.StringVar()]

    # Eingaben ab Zeile 1 (weil Zeile 0 die Kopfzeile ist)
    for r, (text, var) in enumerate(zip(labels, vars_), start=1):
        tk.Label(form, text=text).grid(row=r, column=0, sticky="e", padx=(0, 8), pady=6)
        tk.Entry(form, textvariable=var).grid(row=r, column=1, sticky="we", pady=6)

    # Ergebnis-Feld unterhalb (Zeile: Anzahl Labels + 2)
    result_row = len(labels) + 2
    result = tk.Text(form, height=12, state="disabled")
    result.grid(row=result_row, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
    form.rowconfigure(result_row, weight=1)  # Ergebnis wächst

    def set_result(msg: str):
        result.configure(state="normal")
        result.delete("1.0", "end")
        result.insert("1.0", msg)
        result.configure(state="disabled")

    def berechnen():
        try:
            # 1) Texte parsen -> Listen
            O = parse_number_list(vars_[0].get())
            N = parse_number_list(vars_[1].get())
            He = parse_number_list(vars_[2].get())

            # 2) Länge bestimmen & Einzelwerte broadcasten
            n = max(len(O), len(N), len(He))
            if n == 0:
                raise ValueError("Bitte mindestens einen Wert eingeben.")
            O = broadcast_to_len(O, n, "Sauerstoffanteil")
            N = broadcast_to_len(N, n, "Stickstoffanteil")
            He = broadcast_to_len(He, n, "Heliumanteil")
            # 3) Plausibilitätschecks
            for i in range(n):
                if O[i] < 0 or O[i] > 1:
                    raise ValueError(f"Sauerstoffanteil muss >= 0 und < 1 sein (Eintrag Sauerstoff).")
                if N[i] < 0 or N[i] > 1:
                    raise ValueError(f"Stickstoffanteil muss >= 0 und < 1 sein (Eintrag Stickstoff).")
                if He[i] < 0 or He[i] > 1:
                    raise ValueError(f"Heliumanteil muss >= 0 und < 1 sein (Eintrag Helium).")

            
            # 4) Berechnung pro Index i
            lines = []
            results = []

            for i in range(n):
            # Annahmen: O[i], N[i], He[i] sind Fraktionen (0..1), Summe ~ 1
            # MOD in Metern: ((pp_limit / f_gas) - 1) * 10
                valueN        = ((3.6 / N[i]) - 1) * 10           # ppN₂-Limit (z.B. 3.6 bar)
                valueOArbeit  = ((1.2 / O[i]) - 1) * 10           # ppO₂ Arbeitsdruck 1.2 bar
                valueODeko    = ((1.4 / O[i]) - 1) * 10           # ppO₂ Dekodruck 1.4 bar

                # maßgeblicher Grenzwert für Arbeitsphase: Minimum aus N₂- und O₂-Arbeit-Limit
                valueA = min(valueN, valueOArbeit)

                results.append(valueA)

                # Ausgabezeile sauber formatieren
                lines.append(
                    f"{i+1:>2}: fN₂={N[i]:.3f}, fO₂={O[i]:.3f}, fHe={He[i]:.3f} → "
                    f"MOD(ppN₂)={valueN:.1f} m, "
                    f"MOD(ppO₂A)={valueOArbeit:.1f} m ⇒ "
                    f"maßgebliche MOD (Arbeit)={valueA:.1f} m, "
                    f"Sauerstofffenster={valueODeko:.1f} m "
                )


            set_result("\n".join(lines))

        except ValueError as e:
            messagebox.showerror("Eingabefehler", str(e))

    # Buttons
    btns = tk.Frame(form)
    btns.grid(row=len(labels)+1, column=0, columnspan=2, sticky="e", pady=(8,0))
    tk.Button(btns, text="Berechnen", command=berechnen).pack(side="right")

view_menu.add_command(label="MOD berechnen", command=show_mod)

# Startansicht aktivieren
show_header()

root.mainloop()
