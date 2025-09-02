namespace OptymalizacjaTras.Models;
public class PunktDostawy
{
    public string? Ulica { get; set; }
    public string? Numer { get; set; }
    public string? Miasto { get; set; }
    public string? KodPocztowy { get; set; }
    public string? OknoCzasoweOd { get; set; }
    public string? OknoCzasoweDo { get; set; }
}

public class DaneWejsciowe
{
    public string? UlicaMagazynu { get; set; }
    public string? NumerMagazynu { get; set; }
    public string? MiastoMagazynu { get; set; }
    public string? KodPocztowyMagazynu { get; set; }
    public int LiczbaPojazdow { get; set; }
    public List<PunktDostawy> PunktyDostaw { get; set; } = new();
}