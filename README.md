# Sola — klesbutikk med flere selgere

PHP 8.2+ med PDO SQLite, mbstring og fileinfo. Ingen Composer- eller Node-avhengigheter.

## Start lokalt

```sh
php -S 127.0.0.1:8080 -t public
```

Åpne appen og opprett butikkens første administratorkonto. Bruk et unikt passord med minst 12 tegn. Første oppsett må gjøres før offentlig eksponering. Administratoren oppretter selgere og stativer. Selgere ser bare egne plagg og oppgjør; butikkadministrator ser hele butikken.

1. Registrer plagg, størrelse, pris, eier, stativ og bilde fra mobil eller fil.
2. Skriv ut etiketten med unikt SOLA-nummer og Code 39-strekkode.
3. Slå opp nummeret, bruk USB-skanner eller kameraskanning i en kompatibel nettleser over HTTPS.
4. Etter mottatt betaling registrerer butikkansatte plagget som solgt.
5. Oppgjør viser 80 % til selger og 20 % til butikk som standard. Andelen kan velges når selgeren opprettes og låses for hvert salg.
6. Overfør penger via bank/Vipps og marker deretter utbetalingen. Appen overfører ikke penger og behandler ikke kortbetaling.

Databasen og bilder lagres i `var/`, utenfor offentlig webrot. Sikkerhetskopier begge samlet; stopp skriving eller bruk SQLite backup API ved sikkerhetskopi. Ikke eksponer prosjektroten som webrot. Produksjon krever HTTPS, PHP-FPM/webserver, sikker backup, og rutiner for kontoer og personvern. PHPs innebygde server er kun for utvikling. Ingen standardpassord eller demobrukere opprettes. Betalt/utbetalt registrering er endelig i denne første versjonen; retur, refusjon og korreksjoner må implementeres før slike arbeidsflyter tas i bruk.

## Tester

```sh
python3 tests/smoke.py
```

Testen starter en egen PHP-server og bruker en midlertidig kopi slik at butikkens data ikke endres. Tester innlogging, eierrettigheter, plagg med bilde, salg, dobbeltsalg og oppgjør.

## Opprett bruker og innlogging

Etter at butikkeieren har opprettet første administratorkonto, kan selgere velge **Opprett bruker** på innloggingssiden. Oppgi navn, e-post og passord to ganger (12–72 byte). Nye kontoer får alltid selgerrollen og 80 % andel, uavhengig av innsendte rollefelter. E-postadressen må være unik. Passord lagres som hash. Alle butikksider krever innlogging; hver selger ser bare egne plagg og oppgjør. E-postbekreftelse og glemt-passord via e-post er ikke inkludert.

### Laragon på Windows

Pakk ut mappen `sola` i `C:\laragon\www`. Åpne Laragon-terminalen og kjør:

```bat
cd C:\laragon\www\sola
php -S localhost:8080 -t public
```

Åpne http://localhost:8080. PHP må ha pdo_sqlite, mbstring og fileinfo aktivert. Ved oppdatering: ta sikkerhetskopi og behold eksisterende `var`-mappe med database og bilder.
