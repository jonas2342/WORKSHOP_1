import csv
import os

# --- Klasser ---
class Person:
    def __init__(self, navn, alder, adresse):
        self.navn = navn
        self.alder = alder
        self.adresse = adresse

    def __str__(self):
        return f"Navn: {self.navn}, Alder: {self.alder}, Adresse: {self.adresse}"

    @property
    def alder(self) -> int:
        return self._alder

    @alder.setter
    def alder(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise TypeError("Alder skal være et heltal; decimaltal afrundes") from None
        if value < 0:
            raise ValueError("Alder kan ikke være negativ")
        self._alder = value
        
class Borger(Person):
    def __init__(self, navn, alder, pensionist, adresse, indkomst, husleje):
        super().__init__(navn, alder, adresse)
        self.husleje = husleje
        self.pensionist = pensionist
        self.indkomst = indkomst


    def __str__(self):
        return f"{super().__str__()}, pensionist: {self.pensionist}, husleje: {self.husleje}"


class Lærer(Person):
    """
    Lærer-klasse der udvider Person med email, telefon og fag.
    Demonstrerer properties med validering for at beskytte data-integritet.
    """
    def __init__(self, navn, alder, køn, email, telefon, fag=None):
        super().__init__(navn, alder, køn)
        # Brug properties - dette kalder automatisk setters med validering
        self.email = email
        self.telefon = telefon
        self._fag = fag if fag else []
    
    @property
    def email(self):
        """
        Getter for email - returnerer den interne værdi.
        """
        return self._email
    
    @email.setter
    def email(self, value):
        """
        Setter for email med validering.
        Sikrer at emailen har et gyldigt format (noget@noget.noget).
        """
        if not isinstance(value, str):
            raise TypeError("Email skal være tekst")
        
        # Regex mønster for email-validering
        email_mønster = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_mønster, value):
            raise ValueError("Email skal have formatet: navn@domæne.dk")
        
        self._email = value
    
    @property
    def telefon(self):
        """Getter for telefon - returnerer formateret telefonnummer."""
        return self._telefon
    
    @telefon.setter
    def telefon(self, value):
        """
        Setter for telefon med validering og formatering.
        Accepterer forskellige input-formater men standardiserer til ét format.
        """
        # Fjern mellemrum og bindestreger for at standardisere
        renset = value.replace(" ", "").replace("-", "")
        
        # Validér at det kun er tal
        if not renset.isdigit():
            raise ValueError("Telefonnummer må kun indeholde tal")
        
        # Validér længde (dansk telefonnummer = 8 cifre)
        if len(renset) != 8:
            raise ValueError("Dansk telefonnummer skal være 8 cifre")
        
        # Gem i standardformat for læsbarhed: XX XX XX XX
        self._telefon = f"{renset[:2]} {renset[2:4]} {renset[4:6]} {renset[6:]}"
    
    @property
    def fag(self):
        """
        Getter for fag - returnerer en kopi så den interne liste ikke kan ændres direkte.
        Dette beskytter vores data - brugere skal bruge tilføj_fag() og fjern_fag().
        """
        return self._fag.copy()
    
    def tilføj_fag(self, fag_navn):
        """Tilføj et fag til lærerens fagliste hvis det ikke allerede findes."""
        if fag_navn not in self._fag:
            self._fag.append(fag_navn)
            return True
        return False
    
    def fjern_fag(self, fag_navn):
        """Fjern et fag fra lærerens fagliste hvis det findes."""
        if fag_navn in self._fag:
            self._fag.remove(fag_navn)
            return True
        return False
    
    def __str__(self):
        fag_tekst = ", ".join(self._fag) if self._fag else "Ingen fag tildelt"
        return (f"{super().__str__()}, Email: {self.email}, "
                f"Telefon: {self.telefon}, Fag: {fag_tekst}")




# --- Filnavn ---
FILENAME = "personliste.csv"


# --- Gem listen til CSV ---
def gem_personer_csv(personer):
    # Find mappen hvor .py filen ligger
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Kombiner med filnavnet
    filepath = os.path.join(script_dir, FILENAME)
    
    felt_navn = ["navn", "alder", "pensionist", "indkomst", "husleje"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=felt_navn)
        writer.writeheader()
        for p in personer:
            row = {
                "navn": p.navn,
                "alder": p.alder,
                "pensionist": p.pensionist,
                "indkomst": getattr(p, "indkomst", ""),
                "husleje": getattr(p, "husleje", "")
            }
            writer.writerow(row)
    print(f"Listen er gemt i '{filepath}' (CSV-fil).")


# --- Indlæs liste fra CSV ---
def indlaes_personer_csv():
    # Find mappen hvor .py filen ligger
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Kombiner med filnavnet
    filepath = os.path.join(script_dir, FILENAME)
    
    personer = []
    if os.path.exists(filepath):
        with open(filepath, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                navn = row["navn"]
                alder = int(row["alder"])
                pensionist = row["pensionist"]
                indkomst = row.get("indkomst", "")
                husleje = row.get("husleje", "")
                if indkomst or husleje:
                    personer.append(Borger(navn, alder, pensionist, indkomst, husleje))
                else:
                    personer.append(Person(navn, alder, pensionist))
        print(f"{len(personer)} personer/Borger indlæst fra '{filepath}'")
    else:
        print("Ingen tidligere fil fundet, starter med tom liste.")
    return personer


# --- Terminalprogram ---
def main():
    personer = indlaes_personer_csv()  # indlæs eksisterende CSV

    while True:
        print("\n--- Person/Borger Registrering ---")
        print("1. Tilføj person")
        print("2. Vis alle personer")
        print("3. Tilføj person til indkomst")
        print("4. Gem liste som CSV")
        print("5. Afslut")
        valg = input("Vælg en mulighed: ")

        if valg == "1":
            navn = input("Indtast navn: ")
            alder = input("Indtast alder: ")
            pensionist = input("Indtast pensionist: ")
            try:
                alder = int(alder)
                p = Person(navn, alder, pensionist)
                personer.append(p)
                print("Person tilføjet!")
            except ValueError:
                print("⚠ Alder skal være et heltal.")

        elif valg == "2":
            if not personer:
                print("Ingen personer registreret endnu.")
            else:
                print("\n--- Registrerede personer/Borger ---")
                for i, person in enumerate(personer, start=1):
                    print(f"{i}. {person}")

        elif valg == "3":
            ikke_Borgere = [p for p in personer if not isinstance(p, Borger)]
            if not ikke_Borgere:
                print("Ingen personer at opgradere.")
                continue

            print("\nVælg en person at opgradere til Borger:")
            for i, person in enumerate(ikke_Borgere, start=1):
                print(f"{i}. {person}")

            try:
                valg_index = int(input("Nummer: ")) - 1
                person_valgt = ikke_Borgere[valg_index]
            except (ValueError, IndexError):
                print("Ugyldigt valg.")
                continue

            indkomst = input("Indtast indkomst: ")
            husleje = input("Indtast husleje: ")
            Borger = Borger(person_valgt.navn, person_valgt.alder, person_valgt.pensionist, indkomst, husleje)
            personer[personer.index(person_valgt)] = Borger
            print(f"{Borger.navn} er nu Borger på {indkomst}, husleje {husleje}!")

        elif valg == "4":
            gem_personer_csv(personer)

        elif valg == "5":
            print("Program afsluttes.")
            gem_personer_csv(personer)
            break

        else:
            print("Ugyldigt valg, prøv igen.")


if __name__ == "__main__":
    main()