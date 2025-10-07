import csv
import os
import re

# --- Klasser ---
class Person:
    def __init__(self, navn, alder, køn):
        self.navn = navn
        self.alder = alder
        self.køn = køn

    def __str__(self):
        return f"Navn: {self.navn}, Alder: {self.alder}, Køn: {self.køn}"

    @property
    def alder(self) -> int:
        return self._alder

    @alder.setter
    def alder(self, value):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise TypeError("Alder skal være et heltal") from None
        if value < 0:
            raise ValueError("Alder kan ikke være negativ")
        self._alder = value


class Elev(Person):
    def __init__(self, navn, alder, køn, skole, klassetrin):
        super().__init__(navn, alder, køn)
        self.skole = skole
        self.klassetrin = klassetrin

    def __str__(self):
        return f"{super().__str__()}, Skole: {self.skole}, Klassetrin: {self.klassetrin}"


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


# --- Gem listen til CSV (opdateret version) ---
def gem_personer_csv(personer):
    """
    Gem personer til CSV med understøttelse for både Person, Elev og Lærer.
    Tilføjer type-felt så vi ved hvilken slags objekt der skal oprettes ved indlæsning.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, FILENAME)
    
    # Udvidede felter for at rumme både Elev og Lærer attributter
    felt_navn = [
        "type",  # NYT: Hvilken klasse er objektet
        "navn", "alder", "køn",
        "skole", "klassetrin",  # For Elev
        "email", "telefon", "fag"  # For Lærer
    ]
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=felt_navn)
        writer.writeheader()
        
        for p in personer:
            # Start med grundlæggende info alle har
            row = {
                "navn": p.navn,
                "alder": p.alder,
                "køn": p.køn,
            }
            
            # Tilføj type-specifik information
            if isinstance(p, Lærer):
                row["type"] = "Lærer"
                row["email"] = p.email
                row["telefon"] = p.telefon
                # Fag er en liste - gem som semikolon-separeret string
                row["fag"] = ";".join(p.fag)
                # Sæt elev-felter til tomme
                row["skole"] = ""
                row["klassetrin"] = ""
                
            elif isinstance(p, Elev):
                row["type"] = "Elev"
                row["skole"] = p.skole
                row["klassetrin"] = p.klassetrin
                # Sæt lærer-felter til tomme
                row["email"] = ""
                row["telefon"] = ""
                row["fag"] = ""
                
            else:  # Almindelig Person
                row["type"] = "Person"
                # Sæt alle specifikke felter til tomme
                row["skole"] = ""
                row["klassetrin"] = ""
                row["email"] = ""
                row["telefon"] = ""
                row["fag"] = ""
            
            writer.writerow(row)
    
    print(f"Listen er gemt i '{filepath}' (CSV-fil).")


# --- Indlæs liste fra CSV (opdateret version) ---
def indlaes_personer_csv():
    """
    Indlæs personer fra CSV med understøttelse for forskellige typer.
    Opretter det rigtige objekt baseret på type-feltet.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, FILENAME)
    
    personer = []
    if os.path.exists(filepath):
        with open(filepath, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                navn = row["navn"]
                alder = int(row["alder"])
                køn = row["køn"]
                
                # Læs typen for at vide hvad vi skal oprette
                person_type = row.get("type", "")
                
                if person_type == "Lærer":
                    email = row["email"]
                    telefon = row["telefon"]
                    # Konverter fag-string tilbage til liste
                    fag_str = row.get("fag", "")
                    fag = fag_str.split(";") if fag_str else []
                    
                    lærer = Lærer(navn, alder, køn, email, telefon)
                    # Tilføj hvert fag
                    for fag_navn in fag:
                        if fag_navn:  # Spring over tomme strenge
                            lærer.tilføj_fag(fag_navn)
                    
                    personer.append(lærer)
                    
                elif person_type == "Elev":
                    skole = row["skole"]
                    klassetrin = row["klassetrin"]
                    personer.append(Elev(navn, alder, køn, skole, klassetrin))
                    
                else:  # "Person" eller tomt (bagudkompatibilitet)
                    # Hvis ingen type, prøv den gamle logik
                    if not person_type and (row.get("skole") or row.get("klassetrin")):
                        # Gammel fil uden type-felt, men med skole/klassetrin
                        personer.append(Elev(navn, alder, køn, row["skole"], row["klassetrin"]))
                    else:
                        personer.append(Person(navn, alder, køn))
        
        print(f"{len(personer)} personer indlæst fra '{filepath}'")
    else:
        print("Ingen tidligere fil fundet, starter med tom liste.")
    
    return personer


# --- Terminalprogram ---
def main():
    personer = indlaes_personer_csv()

    while True:
        print("\n" + "="*60)
        print("PERSON/ELEV/LÆRER REGISTRERING")
        print("="*60)
        print("1. Tilføj person")
        print("2. Vis alle personer")
        print("3. Tilføj elev")
        print("4. Tilføj lærer")  # NYT
        print("5. Gem liste som CSV")
        print("6. Afslut")
        print("="*60)
        valg = input("Vælg en mulighed: ")

        if valg == "1":
            navn = input("Indtast navn: ")
            alder = input("Indtast alder: ")
            køn = input("Indtast køn: ")
            try:
                alder = int(alder)
                p = Person(navn, alder, køn)
                personer.append(p)
                print("✓ Person tilføjet!")
            except ValueError as e:
                print(f"⚠ Fejl: {e}")

        elif valg == "2":
            if not personer:
                print("Ingen personer registreret endnu.")
            else:
                print("\n--- Registrerede personer ---")
                for i, person in enumerate(personer, start=1):
                    print(f"{i}. {person}")

        elif valg == "3":
            navn = input("Indtast navn: ")
            alder = input("Indtast alder: ")
            køn = input("Indtast køn: ")
            skole = input("Indtast skole: ")
            klassetrin = input("Indtast klassetrin: ")
            try:
                elev = Elev(navn, int(alder), køn, skole, klassetrin)
                personer.append(elev)
                print(f"✓ Elev {navn} tilføjet!")
            except ValueError as e:
                print(f"⚠ Fejl: {e}")

        elif valg == "4":
            # NYT: Tilføj lærer
            print("\n--- Tilføj ny lærer ---")
            navn = input("Indtast navn: ")
            alder = input("Indtast alder: ")
            køn = input("Indtast køn: ")
            email = input("Indtast email: ")
            telefon = input("Indtast telefon (8 cifre): ")
            
            try:
                # Email og telefon valideres automatisk via properties
                lærer = Lærer(navn, int(alder), køn, email, telefon)
                
                # Tilføj fag
                print("\nTilføj fag (tryk Enter uden at skrive noget for at afslutte)")
                while True:
                    fag = input("Fag: ").strip()
                    if not fag:
                        break
                    if lærer.tilføj_fag(fag):
                        print(f"  ✓ {fag} tilføjet")
                    else:
                        print(f"  ⚠ {fag} er allerede tilføjet")
                
                personer.append(lærer)
                print(f"✓ Lærer {navn} tilføjet!")
                
            except ValueError as e:
                print(f"⚠ Fejl: {e}")
            except TypeError as e:
                print(f"⚠ Fejl: {e}")

        elif valg == "5":
            gem_personer_csv(personer)

        elif valg == "6":
            print("Program afsluttes.")
            gem_personer_csv(personer)
            break

        else:
            print("Ugyldigt valg, prøv igen.")


if __name__ == "__main__":
    main()