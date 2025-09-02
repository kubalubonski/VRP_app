using Microsoft.AspNetCore.Mvc.RazorPages;

namespace OptymalizacjaTras.Pages
{
    public class WynikModel : PageModel
    {
        public int LiczbaPojazdow { get; set; }
        public int LiczbaPunktow { get; set; }
        public string DataGenerowania { get; set; } = "";

        public void OnGet()
        {
            var configPath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "config.csv");
            if (System.IO.File.Exists(configPath))
            {
                var line = System.IO.File.ReadAllLines(configPath).FirstOrDefault();
                if (!string.IsNullOrWhiteSpace(line) && line.StartsWith("LiczbaPojazdow"))
                {
                    var parts = line.Split(',');
                    if (parts.Length > 1 && int.TryParse(parts[1], out int pojazdy))
                        LiczbaPojazdow = pojazdy;
                }
            }
            var danePath = Path.Combine(Directory.GetCurrentDirectory(), "wwwroot", "dane_wejsciowe.csv");
            if (System.IO.File.Exists(danePath))
            {
                var lines = System.IO.File.ReadAllLines(danePath);
                LiczbaPunktow = lines.Count(l => l.StartsWith("PunktDostawy"));
            }
            DataGenerowania = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
        }
    }
}
