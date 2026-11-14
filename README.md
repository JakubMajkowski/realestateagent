# realestateagent

Pomocniczy skrypt skanera ofert wynajmu w Gdyni. GitHub Actions dwa razy dziennie pobiera listy ofert
z serwisów, których nie da się czytać bezpośrednio (Gratka, Morizon, trojmiasto.pl, okolica.pl, krm.pl),
i zapisuje je w `data/`. Skan Claude o 10:00 i 17:00 czyta te pliki i dodaje pasujące oferty do trackera.

- `scraper/fetch.py` – pobieranie i uproszczenie stron
- `data/status.json` – wynik ostatniego pobrania dla każdego serwisu
