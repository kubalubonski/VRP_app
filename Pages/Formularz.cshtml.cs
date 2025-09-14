using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using OptymalizacjaTras.Models;

namespace OptymalizacjaTras.Pages
{
    public class FormularzModel : PageModel
    {
        public string? StatusMessage { get; set; }

        [BindProperty]
        public string? UlicaMagazynu { get; set; }
        [BindProperty]
        public string? NumerMagazynu { get; set; }
        [BindProperty]
        public string? MiastoMagazynu { get; set; }
        [BindProperty]
        public string? KodPocztowyMagazynu { get; set; }
        [BindProperty]
        public int LiczbaPojazdow { get; set; }
        [BindProperty]
        public List<PunktDostawy> PunktyDostaw { get; set; } = new();
        [BindProperty]
        public string? WybranaTrasa { get; set; }

        private string GetErrorMessage(int exitCode, string operationName)
        {
            return exitCode switch
            {
                0 => "OK",
                1 => $"{operationName}: Wystąpił błąd",
                2 => $"{operationName}: Przekroczono limit API - spróbuj za kilka minut",
                _ => $"{operationName}: Nieznany błąd (kod: {exitCode})"
            };
        }

        public IActionResult OnPostLoadSelected()
        {
            if (string.IsNullOrWhiteSpace(WybranaTrasa))
            {
                StatusMessage = "Nie wybrano pliku trasy.";
                var folder = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "trasy");
                List<string> trasy = new List<string>();
                if (Directory.Exists(folder))
                {
                    trasy = Directory.GetFiles(folder, "*.csv").Select(f => Path.GetFileName(f)).ToList();
                }
                ViewData["Trasy"] = trasy;
                return Page();
            }
            var samplePath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "trasy", WybranaTrasa);
            if (!System.IO.File.Exists(samplePath))
            {
                StatusMessage = $"Brak pliku trasy: {WybranaTrasa}";
                var folder = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "trasy");
                List<string> trasy = new List<string>();
                if (Directory.Exists(folder))
                {
                    trasy = Directory.GetFiles(folder, "*.csv").Select(f => Path.GetFileName(f)).ToList();
                }
                ViewData["Trasy"] = trasy;
                return Page();
            }
            var lines = System.IO.File.ReadAllLines(samplePath);
            UlicaMagazynu = "";
            NumerMagazynu = "";
            MiastoMagazynu = "";
            KodPocztowyMagazynu = "";
            LiczbaPojazdow = 1;
            PunktyDostaw = new List<PunktDostawy>();
            foreach (var line in lines.Skip(1))
            {
                var parts = line.Split(',');
                if (parts[0] == "Magazyn")
                {
                    UlicaMagazynu = parts[1];
                    NumerMagazynu = parts[2];
                    MiastoMagazynu = parts[3];
                    KodPocztowyMagazynu = parts[4];
                }
                else if (parts[0] == "PunktDostawy")
                {
                    PunktyDostaw.Add(new PunktDostawy
                    {
                        Ulica = parts[1],
                        Numer = parts[2],
                        Miasto = parts[3],
                        KodPocztowy = parts[4],
                        OknoCzasoweOd = parts[5],
                        OknoCzasoweDo = parts[6]
                    });
                }
            }
            var folder2 = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "trasy");
            List<string> trasy2 = new List<string>();
            if (Directory.Exists(folder2))
            {
                trasy2 = Directory.GetFiles(folder2, "*.csv").Select(f => Path.GetFileName(f)).ToList();
            }
            ViewData["Trasy"] = trasy2;
            StatusMessage = $"Wczytano trasę: {WybranaTrasa}";
            return Page();
        }

        public void OnGet()
        {
            if (PunktyDostaw.Count == 0)
                PunktyDostaw.Add(new PunktDostawy());

            // Pobierz listę plików CSV
            var folder = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "trasy");
            List<string> trasy = new List<string>();
            if (Directory.Exists(folder))
            {
                trasy = Directory.GetFiles(folder, "*.csv").Select(f => Path.GetFileName(f)).ToList();
            }
            ViewData["Trasy"] = trasy;
        }

        public IActionResult OnPost(string add, string remove)
        {
            if (!string.IsNullOrEmpty(add))
            {
                PunktyDostaw.Add(new PunktDostawy());
                return Page();
            }
            if (!string.IsNullOrEmpty(remove) && int.TryParse(remove, out int idx) && idx < PunktyDostaw.Count)
            {
                PunktyDostaw.RemoveAt(idx);
                return Page();
            }
            var dane = new DaneWejsciowe
            {
                UlicaMagazynu = UlicaMagazynu,
                NumerMagazynu = NumerMagazynu,
                MiastoMagazynu = MiastoMagazynu,
                KodPocztowyMagazynu = KodPocztowyMagazynu,
                LiczbaPojazdow = LiczbaPojazdow,
                PunktyDostaw = PunktyDostaw
            };
            string filePath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "dane_wejsciowe.csv");
            CsvExporter.ExportDaneWejsciowe(dane, filePath);
            return Page();
        }

        public IActionResult OnPostExportCsv()
        {
            string configPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "config.csv");
            System.IO.File.WriteAllText(configPath, $"LiczbaPojazdow,{LiczbaPojazdow}\n");
            if (string.IsNullOrWhiteSpace(MiastoMagazynu) || string.IsNullOrWhiteSpace(KodPocztowyMagazynu))
            {
                ModelState.AddModelError("MiastoMagazynu", "Podaj miasto magazynu.");
                ModelState.AddModelError("KodPocztowyMagazynu", "Podaj kod pocztowy magazynu.");
                return Page();
            }
            for (int i = 0; i < PunktyDostaw.Count; i++)
            {
                if (string.IsNullOrWhiteSpace(PunktyDostaw[i].Miasto) || string.IsNullOrWhiteSpace(PunktyDostaw[i].KodPocztowy))
                {
                    ModelState.AddModelError($"PunktyDostaw[{i}].Miasto", "Podaj miasto punktu dostawy.");
                    ModelState.AddModelError($"PunktyDostaw[{i}].KodPocztowy", "Podaj kod pocztowy punktu dostawy.");
                    return Page();
                }
            }
            var dane = new DaneWejsciowe
            {
                UlicaMagazynu = UlicaMagazynu,
                NumerMagazynu = NumerMagazynu,
                MiastoMagazynu = MiastoMagazynu,
                KodPocztowyMagazynu = KodPocztowyMagazynu,
                LiczbaPojazdow = LiczbaPojazdow,
                PunktyDostaw = PunktyDostaw
            };
            string filePath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "dane_wejsciowe.csv");
            CsvExporter.ExportDaneWejsciowe(dane, filePath);
            LogProces("[START] Workflow po eksporcie do CSV");
            LogProces("Eksport danych do CSV: OK");

            // Zapisz status że proces się rozpoczął
            var statusPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "processing_status.txt");
            System.IO.File.WriteAllText(statusPath, "🚀 Rozpoczynanie przetwarzania - przygotowywanie danych...");

            // Uruchom przetwarzanie w tle
            _ = Task.Run(() => ExecuteWorkflowInBackground());
            
            StatusMessage = "Rozpoczęto przetwarzanie danych...";
            return Page();
        }

        private async Task ExecuteWorkflowInBackground()
        {
            var statusPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "processing_status.txt");
            
            try
            {
                // ETAP 1: GEOKODOWANIE
                System.IO.File.WriteAllText(statusPath, "🌍 Geokodowanie adresów - konwersja na współrzędne GPS...");
                var success1 = await ExecuteGeocodingAsync();
                if (!success1) return;

                // ETAP 2: POBIERANIE CZASÓW
                System.IO.File.WriteAllText(statusPath, "✅ Geokodowanie ukończone! 🚗 Pobieranie czasów przejazdu z API...");
                var success2 = await ExecuteRoutingAsync();
                if (!success2) return;

                // ETAP 3: SCENARIUSZE
                System.IO.File.WriteAllText(statusPath, "✅ Pobieranie czasów ukończone! ⚡ Generowanie scenariuszy czasowych...");
                var success3 = await ExecuteScenariosAsync();
                if (!success3) return;

                // KONIEC
                System.IO.File.WriteAllText(statusPath, "COMPLETED:🎉 Wszystkie etapy zakończone pomyślnie! Dane gotowe do pobrania.");
                LogProces("[END] Workflow zakończony");
            }
            catch (Exception ex)
            {
                System.IO.File.WriteAllText(statusPath, $"ERROR:Błąd podczas przetwarzania: {ex.Message}");
                LogProces($"[ERROR] Workflow błąd: {ex.Message}");
            }
        }

        private async Task<bool> ExecuteGeocodingAsync()
        {
            var psiGeo = new System.Diagnostics.ProcessStartInfo
            {
                FileName = "python",
                Arguments = "PythonScripts/geocode.py",
                WorkingDirectory = Directory.GetCurrentDirectory(),
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            try
            {
                using var processGeo = System.Diagnostics.Process.Start(psiGeo);
                if (processGeo != null)
                {
                    await processGeo.WaitForExitAsync();
                    string errorMessage = GetErrorMessage(processGeo.ExitCode, "Geokodowanie");
                    if (processGeo.ExitCode == 0)
                    {
                        LogProces("Geokodowanie: OK");
                        return true;
                    }
                    else
                    {
                        LogProces(errorMessage);
                        var statusPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "processing_status.txt");
                        System.IO.File.WriteAllText(statusPath, $"ERROR:{errorMessage}");
                        return false;
                    }
                }
                return false;
            }
            catch (Exception ex)
            {
                LogProces($"Geokodowanie: BŁĄD uruchamiania skryptu: {ex.Message}");
                var statusPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "processing_status.txt");
                System.IO.File.WriteAllText(statusPath, $"ERROR:Błąd geokodowania: {ex.Message}");
                return false;
            }
        }

        private async Task<bool> ExecuteRoutingAsync()
        {
            var psiTimes = new System.Diagnostics.ProcessStartInfo
            {
                FileName = "python",
                Arguments = "PythonScripts/route_times.py",
                WorkingDirectory = Directory.GetCurrentDirectory(),
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            
            try
            {
                using var processTimes = System.Diagnostics.Process.Start(psiTimes);
                if (processTimes != null)
                {
                    await processTimes.WaitForExitAsync();
                    string errorMessage = GetErrorMessage(processTimes.ExitCode, "Pobieranie czasów");
                    if (processTimes.ExitCode == 0)
                    {
                        LogProces("Czasy przejazdu: OK");
                        return true;
                    }
                    else
                    {
                        LogProces(errorMessage);
                        var statusPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "processing_status.txt");
                        System.IO.File.WriteAllText(statusPath, $"ERROR:{errorMessage}");
                        return false;
                    }
                }
                return false;
            }
            catch (Exception ex)
            {
                LogProces($"Czasy przejazdu: BŁĄD uruchamiania skryptu: {ex.Message}");
                var statusPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "processing_status.txt");
                System.IO.File.WriteAllText(statusPath, $"ERROR:Błąd pobierania czasów: {ex.Message}");
                return false;
            }
        }

        private async Task<bool> ExecuteScenariosAsync()
        {
            var psiScen = new System.Diagnostics.ProcessStartInfo
            {
                FileName = "python",
                Arguments = "PythonScripts/czasy_przejazdu_perturb.py",
                WorkingDirectory = Directory.GetCurrentDirectory(),
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            
            try
            {
                using var processScen = System.Diagnostics.Process.Start(psiScen);
                if (processScen != null)
                {
                    await processScen.WaitForExitAsync();
                    string errorMessage = GetErrorMessage(processScen.ExitCode, "Scenariusze czasowe");
                    if (processScen.ExitCode == 0)
                    {
                        LogProces("Scenariusze czasowe: OK");
                        return true;
                    }
                    else
                    {
                        LogProces(errorMessage);
                        var statusPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "processing_status.txt");
                        System.IO.File.WriteAllText(statusPath, $"ERROR:{errorMessage}");
                        return false;
                    }
                }
                return false;
            }
            catch (Exception ex)
            {
                LogProces($"Scenariusze czasowe: BŁĄD uruchamiania skryptu: {ex.Message}");
                var statusPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "processing_status.txt");
                System.IO.File.WriteAllText(statusPath, $"ERROR:Błąd scenariuszy: {ex.Message}");
                return false;
            }
        }

        public IActionResult OnGetProcessingStatus()
        {
            var statusPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "processing_status.txt");
            if (System.IO.File.Exists(statusPath))
            {
                var status = System.IO.File.ReadAllText(statusPath);
                return new JsonResult(new { status = status });
            }
            return new JsonResult(new { status = "Brak informacji o statusie" });
        }

        private void LogProces(string msg)
        {
            string logPath = Path.Combine(Directory.GetCurrentDirectory(), "Logs", "log_aplikacja.txt");
            System.IO.File.AppendAllText(logPath, $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] {msg}\n");
        }





        public IActionResult OnPostLoadSample()
        {
            var samplePath = Path.Combine(Directory.GetCurrentDirectory(), "PlanyInstrukcje", "trasy_przykladowe.csv");
            if (!System.IO.File.Exists(samplePath))
            {
                StatusMessage = "Brak pliku z przykładową trasą.";
                return Page();
            }
            var lines = System.IO.File.ReadAllLines(samplePath);
            UlicaMagazynu = "";
            NumerMagazynu = "";
            MiastoMagazynu = "";
            KodPocztowyMagazynu = "";
            LiczbaPojazdow = 1;
            PunktyDostaw = new List<PunktDostawy>();
            foreach (var line in lines.Skip(1))
            {
                var parts = line.Split(',');
                if (parts[0] == "Magazyn")
                {
                    UlicaMagazynu = parts[1];
                    NumerMagazynu = parts[2];
                    MiastoMagazynu = parts[3];
                    KodPocztowyMagazynu = parts[4];
                }
                else if (parts[0] == "PunktDostawy")
                {
                    PunktyDostaw.Add(new PunktDostawy
                    {
                        Ulica = parts[1],
                        Numer = parts[2],
                        Miasto = parts[3],
                        KodPocztowy = parts[4],
                        OknoCzasoweOd = parts[5],
                        OknoCzasoweDo = parts[6]
                    });
                }
            }
            
            // Sprawdź czy dane magazynu zostały wczytane
            if (string.IsNullOrWhiteSpace(MiastoMagazynu) || string.IsNullOrWhiteSpace(KodPocztowyMagazynu))
            {
                StatusMessage = $"Błąd: Plik {WybranaTrasa} nie zawiera kompletnych danych magazynu. Sprawdź czy plik ma poprawny format.";
                return Page();
            }
            
            StatusMessage = "Wczytano przykładową trasę.";
            return Page();
        }
    }
}


