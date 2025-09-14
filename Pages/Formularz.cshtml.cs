using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.RazorPages;
using OptymalizacjaTras.Models;
using OptymalizacjaTras.Services;

namespace OptymalizacjaTras.Pages
{
    public class FormularzModel : PageModel
    {
        private readonly IProcessingService _processingService;
        private readonly IStatusService _statusService;
        private readonly ILogger<FormularzModel> _logger;

        public FormularzModel(IProcessingService processingService, IStatusService statusService, ILogger<FormularzModel> logger)
        {
            _processingService = processingService;
            _statusService = statusService;
            _logger = logger;
        }

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
            // Walidacja danych
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

            // Utworzenie obiektu danych
            var dane = new DaneWejsciowe
            {
                UlicaMagazynu = UlicaMagazynu,
                NumerMagazynu = NumerMagazynu,
                MiastoMagazynu = MiastoMagazynu,
                KodPocztowyMagazynu = KodPocztowyMagazynu,
                LiczbaPojazdow = LiczbaPojazdow,
                PunktyDostaw = PunktyDostaw
            };

            _logger.LogInformation("[START] Workflow po eksporcie do CSV");

            // Uruchom przetwarzanie w tle
            _ = Task.Run(async () => await _processingService.ExecuteWorkflowAsync(dane));
            
            StatusMessage = "Rozpoczęto przetwarzanie danych...";
            return Page();
        }

        public async Task<IActionResult> OnGetProcessingStatus()
        {
            var status = await _statusService.GetCurrentStatusAsync();
            if (string.IsNullOrEmpty(status))
            {
                status = "Brak informacji o statusie";
            }
            return new JsonResult(new { status = status });
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


