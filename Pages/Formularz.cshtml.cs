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
                string outputGeo = processGeo != null ? processGeo.StandardOutput.ReadToEnd() : "";
                string errorGeo = processGeo != null ? processGeo.StandardError.ReadToEnd() : "Process null";
                if (processGeo != null)
                {
                    processGeo.WaitForExit();
                    if (processGeo.ExitCode == 0)
                        LogProces("Geokodowanie: OK");
                    else
                        LogProces($"Geokodowanie: BŁĄD: {errorGeo}");
                }
                else
                {
                    LogProces("Geokodowanie: BŁĄD uruchamiania procesu");
                }
            }
            catch (Exception ex)
            {
                LogProces($"Geokodowanie: BŁĄD uruchamiania skryptu: {ex.Message}");
            }
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
                string outputTimes = processTimes != null ? processTimes.StandardOutput.ReadToEnd() : "";
                string errorTimes = processTimes != null ? processTimes.StandardError.ReadToEnd() : "Process null";
                if (processTimes != null)
                {
                    processTimes.WaitForExit();
                    if (processTimes.ExitCode == 0)
                        LogProces("Czasy przejazdu: OK");
                    else
                        LogProces($"Czasy przejazdu: BŁĄD: {errorTimes}");
                }
                else
                {
                    LogProces("Czasy przejazdu: BŁĄD uruchamiania procesu");
                }
            }
            catch (Exception ex)
            {
                LogProces($"Czasy przejazdu: BŁĄD uruchamiania skryptu: {ex.Message}");
            }
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
                string outputScen = processScen != null ? processScen.StandardOutput.ReadToEnd() : "";
                string errorScen = processScen != null ? processScen.StandardError.ReadToEnd() : "Process null";
                if (processScen != null)
                {
                    processScen.WaitForExit();
                    if (processScen.ExitCode == 0)
                        LogProces("Scenariusze czasowe: OK");
                    else
                        LogProces($"Scenariusze czasowe: BŁĄD: {errorScen}");
                }
                else
                {
                    LogProces("Scenariusze czasowe: BŁĄD uruchamiania procesu");
                }
            }
            catch (Exception ex)
            {
                LogProces($"Scenariusze czasowe: BŁĄD uruchamiania skryptu: {ex.Message}");
            }
            LogProces("[END] Workflow zakończony");
            return RedirectToPage("/Wynik");
        }

        private void LogProces(string msg)
        {
            string logPath = Path.Combine(Directory.GetCurrentDirectory(), "Logs", "log_aplikacja.txt");
            System.IO.File.AppendAllText(logPath, $"[{DateTime.Now:yyyy-MM-dd HH:mm:ss}] {msg}\n");
        }

        public IActionResult OnPostGeocode()
        {
            StatusMessage = "Geokodowanie w toku...";
            ModelState.Clear();
            var psi = new System.Diagnostics.ProcessStartInfo
            {
                FileName = "python",
                Arguments = "geocode.py",
                WorkingDirectory = Directory.GetCurrentDirectory(),
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            try
            {
                using var process = System.Diagnostics.Process.Start(psi);
                string output = process != null ? process.StandardOutput.ReadToEnd() : "";
                string error = process != null ? process.StandardError.ReadToEnd() : "Process null";
                if (process != null)
                {
                    process.WaitForExit();
                    if (process.ExitCode == 0)
                        StatusMessage = "Geokodowanie zakończone.";
                    else
                        StatusMessage = $"Błąd geokodowania: {error}";
                }
                else
                {
                    StatusMessage = "Błąd uruchamiania procesu geokodowania.";
                }
            }
            catch (Exception ex)
            {
                StatusMessage = $"Błąd uruchamiania skryptu: {ex.Message}";
            }
            return Page();
        }

        public IActionResult OnPostRouteTimes()
        {
            try
            {
                var psi = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = "route_times.py",
                    WorkingDirectory = Directory.GetCurrentDirectory(),
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };
                using var process = System.Diagnostics.Process.Start(psi);
                string output = process != null ? process.StandardOutput.ReadToEnd() : "";
                string error = process != null ? process.StandardError.ReadToEnd() : "Process null";
                if (process != null)
                {
                    process.WaitForExit();
                    if (process.ExitCode == 0)
                        StatusMessage = "Czasy przejazdu pobrane.";
                    else
                        StatusMessage = $"Błąd pobierania czasów: {error}";
                }
                else
                {
                    StatusMessage = "Błąd uruchamiania procesu pobierania czasów.";
                }
            }
            catch (Exception ex)
            {
                StatusMessage = $"Błąd uruchamiania skryptu: {ex.Message}";
            }
            return Page();
        }

        public IActionResult OnPostScenarios()
        {
            try
            {
                var psi = new System.Diagnostics.ProcessStartInfo
                {
                    FileName = "python",
                    Arguments = "czasy_przejazdu_perturb.py",
                    WorkingDirectory = Directory.GetCurrentDirectory(),
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true
                };
                using var process = System.Diagnostics.Process.Start(psi);
                string output = process != null ? process.StandardOutput.ReadToEnd() : "";
                string error = process != null ? process.StandardError.ReadToEnd() : "Process null";
                if (process != null)
                {
                    process.WaitForExit();
                    if (process.ExitCode == 0)
                        StatusMessage = "Scenariusze czasowe wygenerowane.";
                    else
                        StatusMessage = $"Błąd generowania scenariuszy: {error}";
                }
                else
                {
                    StatusMessage = "Błąd uruchamiania procesu generowania scenariuszy.";
                }
            }
            catch (Exception ex)
            {
                StatusMessage = $"Błąd uruchamiania skryptu: {ex.Message}";
            }
            return Page();
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
            // Ustaw wartości nawet jeśli są puste
            if (string.IsNullOrWhiteSpace(UlicaMagazynu)) UlicaMagazynu = "Aleje Jerozolimskie";
            if (string.IsNullOrWhiteSpace(NumerMagazynu)) NumerMagazynu = "179";
            if (string.IsNullOrWhiteSpace(MiastoMagazynu)) MiastoMagazynu = "Warszawa";
            if (string.IsNullOrWhiteSpace(KodPocztowyMagazynu)) KodPocztowyMagazynu = "02-222";
            if (LiczbaPojazdow < 1) LiczbaPojazdow = 1;
            StatusMessage = "Wczytano przykładową trasę.";
            return Page();
        }
    }
}


